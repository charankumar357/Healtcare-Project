import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import Colors from '../../constants/Colors';
import { useStore } from '../../store/useStore';

export default function LoginScreen() {
    const router = useRouter();
    const { login, isLoading } = useStore();

    const [phone, setPhone] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async () => {
        if (!phone || !password) {
            Alert.alert('Missing Info', 'Please enter your phone number and password.');
            return;
        }
        const success = await login(phone, password);
        if (success) {
            router.replace('/(main)/home');
        } else {
            Alert.alert('Login Failed', 'Incorrect phone number or password. Please try again.');
        }
    };

    return (
        <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
            <View style={styles.topSection}>
                <Text style={styles.logo}>🏥</Text>
                <Text style={styles.appName}>HealthBridge AI</Text>
                <Text style={styles.tagline}>Your personal health screening assistant</Text>
            </View>

            <View style={styles.card}>
                <Text style={styles.cardTitle}>Patient Login</Text>

                <Text style={styles.label}>Phone Number</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Enter your phone number"
                    placeholderTextColor={Colors.textSecondary}
                    keyboardType="phone-pad"
                    value={phone}
                    onChangeText={setPhone}
                    autoCapitalize="none"
                />

                <Text style={styles.label}>Password</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Enter your password"
                    placeholderTextColor={Colors.textSecondary}
                    secureTextEntry
                    value={password}
                    onChangeText={setPassword}
                />

                <TouchableOpacity
                    style={[styles.button, isLoading && styles.buttonDisabled]}
                    onPress={handleLogin}
                    disabled={isLoading}
                >
                    {isLoading
                        ? <ActivityIndicator color={Colors.white} />
                        : <Text style={styles.buttonText}>Login</Text>}
                </TouchableOpacity>

                <TouchableOpacity style={styles.registerLink} onPress={() => Alert.alert('Register', 'Registration coming soon!')}>
                    <Text style={styles.registerText}>New patient? <Text style={styles.registerHighlight}>Create account</Text></Text>
                </TouchableOpacity>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
        backgroundColor: Colors.primary,
        justifyContent: 'center',
        padding: 24,
    },
    topSection: {
        alignItems: 'center',
        marginBottom: 32,
    },
    logo: { fontSize: 64, marginBottom: 8 },
    appName: {
        fontSize: 28,
        fontWeight: 'bold',
        color: Colors.white,
        marginBottom: 8,
    },
    tagline: {
        fontSize: 14,
        color: 'rgba(255,255,255,0.8)',
        textAlign: 'center',
    },
    card: {
        backgroundColor: Colors.white,
        borderRadius: 20,
        padding: 28,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2,
        shadowRadius: 16,
        elevation: 10,
    },
    cardTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: Colors.textPrimary,
        marginBottom: 20,
        textAlign: 'center',
    },
    label: {
        fontSize: 13,
        fontWeight: '600',
        color: Colors.textSecondary,
        marginBottom: 6,
    },
    input: {
        borderWidth: 1,
        borderColor: '#e2e8f0',
        borderRadius: 10,
        padding: 14,
        fontSize: 16,
        color: Colors.textPrimary,
        marginBottom: 16,
        backgroundColor: '#f8fafc',
    },
    button: {
        backgroundColor: Colors.primary,
        borderRadius: 12,
        paddingVertical: 15,
        alignItems: 'center',
        marginTop: 4,
    },
    buttonDisabled: { opacity: 0.6 },
    buttonText: { color: Colors.white, fontSize: 17, fontWeight: '700' },
    registerLink: { marginTop: 16, alignItems: 'center' },
    registerText: { fontSize: 14, color: Colors.textSecondary },
    registerHighlight: { color: Colors.primary, fontWeight: '700' },
});
