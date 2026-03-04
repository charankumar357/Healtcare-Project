import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import Colors from '../../constants/Colors';
import VoiceInput from '../../components/VoiceInput';
import { useStore } from '../../store/useStore';

// Default demographics (ASHA worker fills these before submitting)
const DEFAULT_DEMOGRAPHICS = {
    age: 30,
    gender: 'female',
    comorbidities: [],
    pregnancy: false,
};

export default function SymptomInputScreen() {
    const router = useRouter();
    const { runScreening, isLoading, language } = useStore();

    const [activeTab, setActiveTab] = useState('Text');
    const [symptomText, setSymptomText] = useState('');

    const TABS = ['Text', 'Voice', 'Guided'];

    const handleSubmit = async () => {
        if (!symptomText.trim()) {
            Alert.alert('No Symptoms', 'Please describe the patient\'s symptoms first.');
            return;
        }
        try {
            await runScreening(symptomText, DEFAULT_DEMOGRAPHICS);
            router.push('/(main)/result');
        } catch (e) {
            Alert.alert('Error', e.message || 'Failed to analyse symptoms. Please try again.');
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Enter Symptoms</Text>

            {/* Tab bar */}
            <View style={styles.tabBar}>
                {TABS.map((tab) => (
                    <TouchableOpacity
                        key={tab}
                        style={[styles.tab, activeTab === tab && styles.activeTab]}
                        onPress={() => setActiveTab(tab)}
                        activeOpacity={0.7}
                    >
                        <Text style={[styles.tabText, activeTab === tab && styles.activeTabText]}>
                            {tab}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>

            {/* Content area */}
            <View style={styles.contentArea}>
                {activeTab === 'Text' && (
                    <TextInput
                        style={styles.textInput}
                        placeholder={
                            language === 'hi' ? 'यहाँ लक्षण लिखें...'
                                : language === 'te' ? 'ఇక్కడ లక్షణాలు రాయండి...'
                                    : 'Describe symptoms here (any language)...'
                        }
                        placeholderTextColor={Colors.disabled}
                        multiline
                        value={symptomText}
                        onChangeText={setSymptomText}
                        textAlignVertical="top"
                    />
                )}

                {activeTab === 'Voice' && (
                    <VoiceInput onTranscribed={(text) => {
                        setSymptomText(text);
                        setActiveTab('Text'); // switch to text tab to show result
                    }} />
                )}

                {activeTab === 'Guided' && (
                    <View style={styles.placeholderContainer}>
                        <Text style={styles.placeholder}>Guided questionnaire — coming soon</Text>
                    </View>
                )}
            </View>

            {/* Analyse Button */}
            <TouchableOpacity
                style={[styles.analyseButton, (isLoading || !symptomText.trim()) && styles.buttonDisabled]}
                onPress={handleSubmit}
                disabled={isLoading || !symptomText.trim()}
            >
                {isLoading
                    ? <ActivityIndicator color={Colors.white} />
                    : <Text style={styles.analyseButtonText}>🔍 Analyse Symptoms</Text>
                }
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
        padding: 20,
    },
    title: {
        fontSize: 22,
        fontWeight: 'bold',
        color: Colors.textPrimary,
        marginBottom: 16,
    },
    tabBar: {
        flexDirection: 'row',
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 4,
        marginBottom: 20,
    },
    tab: {
        flex: 1,
        paddingVertical: 10,
        alignItems: 'center',
        borderRadius: 10,
    },
    activeTab: { backgroundColor: Colors.primary },
    tabText: { fontSize: 14, fontWeight: '600', color: Colors.textSecondary },
    activeTabText: { color: Colors.white },
    contentArea: { flex: 1 },
    textInput: {
        flex: 1,
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 16,
        fontSize: 16,
        color: Colors.textPrimary,
        lineHeight: 24,
    },
    placeholderContainer: {
        flex: 1,
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 20,
        justifyContent: 'center',
        alignItems: 'center',
    },
    placeholder: { color: Colors.disabled, fontSize: 14 },
    analyseButton: {
        backgroundColor: Colors.primary,
        borderRadius: 12,
        paddingVertical: 16,
        alignItems: 'center',
        marginTop: 16,
    },
    buttonDisabled: { opacity: 0.5 },
    analyseButtonText: {
        color: Colors.white,
        fontSize: 17,
        fontWeight: '700',
    },
});
