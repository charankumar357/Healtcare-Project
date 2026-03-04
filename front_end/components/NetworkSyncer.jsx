import { useEffect, useRef } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { useDatabase } from '../hooks/useDatabase';

/**
 * Headless component that listens for network changes and
 * triggers a background sync of the offline SQLite database.
 */
export default function NetworkSyncer() {
    const { syncPendingSessions } = useDatabase();
    const syncingRef = useRef(false);

    useEffect(() => {
        // Subscribe to network state updates
        const unsubscribe = NetInfo.addEventListener((state) => {
            // If we just got internet back, and we aren't already syncing
            if (state.isConnected && state.isInternetReachable && !syncingRef.current) {
                console.log('Network connected. Attempting sync...');

                syncingRef.current = true;

                syncPendingSessions().finally(() => {
                    syncingRef.current = false;
                });
            }
        });

        // Cleanup subscription on unmount
        return () => unsubscribe();
    }, [syncPendingSessions]);

    // Headless component renders nothing
    return null;
}
