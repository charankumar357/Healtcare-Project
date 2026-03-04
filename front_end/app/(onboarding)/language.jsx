import { View, Text, StyleSheet } from 'react-native';
import Colors from '../../constants/Colors';

export default function LanguageScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Choose Your Language</Text>
            <Text style={styles.subtitle}>Select a language to continue</Text>

            <View style={styles.grid}>
                {['English', 'हिन्दी', 'தமிழ்', 'తెలుగు', 'ಕನ್ನಡ', 'मराठी'].map(
                    (lang, index) => (
                        <View key={index} style={styles.langCard}>
                            <Text style={styles.langText}>{lang}</Text>
                            <Text style={styles.audioIcon}>🔊</Text>
                        </View>
                    )
                )}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
        padding: 24,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: Colors.primary,
        textAlign: 'center',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 14,
        color: Colors.textSecondary,
        textAlign: 'center',
        marginBottom: 24,
    },
    grid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        gap: 12,
    },
    langCard: {
        width: '47%',
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.08,
        shadowRadius: 8,
        elevation: 3,
    },
    langText: {
        fontSize: 16,
        fontWeight: '600',
        color: Colors.textPrimary,
    },
    audioIcon: {
        fontSize: 20,
    },
});
