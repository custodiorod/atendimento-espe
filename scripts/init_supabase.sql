-- ============================================================
-- CLINIC AI - SUPABASE DATABASE INITIALIZATION SCRIPT
-- ============================================================
-- This script creates all tables, indexes, and functions
-- for the Clinic AI system.
--
-- Execute this in your Supabase SQL Editor.
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For RAG embeddings

-- ============================================================
-- 1. CONTACTS TABLE
-- ============================================================
-- Stores patient/lead identity
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT UNIQUE,
    full_name TEXT,
    phone_e164 TEXT NOT NULL UNIQUE,
    birth_date DATE,
    is_existing_patient BOOLEAN DEFAULT FALSE,
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    consent_status TEXT DEFAULT 'unknown', -- unknown, opted_in, opted_out
    opt_out BOOLEAN DEFAULT FALSE,
    source TEXT DEFAULT 'whatsapp',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_e164);
CREATE INDEX IF NOT EXISTS idx_contacts_external_id ON contacts(external_id);
CREATE INDEX IF NOT EXISTS idx_contacts_is_existing_patient ON contacts(is_existing_patient);
CREATE INDEX IF NOT EXISTS idx_contacts_last_seen ON contacts(last_seen_at DESC);

-- ============================================================
-- 2. CONVERSATIONS TABLE
-- ============================================================
-- Stores conversation state and ownership
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    owner TEXT NOT NULL DEFAULT 'ai', -- ai, human
    mode TEXT, -- sdr, support, finance, post_consulta
    status TEXT DEFAULT 'active', -- active, paused, closed
    paused_until TIMESTAMPTZ,
    last_message_at TIMESTAMPTZ,
    last_response_at TIMESTAMPTZ,
    last_intent TEXT,
    last_stage TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_conversations_contact ON conversations(contact_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_owner ON conversations(owner);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC);

-- ============================================================
-- 3. MESSAGES TABLE
-- ============================================================
-- Stores all messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    provider_message_id TEXT,
    direction TEXT NOT NULL, -- inbound, outbound
    message_type TEXT DEFAULT 'text', -- text, image, audio, video, document
    content TEXT,
    media_url TEXT,
    transcribed_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    trace_id TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_contact ON messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction);

