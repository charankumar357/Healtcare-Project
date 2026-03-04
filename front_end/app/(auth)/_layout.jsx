import { Stack } from 'expo-router';

export default function AuthLayout() {
    return (
        <Stack
            screenOptions={{
                headerStyle: { backgroundColor: '#1B4F72' },
                headerTintColor: '#FFFFFF',
                headerTitleStyle: { fontWeight: 'bold' },
            }}
        >
            <Stack.Screen
                name="login"
                options={{ title: 'Login', headerShown: false }}
            />
        </Stack>
    );
}
