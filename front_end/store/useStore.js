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
     * Local fallback scorer — used when API is unavailable (demo mode / no token).
     * Simple rule-based scoring on keyword presence.
     */
    _localScore(symptomText) {
        const text = symptomText.toLowerCase();

        // Critical red-flag keywords
        const critical = ['chest pain', 'cannot breathe', 'unconscious', 'seizure', 'stroke', 'heart attack', 'bleeding heavily'];
        // High risk keywords
        const high = ['difficulty breathing', 'breathless', 'severe', 'high fever', 'vomiting blood', 'fainting', 'swelling'];
        // Moderate keywords
        const moderate = ['fever', 'headache', 'cough', 'cold', 'body pain', 'weakness', 'dizziness', 'nausea', 'diarrhoea', 'vomiting'];

        let score = 10;
        if (critical.some(k => text.includes(k))) score = 90;
        else if (high.some(k => text.includes(k))) score = 65;
        else if (moderate.some(k => text.includes(k))) score = 40;

        const tier =
            score >= 80 ? 'critical' :
                score >= 60 ? 'high' :
                    score >= 35 ? 'moderate' : 'low';

        const messages = {
            critical: {
                why: ['Critical symptoms detected — immediate emergency care needed'],
                meaning: 'Your symptoms indicate a potentially life-threatening condition.',
                whatToDo: '🚨 Call 108 immediately or go to the nearest emergency room.',
            },
            high: {
                why: ['High-risk symptoms detected'],
                meaning: 'Your symptoms suggest a serious condition that requires prompt medical attention.',
                whatToDo: 'Visit a doctor or hospital today. Do not delay.',
            },
            moderate: {
                why: ['Moderate symptoms identified: ' + moderate.filter(k => text.includes(k)).join(', ')],
                meaning: 'Your symptoms indicate a moderate health concern.',
                whatToDo: 'Consult a doctor within 24–48 hours. Rest and stay hydrated.',
            },
            low: {
                why: ['Mild symptoms detected'],
                meaning: 'Your symptoms appear mild at this time.',
                whatToDo: 'Monitor your symptoms. If they worsen, consult a doctor.',
            },
        };

        return {
            score,
            tier,
            redFlag: tier === 'critical',
            redFlagReason: tier === 'critical' ? 'Critical symptoms present' : null,
            symptoms: moderate.filter(k => text.includes(k)).concat(high.filter(k => text.includes(k))),
            explanation: { en: messages[tier], hi: messages[tier], te: messages[tier] },
            recommendation: messages[tier].whatToDo,
        };
    },

    /**
     * Full pipeline: extract → score → explain → recommend
     * Falls back to local scoring if API unavailable (demo mode / no token).
     */
    runScreening: async (symptomText, demographics) => {
        set({ isLoading: true, error: null });
        try {
            const lang = get().language;
            let assessment;

            try {
                // Try the real API first
                const extractResult = await api.extractSymptoms(symptomText, lang);
                const symptoms = extractResult.symptoms;
                const scoreResult = await api.scoreRisk(symptoms, demographics);
                const explainResult = await api.explainRisk(scoreResult.risk_score, scoreResult.risk_tier, lang);
                const recResult = await api.getRecommendation(scoreResult.risk_tier, symptoms, lang);

                // Format explanation to match what result.jsx expects
                const formattedExplanation = {};
                formattedExplanation[lang] = {
                    why: explainResult.why_this_score || [],
                    meaning: explainResult.what_it_means || '',
                    whatToDo: explainResult.what_to_do_now || ''
                };

                assessment = {
                    score: scoreResult.risk_score,
                    tier: scoreResult.risk_tier,
                    redFlag: scoreResult.red_flag_triggered,
                    redFlagReason: scoreResult.red_flag_reason,
                    symptoms,
                    explanation: formattedExplanation,
                    recommendation: recResult,
                };
            } catch (apiError) {
                // API failed (e.g. 401 Unauthorized in Demo Mode, or Network Error)
                console.log('API unavailable, using local scoring:', apiError.message);
                assessment = get()._localScore(symptomText);
            }

            set({ currentAssessment: assessment, isLoading: false });
            return assessment;
        } catch (e) {
            // Only catch catastrophic non-API errors here
            console.error('Screening pipeline failed:', e);
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
