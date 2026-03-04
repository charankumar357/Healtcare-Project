import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Colors from '../../constants/Colors';

export default function ReportScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Assessment Report</Text>

            <View style={styles.previewCard}>
                <Text style={styles.previewHeader}>Patient Health Report</Text>
                <Text style={styles.previewText}>Date: {new Date().toLocaleDateString()}</Text>
                <Text style={styles.previewText}>Risk Level: Moderate</Text>
                <Text style={styles.previewText}>Symptoms: Fever, Cough</Text>

                <View style={styles.pdfPlaceholder}>
                    <Text style={styles.pdfText}>PDF Preview</Text>
                </View>
            </View>

            <TouchableOpacity style={styles.shareButton}>
                <Text style={styles.shareText}>📤 Share PDF via WhatsApp</Text>
            </TouchableOpacity>
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
    previewCard: {
        backgroundColor: Colors.white,
        borderRadius: 12,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 8,
        elevation: 2,
        flex: 1,
        marginBottom: 24,
    },
    previewHeader: {
        fontSize: 18,
        fontWeight: 'bold',
        color: Colors.primary,
        marginBottom: 16,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
        paddingBottom: 12,
    },
    previewText: {
        fontSize: 14,
        color: Colors.textSecondary,
        marginBottom: 8,
    },
    pdfPlaceholder: {
        flex: 1,
        backgroundColor: Colors.background,
        borderRadius: 8,
        marginTop: 20,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: Colors.border,
        borderStyle: 'dashed',
    },
    pdfText: {
        color: Colors.disabled,
        fontWeight: '600',
    },
    shareButton: {
        backgroundColor: Colors.secondary,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    shareText: {
        color: Colors.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
});
