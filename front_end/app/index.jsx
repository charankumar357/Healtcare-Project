import { Redirect } from 'expo-router';

export default function Index() {
    // Entry point — redirect to the auth flow
    return <Redirect href="/(auth)/login" />;
}
