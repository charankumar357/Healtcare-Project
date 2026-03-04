import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as api from '../services/api';

export const useStore = create((set, get) => ({
    // ─── State ───
    language: 'en',         // 'en' | 'hi' | 'te' | 'ta' | 'kn'
    token: null,
    worker: null,
    currentAssessment: null,  // filled after full screening pipeline
    isLoading: false,
    error: null,

    // ─── Setters ───
    setLanguage: (lang) => set({ language: lang }),
    setError: (error) => set({ error }),
    clearError: () => set({ error: null }),

    // ─── Auth ───
    login: async (phone, password) => {
        set({ isLoading: true, error: null });
        try {
            const data = await api.login(phone, password);
            set({ token: data.access_token, isLoading: false });
            return true;
        } catch (e) {
            set({ error: e.message, isLoading: false });
            return false;
        }
    },

    logout: async () => {
        await api.logout();
        set({ token: null, worker: null, currentAssessment: null });
    },

    loadToken: async () => {
        const token = await AsyncStorage.getItem('jwt_token');
        if (token) set({ token });
    },

    // ─── Screening Pipeline ───
    /**
     * Full pipeline: extract → score → explain → recommend
     * Returns { score, tier, explanation, recommendation } or throws
     */
    runScreening: async (symptomText, demographics) => {
        set({ isLoading: true, error: null });
        try {
            const lang = get().language;

            // Step 1: Extract symptoms from text
            const extractResult = await api.extractSymptoms(symptomText, lang);
            const symptoms = extractResult.symptoms;

            // Step 2: Score risk
            const scoreResult = await api.scoreRisk(symptoms, demographics);

            // Step 3: Explanation in patient's language
            const explainResult = await api.explainRisk(
                scoreResult.risk_score,
                scoreResult.risk_tier,
                lang
            );

            // Step 4: Recommendation
            const recResult = await api.getRecommendation(
                scoreResult.risk_tier,
                symptoms,
                lang
            );

            const assessment = {
                score: scoreResult.risk_score,
                tier: scoreResult.risk_tier,
                redFlag: scoreResult.red_flag_triggered,
                redFlagReason: scoreResult.red_flag_reason,
                symptoms,
                explanation: explainResult,
                recommendation: recResult,
            };

            set({ currentAssessment: assessment, isLoading: false });
            return assessment;
        } catch (e) {
            set({ error: e.message, isLoading: false });
            throw e;
        }
    },

    /** Save completed session to the database */
    saveSession: async (patientInfo) => {
        const { currentAssessment, language } = get();
        if (!currentAssessment) return null;
        return api.completeSession({
            ...patientInfo,
            ...currentAssessment,
            language,
        });
    },
}));
