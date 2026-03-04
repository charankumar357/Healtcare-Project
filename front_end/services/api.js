/**
 * HealthBridge AI — API Service
 * All backend calls go through this file.
 *
 * LOCAL DEV:  BASE_URL = 'http://192.168.x.x:8000'  (your PC's IP on LAN)
 * PRODUCTION: BASE_URL = 'https://healthbridge-api.onrender.com'
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// ─── Backend URL ───
export const BASE_URL = 'https://healthbridge-api.onrender.com';

// ─────────────────────────────────────────────
// Internal helper: make authenticated requests
// ─────────────────────────────────────────────
async function request(method, path, body = null) {
  const token = await AsyncStorage.getItem('jwt_token');

  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${path}`, options);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `HTTP ${res.status}`);
  }
  return data;
}

// ─────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────

/** Register a new ASHA worker */
export async function register(name, phone, password, district, state) {
  return request('POST', '/auth/register', { name, phone, password, district, state });
}

/** Login → saves JWT token to AsyncStorage */
export async function login(phone, password) {
  // FastAPI OAuth2 expects form-data for /auth/login
  const token = await AsyncStorage.getItem('jwt_token'); // not needed here
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(phone)}&password=${encodeURIComponent(password)}`,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Login failed');

  // Save token for all future requests
  await AsyncStorage.setItem('jwt_token', data.access_token);
  return data;
}

/** Logout — remove token */
export async function logout() {
  await AsyncStorage.removeItem('jwt_token');
}

/** Get current logged-in worker info */
export async function getMe() {
  return request('GET', '/auth/me');
}

// ─────────────────────────────────────────────
// SCREENING PIPELINE
// ─────────────────────────────────────────────

/**
 * Step 1: Extract symptoms from raw text
 * @param {string} symptomText - Raw text in any language
 * @param {string} language    - 'en' | 'hi' | 'te' | 'ta' | 'kn'
 */
export async function extractSymptoms(symptomText, language = 'en') {
  return request('POST', '/screening/extract', {
    symptom_text: symptomText,
    language,
  });
}

/**
 * Step 2: Score risk from extracted symptoms + demographics
 * @param {Array}  symptoms    - From extractSymptoms response
 * @param {object} demographics - { age, gender, comorbidities, pregnancy }
 */
export async function scoreRisk(symptoms, demographics) {
  return request('POST', '/screening/score', { symptoms, demographics });
}

/**
 * Step 3: Get plain-language explanation
 * @param {number} riskScore
 * @param {string} riskTier  - 'low' | 'moderate' | 'high' | 'critical'
 * @param {string} language  - Patient's preferred language
 */
export async function explainRisk(riskScore, riskTier, language = 'en') {
  return request('POST', '/screening/explain', { risk_score: riskScore, risk_tier: riskTier, language });
}

/**
 * Step 4: Get recommendation
 * @param {string} riskTier
 * @param {Array}  symptoms
 * @param {string} language
 */
export async function getRecommendation(riskTier, symptoms, language = 'en') {
  return request('POST', '/screening/recommend', { risk_tier: riskTier, symptoms, language });
}

/**
 * Step 5: Save the full completed session to the database
 */
export async function completeSession(sessionData) {
  return request('POST', '/screening/complete', sessionData);
}

/** Get all past sessions for the logged-in ASHA worker */
export async function getSessions() {
  return request('GET', '/screening/sessions');
}

// ─────────────────────────────────────────────
// AUDIO TRANSCRIPTION
// ─────────────────────────────────────────────

/**
 * Transcribe voice recording via Groq Whisper
 * @param {object} audioFile - { uri, name, type } from Expo Audio
 */
export async function transcribeAudio(audioFile) {
  const token = await AsyncStorage.getItem('jwt_token');
  const formData = new FormData();
  formData.append('audio', { uri: audioFile.uri, name: audioFile.name || 'recording.m4a', type: audioFile.type || 'audio/m4a' });

  const res = await fetch(`${BASE_URL}/audio/transcribe`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Transcription failed');
  return data;
}

// ─────────────────────────────────────────────
// REPORT & FACILITIES
// ─────────────────────────────────────────────

/** Get PDF report URL for a session */
export function getReportUrl(sessionId) {
  return `${BASE_URL}/report/${sessionId}/pdf`;
}

/**
 * Get nearby health facilities
 * @param {number} lat
 * @param {number} lng
 */
export async function getNearbyFacilities(lat, lng) {
  return request('GET', `/facilities/nearby?lat=${lat}&lng=${lng}`);
}

// ─────────────────────────────────────────────
// OFFLINE SYNC
// ─────────────────────────────────────────────

/**
 * Batch sync offline sessions
 * @param {Array} sessions - Array of offline session objects
 */
export async function syncOfflineSessions(sessions) {
  return request('POST', '/sessions/sync', { sessions });
}
