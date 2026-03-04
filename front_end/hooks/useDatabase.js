import { useSQLiteContext } from 'expo-sqlite';
import axios from 'axios';

// The Database Init Function to be passed to SQLiteProvider
export async function initDatabase(db) {
    try {
        // Enable WAL mode for better performance
        await db.execAsync('PRAGMA journal_mode = WAL');

        await db.execAsync(`
      CREATE TABLE IF NOT EXISTS screening_sessions (
        id TEXT PRIMARY KEY,
        patient_id TEXT,
        symptoms_json TEXT,
        risk_score INTEGER,
        risk_tier TEXT,
        recommendation_type TEXT,
        explanation_json TEXT,
        created_at TEXT,
        synced INTEGER DEFAULT 0
      );

      CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        age_band TEXT,
        gender TEXT,
        language TEXT,
        conditions TEXT
      );
    `);
        console.log('Database initialized successfully.');
    } catch (error) {
        console.error('Database Init Error:', error);
    }
}

export function useDatabase() {
    const db = useSQLiteContext();

    const saveSession = async (sessionData) => {
        try {
            const {
                id,
                patient_id,
                symptoms_json,
                risk_score,
                risk_tier,
                recommendation_type,
                explanation_json
            } = sessionData;

            const created_at = new Date().toISOString();

            await db.runAsync(
                `INSERT INTO screening_sessions (id, patient_id, symptoms_json, risk_score, risk_tier, recommendation_type, explanation_json, created_at, synced)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)`,
                [id, patient_id, JSON.stringify(symptoms_json), risk_score, risk_tier, recommendation_type, JSON.stringify(explanation_json), created_at]
            );

            console.log('Saved offline session:', id);
            return true;
        } catch (error) {
            console.error('Failed to save session:', error);
            return false;
        }
    };

    const getSessions = async (patientId) => {
        try {
            const result = await db.getAllAsync(
                'SELECT * FROM screening_sessions WHERE patient_id = ? ORDER BY created_at DESC',
                [patientId]
            );
            return result;
        } catch (error) {
            console.error('Failed to get sessions:', error);
            return [];
        }
    };

    const syncPendingSessions = async () => {
        try {
            // 1. Find all unsynced
            const pending = await db.getAllAsync(
                'SELECT * FROM screening_sessions WHERE synced = 0'
            );

            if (pending.length === 0) {
                console.log('No pending sessions to sync.');
                return;
            }

            console.log(`Found ${pending.length} sessions to sync...`);

            // 2. Post each to backend (Mocked endpoint for HealthBridge)
            for (const session of pending) {
                // Parse the JSON strings back to objects for the API payload
                const payload = {
                    ...session,
                    symptoms_json: JSON.parse(session.symptoms_json),
                    explanation_json: JSON.parse(session.explanation_json),
                };

                try {
                    // This is a mocked API endpoint per the spec
                    await axios.post('https://api.healthbridge.mock/sessions/sync', payload);

                    // 3. Mark as synced
                    await db.runAsync(
                        'UPDATE screening_sessions SET synced = 1 WHERE id = ?',
                        [session.id]
                    );
                    console.log(`Synced session: ${session.id}`);
                } catch (apiError) {
                    console.error(`Failed to sync session ${session.id}, will retry later`, apiError.message);
                }
            }
        } catch (error) {
            console.error('Error during sync block:', error);
        }
    };

    return {
        saveSession,
        getSessions,
        syncPendingSessions
    };
}
