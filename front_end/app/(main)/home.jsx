import { View, Text, StyleSheet } from 'react-native';
import Colors from '../../constants/Colors';

export default function HomeScreen() {
    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.greeting}>Welcome back 👋</Text>
                <Text style={styles.role}>ASHA Health Worker</Text>
            </View>

            <View style={styles.actionCard}>
                <Text style={styles.actionTitle}>Start New Screening</Text>
                <Text style={styles.actionSubtitle}>
                    Begin a new health risk assessment
                </Text>
                {/* TODO: Start screening button */}
            </View>

            <Text style={styles.sectionTitle}>Recent Screenings</Text>
            <View style={styles.emptyState}>
                <Text style={styles.emptyText}>No recent screenings</Text>
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
    header: {
        marginBottom: 24,
    },
    greeting: {
        fontSize: 24,
        fontWeight: 'bold',
        color: Colors.textPrimary,
    },
    role: {
        fontSize: 14,
        color: Colors.textSecondary,
        marginTop: 4,
    },
    actionCard: {
        backgroundColor: Colors.primary,
        borderRadius: 16,
        padding: 24,
        marginBottom: 24,
    },
    actionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: Colors.white,
        marginBottom: 4,
    },
    actionSubtitle: {
        fontSize: 13,
        color: 'rgba(255,255,255,0.8)',
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '700',
        color: Colors.textPrimary,
        marginBottom: 12,
    },
    emptyState: {
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 32,
        alignItems: 'center',
    },
    emptyText: {
        color: Colors.textSecondary,
        fontSize: 14,
    },
});
