import React, { useState, useRef } from 'react';
import {
    View, Text, StyleSheet, TouchableOpacity,
    TextInput, ActivityIndicator, Alert,
} from 'react-native';
import { Audio } from 'expo-av';
import Animated, {
    useSharedValue, useAnimatedStyle,
    withRepeat, withSequence, withTiming, withSpring,
} from 'react-native-reanimated';
import Colors from '../constants/Colors';
import { transcribeAudio } from '../services/api';

const MAX_RECORDING_TIME = 60; // seconds
const MIN_RECORDING_TIME = 3;  // seconds

/**
 * VoiceInput component
 * Records audio via expo-av, sends to backend /audio/transcribe (Groq Whisper),
 * returns transcribed text via onTranscribed callback.
 *
 * @param {function} onTranscribed - called with the transcript string when done
 */
export default function VoiceInput({ onTranscribed }) {
    const [hasPermission, setHasPermission] = useState(null);
    const [recording, setRecording] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [recordingDuration, setRecordingDuration] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [detectedLang, setDetectedLang] = useState(null);

    const timerRef = useRef(null);
    const scale = useSharedValue(1);

    // Request mic permission on mount
    React.useEffect(() => {
        (async () => {
            const { status } = await Audio.requestPermissionsAsync();
            setHasPermission(status === 'granted');
        })();
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, []);

    const animatedStyle = useAnimatedStyle(() => ({
        transform: [{ scale: scale.value }],
    }));

    const startTimer = () => {
        setRecordingDuration(0);
        timerRef.current = setInterval(() => {
            setRecordingDuration((prev) => {
                if (prev >= MAX_RECORDING_TIME - 1) {
                    stopRecording();
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
            await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            setRecording(recording);
            setIsRecording(true);
            scale.value = withRepeat(
                withSequence(withTiming(1.2, { duration: 500 }), withTiming(1, { duration: 500 })),
                -1, true
            );
            startTimer();
        } catch (err) {
            console.error('Failed to start recording', err);
        }
    };

    const stopRecording = async () => {
        if (!recording) return;
        try {
            setIsRecording(false);
            stopTimer();
            scale.value = withSpring(1);

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
            console.error('Stop Recording Error:', error);
        }
    };

    // Send audio to backend /audio/transcribe (Groq Whisper)
    const processAudio = async (uri) => {
        setIsProcessing(true);
        setTranscript('');
        setDetectedLang(null);
        try {
            const result = await transcribeAudio({
                uri,
                name: 'recording.m4a',
                type: 'audio/m4a',
            });
            setTranscript(result.text || '');
            setDetectedLang(result.language || null);
        } catch (error) {
            console.error('Transcription error:', error);
            Alert.alert('Error', 'Failed to transcribe audio. Please type your symptoms instead.');
        } finally {
            setIsProcessing(false);
        }
    };

    const reset = () => {
        setTranscript('');
        setDetectedLang(null);
        setRecordingDuration(0);
    };

    const handleUseText = () => {
        if (onTranscribed && transcript) onTranscribed(transcript);
    };

    // ── Permission denied ──
    if (hasPermission === false) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorText}>Microphone permission is required.</Text>
                <TouchableOpacity style={styles.button} onPress={() => Audio.requestPermissionsAsync()}>
                    <Text style={styles.buttonText}>Grant Permission</Text>
                </TouchableOpacity>
            </View>
        );
    }

    // ── Processing ──
    if (isProcessing) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color={Colors.primary} />
                <Text style={styles.loadingText}>Transcribing audio...</Text>
            </View>
        );
    }

    // ── Transcript ready ──
    if (transcript) {
        return (
            <View style={styles.resultContainer}>
                {detectedLang && (
                    <View style={styles.badge}>
                        <Text style={styles.badgeText}>Detected: {detectedLang}</Text>
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
                    <TouchableOpacity style={styles.primaryButton} onPress={handleUseText}>
                        <Text style={styles.primaryButtonText}>Use This Text ✓</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    // ── Record UI ──
    return (
        <View style={styles.centerContainer}>
            <Text style={styles.timerText}>
                {Math.floor(recordingDuration / 60)}:{(recordingDuration % 60).toString().padStart(2, '0')}
            </Text>
            <Text style={styles.helpText}>
                {isRecording ? '🔴 Recording — release to stop' : 'Press and hold to record'}
            </Text>
            <TouchableOpacity onPressIn={startRecording} onPressOut={stopRecording} activeOpacity={0.8}>
                <Animated.View style={[styles.micButton, isRecording && styles.micButtonActive, animatedStyle]}>
                    <Text style={styles.micIcon}>🎤</Text>
                </Animated.View>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
    resultContainer: { flex: 1, padding: 16 },
    micButton: {
        width: 80, height: 80, borderRadius: 40,
        backgroundColor: Colors.primary,
        justifyContent: 'center', alignItems: 'center',
        elevation: 8, shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3, shadowRadius: 8, marginVertical: 20,
    },
    micButtonActive: { backgroundColor: '#e53e3e' },
    micIcon: { fontSize: 32 },
    timerText: { fontSize: 36, fontWeight: '300', color: Colors.textPrimary, marginBottom: 8 },
    helpText: { fontSize: 16, color: Colors.textSecondary, marginBottom: 24 },
    errorText: { color: '#e53e3e', marginBottom: 16 },
    loadingText: { marginTop: 16, fontSize: 16, color: Colors.textSecondary },
    textInput: {
        flex: 1, backgroundColor: Colors.white, borderRadius: 12,
        padding: 16, fontSize: 16, color: Colors.textPrimary,
        textAlignVertical: 'top', borderWidth: 1,
        borderColor: '#e2e8f0', marginBottom: 16,
    },
    badge: {
        alignSelf: 'flex-start', backgroundColor: Colors.primary + '20',
        paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, marginBottom: 12,
    },
    badgeText: { fontSize: 12, fontWeight: '600', color: Colors.primary },
    actionRow: { flexDirection: 'row', gap: 12 },
    outlineButton: {
        flex: 1, padding: 16, borderRadius: 12,
        borderWidth: 1, borderColor: Colors.primary, alignItems: 'center',
    },
    outlineButtonText: { color: Colors.primary, fontSize: 16, fontWeight: 'bold' },
    primaryButton: {
        flex: 1, backgroundColor: Colors.primary,
        padding: 16, borderRadius: 12, alignItems: 'center',
    },
    primaryButtonText: { color: Colors.white, fontSize: 16, fontWeight: 'bold' },
    button: { backgroundColor: Colors.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
    buttonText: { color: Colors.white, fontWeight: 'bold' },
});
