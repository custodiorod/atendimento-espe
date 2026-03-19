-- ============================================================
-- Migration 001 — Schema inicial do sistema ESPE
-- ============================================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================
-- contacts
-- Identidade principal do paciente/lead
-- ============================================================
CREATE TABLE IF NOT EXISTS contacts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id     TEXT,
    full_name       TEXT,
    phone_e164      TEXT NOT NULL UNIQUE,
    birth_date      DATE,
    is_existing_patient BOOLEAN DEFAULT FALSE,
    first_seen_at   TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
    consent_status  TEXT DEFAULT 'pending' CHECK (consent_status IN ('pending','accepted','rejected')),
    opt_out         BOOLEAN DEFAULT FALSE,
    source          TEXT DEFAULT 'whatsapp',
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contacts_phone ON contacts (phone_e164);
CREATE INDEX idx_contacts_existing_patient ON contacts (is_existing_patient);

-- ============================================================
-- conversations
-- Estado atual da conversa
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    owner           TEXT NOT NULL DEFAULT 'ai' CHECK (owner IN ('ai','human')),
    mode            TEXT NOT NULL DEFAULT 'sdr' CHECK (mode IN ('sdr','support','finance','post_consulta')),
    status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','paused','closed')),
    paused_until    TIMESTAMPTZ,
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    last_response_at TIMESTAMPTZ,
    last_intent     TEXT,
    last_stage      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_contact ON conversations (contact_id);
CREATE INDEX idx_conversations_owner ON conversations (owner);
CREATE INDEX idx_conversations_status ON conversations (status);

-- ============================================================
-- messages
-- Todas as mensagens trocadas
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    contact_id          UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    provider_message_id TEXT UNIQUE,
    direction           TEXT NOT NULL CHECK (direction IN ('inbound','outbound')),
    message_type        TEXT DEFAULT 'text' CHECK (message_type IN ('text','image','audio','document','video','sticker','location','reaction')),
    content             TEXT,
    media_url           TEXT,
    transcribed_text    TEXT,
    trace_id            TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages (conversation_id);
CREATE INDEX idx_messages_contact ON messages (contact_id);
CREATE INDEX idx_messages_provider_id ON messages (provider_message_id);
CREATE INDEX idx_messages_created_at ON messages (created_at DESC);

-- ============================================================
-- appointments
-- Agendamentos sincronizados com Doctoralia
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id                  UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    doctoralia_appointment_id   TEXT UNIQUE,
    doctor_id                   UUID,
    scheduled_at                TIMESTAMPTZ,
    status                      TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled','confirmed','cancelled','realized','no_show')),
    is_future                   BOOLEAN GENERATED ALWAYS AS (scheduled_at > NOW()) STORED,
    was_realized                BOOLEAN DEFAULT FALSE,
    realized_at                 TIMESTAMPTZ,
    cancelled_at                TIMESTAMPTZ,
    no_show                     BOOLEAN DEFAULT FALSE,
    created_by                  TEXT DEFAULT 'ai' CHECK (created_by IN ('ai','human','sync')),
    last_synced_at              TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_appointments_contact ON appointments (contact_id);
CREATE INDEX idx_appointments_status ON appointments (status);
CREATE INDEX idx_appointments_scheduled_at ON appointments (scheduled_at);
CREATE INDEX idx_appointments_doctoralia_id ON appointments (doctoralia_appointment_id);

