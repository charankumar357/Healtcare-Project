-- ============================================================================
-- HealthBridge AI — Database Schema
-- Run this script directly in your Neon.tech SQL Editor or psql
-- ============================================================================

-- Enable UUID extension (required for uuid_generate_v4)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: patients
-- ============================================================================
CREATE TABLE IF NOT EXISTS patients (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_hash      VARCHAR(64) NOT NULL UNIQUE,      -- SHA-256 hash of phone (never store raw phone)
    age             INTEGER NOT NULL,
    gender          VARCHAR(10) NOT NULL,              -- male | female | other
    district        VARCHAR(100),
    state           VARCHAR(100),
    pincode         VARCHAR(6),
    preferred_language VARCHAR(5) DEFAULT 'en',        -- en | hi | te | ta | kn
    comorbidities   TEXT,                              -- JSON array string: '["diabetes","hypertension"]'
    is_pregnant     BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast patient lookup by phone hash
CREATE INDEX IF NOT EXISTS idx_patients_phone_hash ON patients(phone_hash);

-- ============================================================================
-- TABLE 2: asha_workers
-- ============================================================================
CREATE TABLE IF NOT EXISTS asha_workers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(100) NOT NULL,
    phone_hash          VARCHAR(64) NOT NULL UNIQUE,   -- SHA-256 hash of phone
    password_hash       VARCHAR(128) NOT NULL,          -- bcrypt hash of password
    district            VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    phc_name            VARCHAR(200),                   -- Primary Health Centre name
    preferred_language  VARCHAR(5) DEFAULT 'en',        -- en | hi | te | ta | kn
    total_screenings    INTEGER DEFAULT 0,
    is_active           BOOLEAN DEFAULT TRUE,
    last_login_at       TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast worker lookup by phone hash
CREATE INDEX IF NOT EXISTS idx_asha_workers_phone_hash ON asha_workers(phone_hash);

-- ============================================================================
-- TABLE 3: screening_sessions
-- ============================================================================
CREATE TABLE IF NOT EXISTS screening_sessions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id              UUID NOT NULL REFERENCES patients(id),
    asha_worker_id          UUID REFERENCES asha_workers(id),

    -- Input
    raw_symptom_text        TEXT NOT NULL,               -- Original text (Hindi/Telugu/English)
    detected_language       VARCHAR(5) DEFAULT 'en',     -- Language detected during extraction
    input_mode              VARCHAR(10) DEFAULT 'text',  -- text | voice

    -- Extraction Result
    extracted_symptoms      JSONB,                       -- JSON from symptom extraction LLM call

    -- Scoring Result
    risk_score              INTEGER,                     -- 0-100
    risk_tier               VARCHAR(10),                 -- low | moderate | high | critical
    red_flag_triggered      BOOLEAN DEFAULT FALSE,
    red_flag_reason         TEXT,
    scoring_result          JSONB,                       -- Full scoring JSON from LLM or offline scorer

    -- Recommendation
    recommendation_type     VARCHAR(20),                 -- self_care | teleconsultation | hospital_visit | emergency
    recommendation_details  JSONB,

    -- Explanation
    explanation             JSONB,                       -- Plain-language explanation for the patient

    -- LLM Metadata
    scoring_method          VARCHAR(10) DEFAULT 'llm',   -- llm | offline
    llm_model_used          VARCHAR(50),
    llm_latency_ms          INTEGER,
    llm_tokens_used         INTEGER,

    -- PDF Report
    pdf_report_url          VARCHAR(500),

    -- Offline Sync
    is_synced               BOOLEAN DEFAULT TRUE,        -- FALSE if created offline
    device_id               VARCHAR(100),
    offline_created_at      TIMESTAMPTZ,                 -- Original creation time on device

    -- Timestamps
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_sessions_patient_id ON screening_sessions(patient_id);
CREATE INDEX IF NOT EXISTS idx_sessions_asha_worker_id ON screening_sessions(asha_worker_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON screening_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_risk_tier ON screening_sessions(risk_tier);

-- ============================================================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all 3 tables
CREATE TRIGGER trigger_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_asha_workers_updated_at
    BEFORE UPDATE ON asha_workers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_sessions_updated_at
    BEFORE UPDATE ON screening_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DONE! Verify tables were created:
-- ============================================================================
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
