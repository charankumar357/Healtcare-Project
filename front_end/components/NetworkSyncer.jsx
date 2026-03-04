import { useEffect, useRef } from 'react';
import { Platform } from 'react-native';

/**
 * Headless component that syncs offline sessions when network is restored.
 * On web: uses navigator.onLine events (no native NetInfo needed).
 * On native: uses @react-native-community/netinfo.
 */
export default function NetworkSyncer() {
    const syncingRef = useRef(false);

    const handleSync = async () => {
        if (syncingRef.current) return;
        // On web, we skip SQLite sync (no local DB on web)
        // Sync happens automatically via the backend API calls
        console.log('Network reconnected — online mode active.');
    };

    useEffect(() => {
        if (Platform.OS === 'web') {
            // Web: use browser online/offline events
            window.addEventListener('online', handleSync);
            return () => window.removeEventListener('online', handleSync);
        } else {
            // Native: use NetInfo
            let unsubscribe = () => { };
            (async () => {
                try {
                    const NetInfo = require('@react-native-community/netinfo').default;
                    unsubscribe = NetInfo.addEventListener((state) => {
                        if (state.isConnected && state.isInternetReachable) {
                            handleSync();
                        }
                    });
                } catch (e) {
                    console.log('NetInfo not available:', e.message);
                }
            })();
            return () => unsubscribe();
        }
    }, []);

    return null; // Headless component
}
