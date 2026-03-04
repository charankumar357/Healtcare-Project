import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import Colors from '../../constants/Colors';

export default function ProcessingScreen() {
    return (
        <View style={styles.container}>
            <ActivityIndicator size="large" color={Colors.primary} />
            <Text style={styles.title}>Analyzing Symptoms</Text>
            <Text style={styles.subtitle}>
                Our AI is processing your health data...
            </Text>
            {/* TODO: Replace with Lottie animation */}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: Colors.primary,
        marginTop: 24,
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 14,
        color: Colors.textSecondary,
        textAlign: 'center',
    },
});
