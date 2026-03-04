import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
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
            Alert.alert('Login Failed', 'Incorrect phone number or password.');
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.card}>
                <Text style={styles.title}>🏥 HealthBridge</Text>
                <Text style={styles.subtitle}>ASHA Worker Login</Text>

                <TextInput
                    style={styles.input}
                    placeholder="Phone number"
                    placeholderTextColor={Colors.textSecondary}
                    keyboardType="phone-pad"
                    value={phone}
                    onChangeText={setPhone}
                    autoCapitalize="none"
                />
                <TextInput
                    style={styles.input}
                    placeholder="Password"
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
        marginBottom: 24,
    },
    input: {
        width: '100%',
        borderWidth: 1,
        borderColor: Colors.disabled,
        borderRadius: 10,
        padding: 14,
        fontSize: 16,
        color: Colors.textPrimary,
        marginBottom: 14,
        backgroundColor: '#f9f9f9',
    },
    button: {
        backgroundColor: Colors.primary,
        borderRadius: 10,
        paddingVertical: 14,
        width: '100%',
        alignItems: 'center',
        marginTop: 8,
    },
    buttonDisabled: { opacity: 0.6 },
    buttonText: {
        color: Colors.white,
        fontSize: 16,
        fontWeight: '700',
    },
});
