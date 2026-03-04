import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import Colors from '../../constants/Colors';
import { useStore } from '../../store/useStore';

export default function HomeScreen() {
    const router = useRouter();
    const { logout } = useStore();

    const handleLogout = async () => {
        await logout();
        router.replace('/(auth)/login');
    };

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.greeting}>Hello 👋</Text>
                    <Text style={styles.subtitle}>How are you feeling today?</Text>
                </View>
                <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
                    <Text style={styles.logoutText}>Logout</Text>
                </TouchableOpacity>
            </View>

            {/* Start Screening Card */}
            <TouchableOpacity
                style={styles.screeningCard}
                onPress={() => router.push('/(main)/symptom-input')}
                activeOpacity={0.85}
            >
                <Text style={styles.screeningIcon}>🩺</Text>
                <Text style={styles.screeningTitle}>Start Health Screening</Text>
                <Text style={styles.screeningSubtitle}>
                    Describe your symptoms and get an AI-powered risk assessment instantly
                </Text>
                <View style={styles.startButton}>
                    <Text style={styles.startButtonText}>Begin Assessment →</Text>
                </View>
            </TouchableOpacity>

            {/* Quick Info Cards */}
            <Text style={styles.sectionTitle}>What you'll get</Text>
            <View style={styles.infoRow}>
                <View style={styles.infoCard}>
                    <Text style={styles.infoIcon}>📊</Text>
                    <Text style={styles.infoLabel}>Risk Score</Text>
                    <Text style={styles.infoDesc}>AI-powered health risk analysis</Text>
                </View>
                <View style={styles.infoCard}>
                    <Text style={styles.infoIcon}>💊</Text>
                    <Text style={styles.infoLabel}>Recommendation</Text>
                    <Text style={styles.infoDesc}>Personalised next steps</Text>
                </View>
            </View>
            <View style={styles.infoRow}>
                <View style={styles.infoCard}>
                    <Text style={styles.infoIcon}>📄</Text>
                    <Text style={styles.infoLabel}>PDF Report</Text>
                    <Text style={styles.infoDesc}>Download & share with doctor</Text>
                </View>
                <View style={styles.infoCard}>
                    <Text style={styles.infoIcon}>🏥</Text>
                    <Text style={styles.infoLabel}>Nearby Clinics</Text>
                    <Text style={styles.infoDesc}>Find PHC/hospital near you</Text>
                </View>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: Colors.background },
    content: { padding: 20, paddingBottom: 40 },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 28,
    },
    greeting: { fontSize: 26, fontWeight: 'bold', color: Colors.textPrimary },
    subtitle: { fontSize: 14, color: Colors.textSecondary, marginTop: 2 },
    logoutBtn: {
        paddingHorizontal: 14, paddingVertical: 7,
        borderRadius: 8, borderWidth: 1, borderColor: Colors.primary,
    },
    logoutText: { color: Colors.primary, fontWeight: '600', fontSize: 13 },
    screeningCard: {
        backgroundColor: Colors.primary,
        borderRadius: 20, padding: 28,
        marginBottom: 28, alignItems: 'center',
    },
    screeningIcon: { fontSize: 48, marginBottom: 12 },
    screeningTitle: {
        fontSize: 22, fontWeight: 'bold',
        color: Colors.white, marginBottom: 8, textAlign: 'center',
    },
    screeningSubtitle: {
        fontSize: 14, color: 'rgba(255,255,255,0.8)',
        textAlign: 'center', lineHeight: 22, marginBottom: 20,
    },
    startButton: {
        backgroundColor: Colors.white,
        paddingHorizontal: 24, paddingVertical: 12,
        borderRadius: 12,
    },
    startButtonText: { color: Colors.primary, fontWeight: '700', fontSize: 16 },
    sectionTitle: {
        fontSize: 18, fontWeight: '700',
        color: Colors.textPrimary, marginBottom: 14,
    },
    infoRow: { flexDirection: 'row', gap: 12, marginBottom: 12 },
    infoCard: {
        flex: 1, backgroundColor: Colors.white,
        borderRadius: 14, padding: 16, alignItems: 'center',
        shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05, shadowRadius: 8, elevation: 2,
    },
    infoIcon: { fontSize: 28, marginBottom: 8 },
    infoLabel: { fontSize: 13, fontWeight: '700', color: Colors.textPrimary, marginBottom: 4 },
    infoDesc: { fontSize: 11, color: Colors.textSecondary, textAlign: 'center' },
});
