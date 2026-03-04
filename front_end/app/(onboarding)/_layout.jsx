import { Stack } from 'expo-router';

export default function OnboardingLayout() {
    return (
        <Stack
            screenOptions={{
                headerStyle: { backgroundColor: '#1B4F72' },
                headerTintColor: '#FFFFFF',
                headerTitleStyle: { fontWeight: 'bold' },
            }}
        >
            <Stack.Screen
                name="language"
                options={{ title: 'Select Language' }}
            />
            <Stack.Screen
                name="consent"
                options={{ title: 'Data Consent' }}
            />
        </Stack>
    );
}
