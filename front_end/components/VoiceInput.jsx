import React, { useState, useEffect, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    TextInput,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { transcribeAsync, initWhisper } from 'react-native-whisper';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withRepeat,
    withSequence,
    withTiming,
} from 'react-native-reanimated';
import axios from 'axios';
import Colors from '../constants/Colors';

const MAX_RECORDING_TIME = 60; // seconds
const MIN_RECORDING_TIME = 3; // seconds
// NOTE: For a real app, use environment variables. Hardcoding for placeholder.
const GROQ_API_KEY = 'YOUR_GROQ_API_KEY';

export default function VoiceInput() {
    const [hasPermission, setHasPermission] = useState(null);
    const [recording, setRecording] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [recordingDuration, setRecordingDuration] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [detectedLang, setDetectedLang] = useState(null);

    const timerRef = useRef(null);
    const scale = useSharedValue(1);

    // Auto-init Whisper
    useEffect(() => {
        (async () => {
            try {
                const { status } = await Audio.requestPermissionsAsync();
                setHasPermission(status === 'granted');

                // Ensure whisper is initialized
                // Note: the exact path/model depends on your project setup for RN Whisper.
                // Assuming small model is bundled or downloaded on first launch.
            } catch (e) {
                console.log("Permission/Init Error:", e);
            }
        })();
        return stopTimer;
    }, []);

    const animatedStyle = useAnimatedStyle(() => ({
        transform: [{ scale: scale.value }],
    }));

    const startTimer = () => {
        setRecordingDuration(0);
        timerRef.current = setInterval(() => {
            setRecordingDuration((prev) => {
                if (prev >= MAX_RECORDING_TIME - 1) {
                    stopRecording(); // Auto-stop at 60s
                    return MAX_RECORDING_TIME;
                }
                return prev + 1;
            });
        }, 1000);
    };

    const stopTimer = () => {
        if (timerRef.current) clearInterval(timerRef.current);
    };

    const startRecording = async () => {
        if (!hasPermission) {
            Alert.alert('Permission Denied', 'Please enable microphone access in settings.');
            return;
        }

        try {
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });

            console.log('Starting recording..');
            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            setRecording(recording);
            setIsRecording(true);

            // Animate mic button
            scale.value = withRepeat(
                withSequence(withTiming(1.2, { duration: 500 }), withTiming(1, { duration: 500 })),
                -1,
                true
            );

            startTimer();
        } catch (err) {
            console.error('Failed to start recording', err);
        }
    };

    const stopRecording = async () => {
        if (!recording) return;

        try {
            console.log('Stopping recording..');
            setIsRecording(false);
            stopTimer();
            scale.value = withSpring(1); // Reset animation

            await recording.stopAndUnloadAsync();
            await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

            const uri = recording.getURI();
            setRecording(null);

            if (recordingDuration < MIN_RECORDING_TIME) {
                Alert.alert('Too Short', 'Please record for at least 3 seconds.');
                return;
            }

            await processAudio(uri);
        } catch (error) {
            console.error("Stop Recording Error:", error);
        }
    };

    const processAudio = async (uri) => {
        setIsProcessing(true);
        setTranscript('');
        setDetectedLang(null);

        const docPath = FileSystem.documentDirectory + 'recording.wav';

        try {
            // Ensure file is accessible
            await FileSystem.copyAsync({ from: uri, to: docPath });

            // 1. Attempt on-device Whisper
            console.log('Starting on-device STT...');
            // Note: In a real app, you need to provide the actual initialized model context.
            // This uses a pseudo-implementation based on the spec request.
            let result = null;
            try {
                // mock transcribed async block for actual rn-whisper
                // result = await transcribeAsync(docPath, { language: 'auto' });
                // MOCK RESULT for testing logic:
                // result = { text: 'Mock STT output', language: 'en', confidence: 0.9 };
            } catch (e) {
                console.error('Whisper STT failed', e);
            }

            // 2. Logic: Fallback to Groq API if local STT fails or has low confidence
            const confidence = result?.confidence || 0; // Simulated
            if (!result || confidence < 0.75) {
                console.log('Local STT low confidence or failed. Falling back to Groq Whisper API...');
                const formData = new FormData();
                formData.append('file', {
                    uri: docPath,
                    name: 'recording.wav',
                    type: 'audio/wav',
                });
                formData.append('model', 'whisper-large-v3');

                const groqResponse = await axios.post(
                    'https://api.groq.com/openai/v1/audio/transcriptions',
                    formData,
                    {
                        headers: {
                            Authorization: `Bearer ${GROQ_API_KEY}`,
                            'Content-Type': 'multipart/form-data',
                        },
                    }
                );

                setTranscript(groqResponse.data.text);
                setDetectedLang(groqResponse.data.language || 'auto'); // Groq doesn't always return lang, so fallback
            } else {
                setTranscript(result.text);
                setDetectedLang(result.language);
            }
        } catch (error) {
            console.error('Processing error:', error);
            Alert.alert('Error', 'Failed to process audio. Switching to text input.');
        } finally {
            setIsProcessing(false);
        }
    };

    const reset = () => {
        setTranscript('');
        setDetectedLang(null);
        setRecordingDuration(0);
    };

    // UI RENDERS
    if (!hasPermission) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorText}>Microphone permission is required.</Text>
                <TouchableOpacity style={styles.button} onPress={() => Audio.requestPermissionsAsync()}>
                    <Text style={styles.buttonText}>Grant Permission</Text>
                </TouchableOpacity>
            </View>
        );
    }

    if (isProcessing) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color={Colors.primary} />
                <Text style={styles.loadingText}>Transcribing audio...</Text>
            </View>
        );
    }

    if (transcript) {
        return (
            <View style={styles.resultContainer}>
                {detectedLang && (
                    <View style={styles.badge}>
                        <Text style={styles.badgeText}>Detected language: {detectedLang}</Text>
                    </View>
                )}

                <TextInput
                    style={styles.textInput}
                    multiline
                    value={transcript}
                    onChangeText={setTranscript}
                    maxLength={1000}
                />

                <View style={styles.actionRow}>
                    <TouchableOpacity style={styles.outlineButton} onPress={reset}>
                        <Text style={styles.outlineButtonText}>Re-record</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.primaryButton}>
                        <Text style={styles.primaryButtonText}>Use This Text</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    return (
        <View style={styles.centerContainer}>
            <Text style={styles.timerText}>
                {Math.floor(recordingDuration / 60)}:{(recordingDuration % 60).toString().padStart(2, '0')}
            </Text>
            <Text style={styles.helpText}>
                {isRecording ? 'Release to stop' : 'Press and hold to record'}
            </Text>

            <TouchableOpacity
                onPressIn={startRecording}
                onPressOut={stopRecording}
                activeOpacity={0.8}
            >
                <Animated.View style={[styles.micButton, isRecording && styles.micButtonActive, animatedStyle]}>
                    <Text style={styles.micIcon}>🎤</Text>
                </Animated.View>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    resultContainer: {
        flex: 1,
        padding: 16,
    },
    micButton: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: Colors.primary,
        justifyContent: 'center',
        alignItems: 'center',
        elevation: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        marginVertical: 20,
    },
    micButtonActive: {
        backgroundColor: Colors.secondary, // Assuming secondary is a 'recording' state color
    },
    micIcon: {
        fontSize: 32,
    },
    timerText: {
        fontSize: 36,
        fontWeight: '300',
        color: Colors.textPrimary,
        marginBottom: 8,
    },
    helpText: {
        fontSize: 16,
        color: Colors.textSecondary,
        marginBottom: 24,
    },
    errorText: {
        color: Colors.critical,
        marginBottom: 16,
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: Colors.textSecondary,
    },
    textInput: {
        flex: 1,
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 16,
        fontSize: 16,
        color: Colors.textPrimary,
        textAlignVertical: 'top',
        borderWidth: 1,
        borderColor: Colors.border,
        marginBottom: 16,
    },
    badge: {
        alignSelf: 'flex-start',
        backgroundColor: Colors.primary + '15',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 16,
        marginBottom: 12,
    },
    badgeText: {
        fontSize: 12,
        fontWeight: '600',
        color: Colors.primary,
    },
    actionRow: {
        flexDirection: 'row',
        gap: 12,
    },
    outlineButton: {
        flex: 1,
        padding: 16,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: Colors.primary,
        alignItems: 'center',
    },
    outlineButtonText: {
        color: Colors.primary,
        fontSize: 16,
        fontWeight: 'bold',
    },
    primaryButton: {
        flex: 1,
        backgroundColor: Colors.primary,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    primaryButtonText: {
        color: Colors.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
    button: {
        backgroundColor: Colors.primary,
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 8,
    },
    buttonText: {
        color: Colors.white,
        fontWeight: 'bold',
    }
});
