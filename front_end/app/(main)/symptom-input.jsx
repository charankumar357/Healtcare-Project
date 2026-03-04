import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Colors from '../../constants/Colors';
import VoiceInput from '../../components/VoiceInput';

export default function SymptomInputScreen() {
    const [activeTab, setActiveTab] = useState('Voice'); // Defaulting to Voice for testing

    const TABS = ['Text', 'Voice', 'Guided'];

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Enter Symptoms</Text>

            <View style={styles.tabBar}>
                {TABS.map((tab) => (
                    <TouchableOpacity
                        key={tab}
                        style={[styles.tab, activeTab === tab && styles.activeTab]}
                        onPress={() => setActiveTab(tab)}
                        activeOpacity={0.7}
                    >
                        <Text
                            style={[styles.tabText, activeTab === tab && styles.activeTabText]}
                        >
                            {tab}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>

            <View style={styles.contentArea}>
                {activeTab === 'Text' && (
                    <View style={styles.placeholderContainer}>
                        <Text style={styles.placeholder}>Text input mode coming soon...</Text>
                    </View>
                )}

                {activeTab === 'Voice' && <VoiceInput />}

                {activeTab === 'Guided' && (
                    <View style={styles.placeholderContainer}>
                        <Text style={styles.placeholder}>Guided questionnaire coming soon...</Text>
                    </View>
                )}
            </View>
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
    activeTab: {
        backgroundColor: Colors.primary,
    },
    tabText: {
        fontSize: 14,
        fontWeight: '600',
        color: Colors.textSecondary,
    },
    activeTabText: {
        color: Colors.white,
    },
    contentArea: {
        flex: 1,
    },
    placeholderContainer: {
        flex: 1,
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 20,
        justifyContent: 'center',
        alignItems: 'center',
    },
    placeholder: {
        color: Colors.disabled,
        fontSize: 14,
    },
});