-- ============================================================
-- 4. APPOINTMENTS TABLE
-- ============================================================
-- Stores scheduled appointments
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL,
    doctoralia_appointment_id TEXT UNIQUE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    status TEXT DEFAULT 'scheduled', -- scheduled, confirmed, cancelled, completed, no_show
    is_future BOOLEAN DEFAULT TRUE,
    was_realized BOOLEAN DEFAULT FALSE,
    realized_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    no_show BOOLEAN DEFAULT FALSE,
    created_by TEXT DEFAULT 'ai',
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_appointments_contact ON appointments(contact_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctoralia_id ON appointments(doctoralia_appointment_id);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled_at ON appointments(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id ON appointments(doctor_id);

-- ============================================================
-- 5. PAYMENTS TABLE
-- ============================================================
-- Stores payment information
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    provider TEXT NOT NULL, -- openpix, stripe
    external_payment_id TEXT UNIQUE,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed, expired, cancelled, refunded
    amount DECIMAL(10, 2),
    payment_method TEXT,
    payment_link TEXT,
    paid_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_payments_contact ON payments(contact_id);
CREATE INDEX IF NOT EXISTS idx_payments_appointment ON payments(appointment_id);
CREATE INDEX IF NOT EXISTS idx_payments_external_id ON payments(external_payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- ============================================================
-- 6. CRM_MIRROR TABLE
-- ============================================================
-- Mirror of Kommo CRM data
CREATE TABLE IF NOT EXISTS crm_mirror (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    kommo_lead_id TEXT UNIQUE,
    kommo_contact_id TEXT,
    pipeline_id TEXT,
    stage_id TEXT,
    stage_name TEXT,
    tags JSONB DEFAULT '[]',
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_crm_mirror_contact ON crm_mirror(contact_id);
CREATE INDEX IF NOT EXISTS idx_crm_mirror_kommo_lead ON crm_mirror(kommo_lead_id);
CREATE INDEX IF NOT EXISTS idx_crm_mirror_tags ON crm_mirror USING GIN (tags);

-- ============================================================
-- 7. DOCTOR_PROFILES TABLE
-- ============================================================
-- Doctor information
CREATE TABLE IF NOT EXISTS doctor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctoralia_id TEXT UNIQUE,
    full_name TEXT NOT NULL,
    display_name TEXT,
    specialty TEXT,
    crm TEXT,
    bio_short TEXT,
    bio_sales TEXT,
    accepts_new_patients BOOLEAN DEFAULT TRUE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_doctoralia_id ON doctor_profiles(doctoralia_id);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_active ON doctor_profiles(active);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_specialty ON doctor_profiles(specialty);

-- ============================================================
-- 8. DOCTOR_RULES TABLE
-- ============================================================
-- Doctor operational rules
CREATE TABLE IF NOT EXISTS doctor_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id UUID NOT NULL REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    allows_squeeze_in BOOLEAN DEFAULT FALSE,
    squeeze_in_requires_approval BOOLEAN DEFAULT TRUE,
    teleconsultation_available BOOLEAN DEFAULT FALSE,
    min_patient_age INTEGER,
    max_patient_age INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 9. INSURANCE_RULES TABLE
-- ============================================================
-- Insurance acceptance by doctor
CREATE TABLE IF NOT EXISTS insurance_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id UUID NOT NULL REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    insurance_provider TEXT NOT NULL,
    insurance_plan TEXT,
    accepted BOOLEAN NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_insurance_doctor ON insurance_rules(doctor_id);
CREATE INDEX IF NOT EXISTS idx_insurance_provider ON insurance_rules(insurance_provider);
CREATE INDEX IF NOT EXISTS idx_insurance_accepted ON insurance_rules(accepted);

-- ============================================================
-- 10. FAQ_ENTRIES TABLE
-- ============================================================
-- Knowledge base / FAQ for RAG
CREATE TABLE IF NOT EXISTS faq_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT NOT NULL, -- doctors, insurance, scheduling, payments, compliance, objections, post_consulta, faq_geral
    subcategory TEXT,
    title TEXT NOT NULL,
    question TEXT,
    answer TEXT,
    content TEXT, -- Full content for RAG
    doctor_id UUID REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    insurance_provider TEXT,
    active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_faq_domain ON faq_entries(domain);
CREATE INDEX IF NOT EXISTS idx_faq_active ON faq_entries(active);
CREATE INDEX IF NOT EXISTS idx_faq_doctor_id ON faq_entries(doctor_id);
CREATE INDEX IF NOT EXISTS idx_faq_insurance_provider ON faq_entries(insurance_provider);

-- ============================================================
-- 11. RAG_CHUNKS TABLE
-- ============================================================
-- Vectorized chunks for RAG
CREATE TABLE IF NOT EXISTS rag_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faq_entry_id UUID NOT NULL REFERENCES faq_entries(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI embedding size
    domain TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding ON rag_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_domain ON rag_chunks(domain);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_faq_entry_id ON rag_chunks(faq_entry_id);

-- ============================================================
-- 12. EVENTS TABLE
-- ============================================================
-- Operational audit log
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    trace_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_events_contact ON events(contact_id);
CREATE INDEX IF NOT EXISTS idx_events_conversation ON events(conversation_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_trace_id ON events(trace_id);

-- ============================================================
-- 13. SYNC_STATE TABLE
-- ============================================================
-- Track synchronization state
CREATE TABLE IF NOT EXISTS sync_state (
    id TEXT PRIMARY KEY,
    last_sync_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending', -- pending, in_progress, completed, failed
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 14. FEATURE_FLAGS TABLE
-- ============================================================
-- Feature toggles
CREATE TABLE IF NOT EXISTS feature_flags (
    name TEXT PRIMARY KEY,
    enabled BOOLEAN DEFAULT FALSE,
    description TEXT,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default feature flags
INSERT INTO feature_flags (name, enabled, description) VALUES
    ('ai_after_hours', true, 'Enable AI responses outside business hours'),
    ('encaixe_flow', true, 'Enable squeeze-in/emergency appointment flow'),
    ('send_pix_automatically', false, 'Automatically send Pix payment link'),
    ('followup_automatic', true, 'Enable automatic follow-up messages'),
    ('reativation_30d', true, 'Enable 30-day reactivation flow'),
    ('reativation_60d', true, 'Enable 60-day reactivation flow'),
    ('reativation_90d', true, 'Enable 90-day reactivation flow')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- 15. BUSINESS_HOURS TABLE
-- ============================================================
-- Clinic business hours configuration
CREATE TABLE IF NOT EXISTS business_hours (
    id TEXT PRIMARY KEY DEFAULT 'default',
    timezone TEXT DEFAULT 'America/Sao_Paulo',
    start_time TEXT DEFAULT '08:00',
    end_time TEXT DEFAULT '18:00',
    weekdays TEXT DEFAULT '1,2,3,4,5', -- Monday to Friday
    breaks JSONB DEFAULT '[]', -- Array of {start, end} time ranges
    holidays JSONB DEFAULT '[]', -- Array of holiday dates
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default business hours
INSERT INTO business_hours (id) VALUES ('default')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- USEFUL FUNCTIONS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
DO $$
BEGIN
    -- Skip if trigger already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_contacts_updated_at'
    ) THEN
        CREATE TRIGGER update_contacts_updated_at
            BEFORE UPDATE ON contacts
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_conversations_updated_at'
    ) THEN
        CREATE TRIGGER update_conversations_updated_at
            BEFORE UPDATE ON conversations
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_appointments_updated_at'
    ) THEN
        CREATE TRIGGER update_appointments_updated_at
            BEFORE UPDATE ON appointments
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_payments_updated_at'
    ) THEN
        CREATE TRIGGER update_payments_updated_at
            BEFORE UPDATE ON payments
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Function: Get or create contact by phone
CREATE OR REPLACE FUNCTION get_or_create_contact(phone_e164 TEXT, full_name TEXT DEFAULT NULL)
RETURNS UUID AS $$
DECLARE
    contact_id UUID;
BEGIN
    -- Try to find existing contact
    SELECT id INTO contact_id FROM contacts WHERE phone_e164 = $1 LIMIT 1;

    -- If not found, create new
    IF contact_id IS NULL THEN
        INSERT INTO contacts (phone_e164, full_name)
        VALUES ($1, $2)
        RETURNING id INTO contact_id;
    END IF;

    RETURN contact_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if contact has future appointment
CREATE OR REPLACE FUNCTION has_future_appointment(contact_id_param UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS(
        SELECT 1 FROM appointments
        WHERE contact_id = contact_id_param
        AND status IN ('scheduled', 'confirmed')
        AND scheduled_at > NOW()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Get contact stats
CREATE OR REPLACE FUNCTION get_contact_stats(contact_id_param UUID)
RETURNS JSON AS $$
DECLARE
    stats JSON;
BEGIN
    SELECT json_build_object(
        'total_conversations', COALESCE(COUNT(DISTINCT c.id), 0),
        'total_messages', COALESCE(COUNT(m.id), 0),
        'total_appointments', COALESCE(COUNT(a.id), 0),
        'last_conversation_at', MAX(c.last_message_at),
        'last_appointment_at', MAX(a.scheduled_at)
    ) INTO stats
    FROM contacts ct
    LEFT JOIN conversations c ON c.contact_id = ct.id
    LEFT JOIN messages m ON m.conversation_id = c.id
    LEFT JOIN appointments a ON a.contact_id = ct.id
    WHERE ct.id = contact_id_param;

    RETURN stats;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on sensitive tables
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Policies: Service role can do everything
CREATE POLICY "Service role has full access to contacts"
    ON contacts FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to conversations"
    ON conversations FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to messages"
    ON messages FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to appointments"
    ON appointments FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to payments"
    ON payments FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- COMPLETED!
-- ============================================================
-- Database initialization completed successfully!
-- ============================================================
