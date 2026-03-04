import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Platform } from 'react-native';
import NetworkSyncer from '../components/NetworkSyncer';

// SQLiteProvider is native-only — skip on web to prevent blank page
let SQLiteWrapper;
if (Platform.OS !== 'web') {
    const { SQLiteProvider } = require('expo-sqlite');
    const { initDatabase } = require('../hooks/useDatabase');
    SQLiteWrapper = ({ children }) => (
        <SQLiteProvider databaseName="healthbridge.db" onInit={initDatabase}>
            {children}
        </SQLiteProvider>
    );
} else {
    SQLiteWrapper = ({ children }) => <>{children}</>;
}

export default function RootLayout() {
    return (
        <SQLiteWrapper>
            <StatusBar style="light" />
            <NetworkSyncer />
            <Stack
                screenOptions={{
                    headerStyle: { backgroundColor: '#1B4F72' },
                    headerTintColor: '#FFFFFF',
                    headerTitleStyle: { fontWeight: 'bold' },
                    contentStyle: { backgroundColor: '#F4F6F8' },
                }}
            >
                <Stack.Screen name="index" options={{ headerShown: false }} />
                <Stack.Screen name="(auth)" options={{ headerShown: false }} />
                <Stack.Screen name="(onboarding)" options={{ headerShown: false }} />
                <Stack.Screen name="(main)" options={{ headerShown: false }} />
                {/* (asha) screens removed — patient-only app */}
            </Stack>
        </SQLiteWrapper>
    );
}
