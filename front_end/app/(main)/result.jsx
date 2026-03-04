import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Animated } from 'react-native';
import { useRouter } from 'expo-router';
import Colors from '../../constants/Colors';
import { useStore } from '../../store/useStore';
import AnimatedGauge from '../../components/AnimatedGauge';

export default function ResultScreen() {
    const router = useRouter ? useRouter() : null;
    const { language, currentAssessment } = useStore();

    // Guard: no assessment yet (navigated directly to result page)
    if (!currentAssessment) {
        return (
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32, backgroundColor: '#F4F6F8' }}>
                <Text style={{ fontSize: 48, marginBottom: 16 }}>🩺</Text>
                <Text style={{ fontSize: 20, fontWeight: 'bold', color: '#1B4F72', marginBottom: 8, textAlign: 'center' }}>
                    No Assessment Yet
                </Text>
                <Text style={{ fontSize: 15, color: '#7f8c8d', textAlign: 'center', marginBottom: 24 }}>
                    Please go back and enter your symptoms first.
                </Text>
                <TouchableOpacity
                    style={{ backgroundColor: '#1B4F72', paddingHorizontal: 28, paddingVertical: 14, borderRadius: 12 }}
                    onPress={() => router?.replace('/(main)/symptom-input')}
                >
                    <Text style={{ color: '#fff', fontWeight: '700', fontSize: 16 }}>Enter Symptoms →</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const { score, tier, explanation } = currentAssessment;

    // System fonts used — Indic scripts render with device fonts

    // Pulse animation for the tier badge
    const pulseOpacity = useRef(new Animated.Value(0.4)).current;

    useEffect(() => {
        Animated.loop(
            Animated.sequence([
                Animated.timing(pulseOpacity, {
                    toValue: 1,
                    duration: 800,
                    useNativeDriver: true,
                }),
                Animated.timing(pulseOpacity, {
                    toValue: 0.4,
                    duration: 800,
                    useNativeDriver: true,
                })
            ])
        ).start();
    }, [pulseOpacity]);

    const getTierColor = (t) => {
        switch (t) {
            case 'low': return Colors.low;
            case 'moderate': return Colors.moderate;
            case 'high': return Colors.high;
            case 'critical': return Colors.critical;
            default: return Colors.primary;
        }
    };

    // Use system font — device handles Devanagari/Telugu rendering
    const getFontFamily = () => undefined;

    const currentStrings = explanation[language] || explanation['en'];
    const activeColor = getTierColor(tier);
    const fontFamily = getFontFamily();

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>

            {/* Animated Gauge */}
            <View style={styles.gaugeSection}>
                <AnimatedGauge score={score} tier={tier} />

                {/* Tier Badge */}
                <Animated.View style={[styles.badge, {
                    borderColor: activeColor,
                    backgroundColor: activeColor + '15',
                    opacity: pulseOpacity,
                }]}>
                    <Text style={[styles.badgeText, { color: activeColor }]}>
                        {tier.toUpperCase()} RISK
                    </Text>
                </Animated.View>
            </View>

            {/* Flashing Emergency Banner if critical */}
            {tier === 'critical' && (
                <Animated.View style={[styles.emergencyBanner, { opacity: pulseOpacity }]}>
                    <Text style={styles.emergencyText}>⚠️ EMERGENCY — CALL 108 NOW</Text>
                </Animated.View>
            )}

            {/* Explanation Cards */}
            <View style={styles.card}>
                <Text style={styles.cardHeader}>Why this score?</Text>
                {(currentStrings?.why || []).map((point, index) => (
                    <View key={index} style={styles.bulletRow}>
                        <Text style={[styles.bulletPoint, { color: activeColor }]}>•</Text>
                        <Text style={[styles.cardText, { fontFamily }]}>{point}</Text>
                    </View>
                ))}
            </View>

            <View style={styles.card}>
                <Text style={styles.cardHeader}>What does this mean?</Text>
                <Text style={[styles.cardText, { fontFamily }]}>{currentStrings?.meaning || 'No meaning provided.'}</Text>
            </View>

            <View style={[styles.card, { borderLeftColor: activeColor, borderLeftWidth: 4 }]}>
                <Text style={styles.cardHeader}>What to do now?</Text>
                <Text style={[styles.highlightText, { fontFamily }]}>{currentStrings?.whatToDo || 'No recommendation provided.'}</Text>
            </View>

            {/* CTA Buttons */}
            <View style={styles.actionContainer}>
                <TouchableOpacity
                    style={[styles.primaryButton, { backgroundColor: activeColor }]}
                    onPress={() => router?.push('/(main)/recommendation')}
                >
                    <Text style={styles.primaryButtonText}>See Recommendation</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.secondaryButton, { borderColor: activeColor }]}
                    onPress={() => router?.push('/(main)/report')}
                >
                    <Text style={[styles.secondaryButtonText, { color: activeColor }]}>Download Report</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.tertiaryButton}
                    onPress={() => router?.replace('/(main)/symptom-input')}
                >
                    <Text style={styles.tertiaryButtonText}>Start New Screening</Text>
                </TouchableOpacity>
            </View>

        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
    },
    content: {
        padding: 20,
        paddingBottom: 40,
    },
    gaugeSection: {
        alignItems: 'center',
        marginBottom: 32,
    },
    badge: {
        marginTop: 24,
        paddingHorizontal: 24,
        paddingVertical: 8,
        borderRadius: 20,
        borderWidth: 2,
    },
    badgeText: {
        fontSize: 16,
        fontWeight: '800',
        letterSpacing: 1,
    },
    emergencyBanner: {
        backgroundColor: Colors.critical,
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 24,
    },
    emergencyText: {
        color: Colors.white,
        fontWeight: 'bold',
        fontSize: 16,
    },
    card: {
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 20,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 8,
        elevation: 2,
    },
    cardHeader: {
        fontSize: 18,
        fontWeight: 'bold',
        color: Colors.textPrimary,
        marginBottom: 12,
    },
    bulletRow: {
        flexDirection: 'row',
        marginBottom: 8,
        alignItems: 'flex-start',
    },
    bulletPoint: {
        fontSize: 18,
        fontWeight: 'bold',
        marginRight: 8,
        lineHeight: 22,
    },
    cardText: {
        fontSize: 15,
        lineHeight: 24,
        color: Colors.textSecondary,
        flex: 1,
    },
    highlightText: {
        fontSize: 16,
        fontWeight: '700',
        lineHeight: 24,
        color: Colors.textPrimary,
    },
    actionContainer: {
        marginTop: 16,
        gap: 12,
    },
    primaryButton: {
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    primaryButtonText: {
        color: Colors.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
    secondaryButton: {
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
        borderWidth: 1,
        backgroundColor: 'transparent',
    },
    secondaryButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    tertiaryButton: {
        padding: 16,
        alignItems: 'center',
    },
    tertiaryButtonText: {
        color: Colors.textSecondary,
        fontSize: 16,
        fontWeight: '600',
    },
});
