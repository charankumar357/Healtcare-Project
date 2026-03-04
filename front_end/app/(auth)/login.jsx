import { View, Text, StyleSheet } from 'react-native';
import Colors from '../../constants/Colors';

export default function LoginScreen() {
    return (
        <View style={styles.container}>
            <View style={styles.card}>
                <Text style={styles.title}>🏥 HealthBridge</Text>
                <Text style={styles.subtitle}>ASHA Worker Login</Text>
                <Text style={styles.description}>
                    Enter your mobile number to receive an OTP
                </Text>
                {/* TODO: OTP input fields + submit button */}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.primary,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    card: {
        backgroundColor: Colors.white,
        borderRadius: 16,
        padding: 32,
        width: '100%',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 8,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: Colors.primary,
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 18,
        fontWeight: '600',
        color: Colors.textSecondary,
        marginBottom: 16,
    },
    description: {
        fontSize: 14,
        color: Colors.textSecondary,
        textAlign: 'center',
    },
});
