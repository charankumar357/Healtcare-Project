import { Stack } from 'expo-router';

export default function AshaLayout() {
    return (
        <Stack
            screenOptions={{
                headerStyle: { backgroundColor: '#1B4F72' },
                headerTintColor: '#FFFFFF',
                headerTitleStyle: { fontWeight: 'bold' },
            }}
        >
            <Stack.Screen
                name="roster"
                options={{ title: 'Patient Roster' }}
            />
            <Stack.Screen
                name="batch"
                options={{ title: 'Batch Screening' }}
            />
        </Stack>
    );
}
