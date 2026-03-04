import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SQLiteProvider } from 'expo-sqlite';
import { initDatabase } from '../hooks/useDatabase';
import NetworkSyncer from '../components/NetworkSyncer';

export default function RootLayout() {
    return (
        <SQLiteProvider databaseName="healthbridge.db" onInit={initDatabase}>
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
                <Stack.Screen name="(asha)" options={{ headerShown: false }} />
            </Stack>
        </SQLiteProvider>
    );
}
