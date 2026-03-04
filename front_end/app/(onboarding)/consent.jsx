import { View, Text, StyleSheet } from 'react-native';
import Colors from '../../constants/Colors';

export default function ConsentScreen() {
    return (
        <View style={styles.container}>
            <View style={styles.card}>
                <Text style={styles.title}>Data Consent</Text>
                <Text style={styles.description}>
                    Your health data will be processed securely. We collect symptom information
                    to provide health risk assessments. Your data is encrypted and never shared
                    without your permission.
                </Text>

                <View style={styles.voiceButton}>
                    <Text style={styles.voiceIcon}>🔊</Text>
                    <Text style={styles.voiceText}>Listen to consent details</Text>
                </View>

                {/* TODO: Consent checkboxes + accept button */}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
        padding: 24,
        justifyContent: 'center',
    },
    card: {
        backgroundColor: Colors.white,
        borderRadius: 16,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.08,
        shadowRadius: 8,
        elevation: 3,
    },
    title: {
        fontSize: 22,
        fontWeight: 'bold',
        color: Colors.primary,
        marginBottom: 16,
        textAlign: 'center',
    },
    description: {
        fontSize: 14,
        lineHeight: 22,
        color: Colors.textSecondary,
        marginBottom: 20,
    },
    voiceButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: Colors.primary + '10',
        padding: 14,
        borderRadius: 10,
        gap: 10,
    },
    voiceIcon: {
        fontSize: 22,
    },
    voiceText: {
        fontSize: 14,
        fontWeight: '600',
        color: Colors.primary,
    },
});
