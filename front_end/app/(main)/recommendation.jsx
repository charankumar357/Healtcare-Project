import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Colors from '../../constants/Colors';

export default function RecommendationScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Recommended Actions</Text>

            <View style={styles.card}>
                <Text style={styles.cardTitle}>Immediate Step</Text>
                <Text style={styles.cardText}>
                    Schedule a teleconsultation with a doctor within 24 hours.
                </Text>
            </View>

            <View style={styles.card}>
                <Text style={styles.cardTitle}>Home Care</Text>
                <Text style={styles.cardText}>
                    Ensure the patient stays hydrated and rests. Monitor temperature every 4 hours.
                </Text>
            </View>

            <View style={styles.buttonContainer}>
                <TouchableOpacity style={styles.primaryButton}>
                    <Text style={styles.buttonText}>Generate Report</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.secondaryButton}>
                    <Text style={styles.secondaryButtonText}>Return to Home</Text>
                </TouchableOpacity>
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
        marginBottom: 20,
    },
    card: {
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 20,
        marginBottom: 16,
        borderLeftWidth: 4,
        borderLeftColor: Colors.secondary,
    },
    cardTitle: {
        fontSize: 16,
        fontWeight: '700',
        color: Colors.textPrimary,
        marginBottom: 8,
    },
    cardText: {
        fontSize: 14,
        color: Colors.textSecondary,
        lineHeight: 20,
    },
    buttonContainer: {
        marginTop: 'auto',
        gap: 12,
    },
    primaryButton: {
        backgroundColor: Colors.primary,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    buttonText: {
        color: Colors.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
    secondaryButton: {
        backgroundColor: 'transparent',
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: Colors.primary,
    },
    secondaryButtonText: {
        color: Colors.primary,
        fontSize: 16,
        fontWeight: 'bold',
    },
});
