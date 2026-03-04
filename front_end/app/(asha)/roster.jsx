import { View, Text, StyleSheet } from 'react-native';
import Colors from '../../constants/Colors';

export default function RosterScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>My Patients</Text>

            <View style={styles.searchBar}>
                <Text style={styles.searchText}>🔍 Search assigned patients...</Text>
            </View>

            {/* Placeholder list */}
            {[1, 2, 3].map((item) => (
                <View key={item} style={styles.patientCard}>
                    <View style={styles.avatar}>
                        <Text style={styles.avatarText}>RP</Text>
                    </View>
                    <View style={styles.info}>
                        <Text style={styles.name}>Ramesh Patel</Text>
                        <Text style={styles.details}>Age: 45 • Last Visit: 2 weeks ago</Text>
                    </View>
                </View>
            ))}

            {/* TODO: Add FAB to add new patient */}
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
    searchBar: {
        backgroundColor: Colors.white,
        borderRadius: 10,
        padding: 12,
        marginBottom: 20,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    searchText: {
        color: Colors.disabled,
    },
    patientCard: {
        flexDirection: 'row',
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 4,
        elevation: 2,
    },
    avatar: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: Colors.primary + '20',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 16,
    },
    avatarText: {
        color: Colors.primary,
        fontWeight: 'bold',
        fontSize: 16,
    },
    info: {
        flex: 1,
    },
    name: {
        fontSize: 16,
        fontWeight: '600',
        color: Colors.textPrimary,
        marginBottom: 4,
    },
    details: {
        fontSize: 13,
        color: Colors.textSecondary,
    },
});
