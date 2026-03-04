import { Tabs } from 'expo-router';
import Colors from '../../constants/Colors';

export default function MainLayout() {
    return (
        <Tabs
            screenOptions={{
                headerStyle: { backgroundColor: Colors.primary },
                headerTintColor: '#FFFFFF',
                headerTitleStyle: { fontWeight: 'bold' },
                tabBarActiveTintColor: Colors.primary,
                tabBarInactiveTintColor: Colors.disabled,
                tabBarStyle: {
                    backgroundColor: Colors.white,
                    borderTopWidth: 1,
                    borderTopColor: Colors.border,
                    height: 60,
                    paddingBottom: 8,
                    paddingTop: 4,
                },
            }}
        >
            <Tabs.Screen
                name="home"
                options={{
                    title: 'Home',
                    tabBarLabel: 'Home',
                    tabBarIcon: () => null, // TODO: add icon
                }}
            />
            <Tabs.Screen
                name="symptom-input"
                options={{
                    title: 'Symptoms',
                    tabBarLabel: 'Symptoms',
                    tabBarIcon: () => null,
                }}
            />
            <Tabs.Screen
                name="report"
                options={{
                    title: 'Reports',
                    tabBarLabel: 'Reports',
                    tabBarIcon: () => null,
                }}
            />
            {/* These screens are accessible via stack push, not tabs */}
            <Tabs.Screen
                name="processing"
                options={{ href: null, title: 'Processing' }}
            />
            <Tabs.Screen
                name="result"
                options={{ href: null, title: 'Results' }}
            />
            <Tabs.Screen
                name="recommendation"
                options={{ href: null, title: 'Recommendations' }}
            />
        </Tabs>
    );
}
