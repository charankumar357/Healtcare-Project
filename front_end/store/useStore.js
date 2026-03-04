import { create } from 'zustand';

// Mock data based on the spec
const MOCK_ASSESSMENT = {
    score: 72,
    tier: 'high', // 'low' | 'moderate' | 'high' | 'critical'
    explanation: {
        en: {
            why: [
                'Persistent high fever for 3 days',
                'Difficulty breathing during mild exertion',
                'History of hypertension'
            ],
            meaning: 'Your symptoms indicate a high risk of respiratory complication that requires medical attention.',
            whatToDo: 'Schedule a teleconsultation with a doctor within 24 hours.'
        },
        hi: {
            why: [
                '3 दिनों से लगातार तेज बुखार',
                'हल्के परिश्रम के दौरान सांस लेने में कठिनाई',
                'उच्च रक्तचाप का इतिहास'
            ],
            meaning: 'आपके लक्षण श्वसन संबंधी जटिलताओं के उच्च जोखिम का संकेत देते हैं जिसके लिए चिकित्सा ध्यान देने की आवश्यकता है।',
            whatToDo: '24 घंटे के भीतर डॉक्टर से टेलीकंसल्टेशन शेड्यूल करें।'
        },
        te: {
            why: [
                '3 రోజుల పాటు నిరంతర అధిక జ్వరం',
                'స్వల్ప శ్రమ సమయంలో శ్వాస తీసుకోవడంలో ఇబ్బంది',
                'రక్తపోటు చరిత్ర'
            ],
            meaning: 'మీ లక్షణాలు శ్వాసకోశ సమస్యల యొక్క అధిక ప్రమాదాన్ని సూచిస్తున్నాయి, దీనికి వైద్య సహాయం అవసరం.',
            whatToDo: '24 గంటలలోపు డాక్టర్‌తో టెలికన్సల్టేషన్‌ను షెడ్యూల్ చేయండి.'
        }
    }
};

export const useStore = create((set) => ({
    language: 'en', // 'en', 'hi', 'te', 'ta'
    setLanguage: (lang) => set({ language: lang }),

    currentAssessment: MOCK_ASSESSMENT,
    setCurrentAssessment: (assessment) => set({ currentAssessment: assessment }),
}));