-- ============================================================
-- payments
-- Cobranças e pagamentos
-- ============================================================
CREATE TABLE IF NOT EXISTS payments (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id          UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    appointment_id      UUID REFERENCES appointments(id),
    provider            TEXT CHECK (provider IN ('openpix','stripe','manual')),
    external_payment_id TEXT UNIQUE,
    status              TEXT DEFAULT 'pending' CHECK (status IN ('pending','paid','expired','refunded','failed')),
    amount              NUMERIC(10,2),
    payment_method      TEXT,
    payment_link        TEXT,
    paid_at             TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_contact ON payments (contact_id);
CREATE INDEX idx_payments_status ON payments (status);

-- ============================================================
-- owners
-- Histórico de transferências de ownership
-- ============================================================
CREATE TABLE IF NOT EXISTS owners (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id  UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    owner       TEXT NOT NULL CHECK (owner IN ('ai','human')),
    changed_by  TEXT,
    reason      TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_owners_contact ON owners (contact_id);

-- ============================================================
-- crm_mirror
-- Espelho mínimo do Kommo
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_mirror (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id          UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    kommo_lead_id       TEXT UNIQUE,
    kommo_contact_id    TEXT,
    pipeline_id         TEXT,
    stage_id            TEXT,
    stage_name          TEXT,
    tags                TEXT[],
    last_synced_at      TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_crm_mirror_contact ON crm_mirror (contact_id);
CREATE INDEX idx_crm_mirror_kommo_lead ON crm_mirror (kommo_lead_id);

-- ============================================================
-- doctor_profiles
-- Base estruturada dos médicos
-- ============================================================
CREATE TABLE IF NOT EXISTS doctor_profiles (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctoralia_id           TEXT UNIQUE,
    full_name               TEXT NOT NULL,
    display_name            TEXT,
    specialty               TEXT,
    crm                     TEXT,
    bio_short               TEXT,
    bio_sales               TEXT,
    accepts_new_patients    BOOLEAN DEFAULT TRUE,
    active                  BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- doctor_rules
-- Regras operacionais dos médicos
-- ============================================================
CREATE TABLE IF NOT EXISTS doctor_rules (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id                   UUID NOT NULL REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    allows_squeeze_in           BOOLEAN DEFAULT FALSE,
    squeeze_in_requires_approval BOOLEAN DEFAULT TRUE,
    teleconsultation_available  BOOLEAN DEFAULT FALSE,
    min_patient_age             INT,
    max_patient_age             INT,
    notes                       TEXT,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- insurance_rules
-- Base estruturada de convênios
-- ============================================================
CREATE TABLE IF NOT EXISTS insurance_rules (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id           UUID NOT NULL REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    insurance_provider  TEXT NOT NULL,
    insurance_plan      TEXT,
    accepted            BOOLEAN DEFAULT TRUE,
    notes               TEXT,
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_insurance_doctor ON insurance_rules (doctor_id);
CREATE INDEX idx_insurance_provider ON insurance_rules (insurance_provider);

-- ============================================================
-- faq_entries
-- Base de conhecimento / RAG
-- ============================================================
CREATE TABLE IF NOT EXISTS faq_entries (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain              TEXT NOT NULL CHECK (domain IN ('doctors','insurance','scheduling','payments','compliance','objections','post_consulta','faq_geral','emergency','location')),
    subcategory         TEXT,
    title               TEXT NOT NULL,
    question            TEXT,
    answer              TEXT NOT NULL,
    content             TEXT,
    doctor_id           UUID REFERENCES doctor_profiles(id),
    insurance_provider  TEXT,
    active              BOOLEAN DEFAULT TRUE,
    version             INT DEFAULT 1,
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_faq_domain ON faq_entries (domain);
CREATE INDEX idx_faq_active ON faq_entries (active);
CREATE INDEX idx_faq_doctor ON faq_entries (doctor_id);

-- ============================================================
-- rag_chunks
-- Chunks vetorizados da base de conhecimento
-- ============================================================
CREATE TABLE IF NOT EXISTS rag_chunks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    faq_entry_id    UUID NOT NULL REFERENCES faq_entries(id) ON DELETE CASCADE,
    chunk_text      TEXT NOT NULL,
    embedding       vector(1536),
    domain          TEXT,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rag_chunks_faq ON rag_chunks (faq_entry_id);
CREATE INDEX idx_rag_chunks_domain ON rag_chunks (domain);
CREATE INDEX idx_rag_chunks_embedding ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- events
-- Auditoria operacional
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id      UUID REFERENCES contacts(id),
    conversation_id UUID REFERENCES conversations(id),
    event_type      TEXT NOT NULL,
    payload         JSONB DEFAULT '{}',
    trace_id        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_contact ON events (contact_id);
CREATE INDEX idx_events_type ON events (event_type);
CREATE INDEX idx_events_created_at ON events (created_at DESC);

-- ============================================================
-- sync_state
-- Controle de últimas sincronizações
-- ============================================================
CREATE TABLE IF NOT EXISTS sync_state (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service         TEXT NOT NULL UNIQUE CHECK (service IN ('kommo','doctoralia','payments','faq_rag')),
    last_synced_at  TIMESTAMPTZ,
    last_cursor     TEXT,
    status          TEXT DEFAULT 'idle' CHECK (status IN ('idle','running','error')),
    error_message   TEXT,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO sync_state (service) VALUES
    ('kommo'), ('doctoralia'), ('payments'), ('faq_rag')
ON CONFLICT (service) DO NOTHING;

-- ============================================================
-- feature_flags
-- Liga/desliga funcionalidades sem redeploy
-- ============================================================
CREATE TABLE IF NOT EXISTS feature_flags (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL UNIQUE,
    enabled     BOOLEAN DEFAULT FALSE,
    description TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO feature_flags (name, enabled, description) VALUES
    ('ai_after_hours',       TRUE,  'IA responde fora do horário comercial'),
    ('squeeze_in',           FALSE, 'Permite encaixes na agenda'),
    ('auto_pix',             FALSE, 'Envio automático de link de pagamento Pix'),
    ('auto_followup',        FALSE, 'Follow-up automático após consulta'),
    ('auto_reactivation',    FALSE, 'Recaptação automática de inativos'),
    ('teleconsultation',     FALSE, 'Atendimento por teleconsulta disponível')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- business_hours
-- Horário comercial da clínica
-- ============================================================
CREATE TABLE IF NOT EXISTS business_hours (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=domingo, 6=sábado
    open_time   TIME NOT NULL,
    close_time  TIME NOT NULL,
    active      BOOLEAN DEFAULT TRUE,
    UNIQUE (day_of_week)
);

INSERT INTO business_hours (day_of_week, open_time, close_time) VALUES
    (1, '08:00', '18:00'), -- segunda
    (2, '08:00', '18:00'), -- terça
    (3, '08:00', '18:00'), -- quarta
    (4, '08:00', '18:00'), -- quinta
    (5, '08:00', '17:00')  -- sexta
ON CONFLICT (day_of_week) DO NOTHING;

-- ============================================================
-- message_templates
-- Templates de mensagens padronizadas
-- ============================================================
CREATE TABLE IF NOT EXISTS message_templates (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL UNIQUE,
    content     TEXT NOT NULL,
    variables   TEXT[],
    active      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- doctor_aliases
-- Aliases de nomes dos médicos para reconhecimento pela IA
-- ============================================================
CREATE TABLE IF NOT EXISTS doctor_aliases (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id   UUID NOT NULL REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_doctor_aliases_doctor ON doctor_aliases (doctor_id);

-- ============================================================
-- Função de updated_at automático
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger em todas as tabelas com updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'contacts','conversations','payments','appointments',
        'crm_mirror','doctor_profiles','doctor_rules','insurance_rules',
        'faq_entries','sync_state','feature_flags','message_templates'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();', t
        );
    END LOOP;
END;
$$;
