import { View, Text, StyleSheet } from 'react-native';
import Colors from '../../constants/Colors';

export default function BatchScreen() {
    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Batch Screening</Text>
                <View style={styles.badge}>
                    <Text style={styles.badgeText}>Offline Mode</Text>
                </View>
            </View>

            <View style={styles.card}>
                <Text style={styles.cardTitle}>Village Camp - Sector 4</Text>
                <Text style={styles.cardText}>14 assessments pending sync</Text>

                {/* Placeholder sync button */}
                <View style={styles.syncButton}>
                    <Text style={styles.syncText}>Sync Now</Text>
                </View>
            </View>

            {/* TODO: List of offline records waiting to be synced */}
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
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
    },
    title: {
        fontSize: 22,
        fontWeight: 'bold',
        color: Colors.textPrimary,
    },
    badge: {
        backgroundColor: Colors.moderate,
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 12,
    },
    badgeText: {
        color: Colors.white,
        fontSize: 12,
        fontWeight: 'bold',
    },
    card: {
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 20,
        borderLeftWidth: 4,
        borderLeftColor: Colors.moderate,
    },
    cardTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: Colors.textPrimary,
        marginBottom: 8,
    },
    cardText: {
        fontSize: 14,
        color: Colors.textSecondary,
        marginBottom: 16,
    },
    syncButton: {
        backgroundColor: Colors.primary + '10',
        padding: 12,
        borderRadius: 8,
        alignItems: 'center',
    },
    syncText: {
        color: Colors.primary,
        fontWeight: '600',
    },
});
