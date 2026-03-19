# Arquitetura Completa Atualizada — Sistema de Atendimento com IA para Clínica

## Objetivo

Este documento consolida a arquitetura completa do sistema, com foco em:

- atendimento via WhatsApp fora do horário comercial
- agendamento via Doctoralia
- operação humana em paralelo
- CRM comercial via Kommo
- Supabase como fonte da verdade operacional
- Redis + RabbitMQ + Celery + Kestra
- RAG / FAQ centralizado no Supabase
- observabilidade, segurança, compliance e governança

Este documento também define:

- estrutura de pastas
- responsabilidades de cada serviço
- tabelas principais
- variáveis de ambiente
- fluxos centrais
- regras de negócio importantes
- pontos adicionais que precisam existir no sistema

---

# PRINCÍPIO CENTRAL

> **Supabase é a verdade absoluta operacional do sistema.**

Isso significa:

- Kommo não é a verdade
- Doctoralia não é a verdade
- Uazapi não é a verdade
- Slack não é a verdade
- Langfuse não é a verdade

Todos esses sistemas são:
- canais
- interfaces
- fontes de evento
- sistemas auxiliares
- espelhos

O Supabase consolida:

- estado
- histórico
- ownership
- tags
- appointments
- pagamentos
- espelhamento do CRM
- base estruturada de médicos
- base estruturada de convênios
- FAQ/RAG
- auditoria de negócio

---

# VISÃO GERAL DA ARQUITETURA

```text
Paciente
  ↓
WhatsApp
  ↓
Uazapi
  ↓
FastAPI (Webhook/API)
  ↓
Middleware (contexto, trace, owner, idempotência)
  ↓
LangGraph / Orchestrator
  ↓
Supabase (fonte da verdade)

Assíncrono:
FastAPI → RabbitMQ → Celery Workers → Redis → Supabase / Integrações

Agendado:
Kestra → Tasks / API interna → Supabase → Doctoralia / Kommo / WhatsApp
```

---

# CAMADAS DO SISTEMA

## 1. Canal de Entrada

### Componentes
- WhatsApp
- Uazapi

### Responsabilidades
- receber mensagens
- enviar mensagens
- receber mídia
- encaminhar payload para API

---

## 2. API Principal (FastAPI)

### Responsabilidades
- receber webhook do WhatsApp
- receber webhook de pagamentos
- receber webhooks auxiliares
- normalizar payload
- criar contexto da conversa
- validar idempotência
- decidir owner AI/HUMANO
- chamar LangGraph
- salvar tudo no Supabase
- disparar jobs assíncronos
- responder rapidamente

### Endpoints mínimos
- `POST /webhook/whatsapp`
- `POST /webhook/payments`
- `GET /health`
- `POST /internal/reprocess`
- `POST /internal/send-message`

---

## 3. Middleware / Context Layer

### É obrigatório
Essa camada é essencial e deve existir no projeto.

### Responsabilidades
- gerar `trace_id`
- gerar `conversation_id`
- resolver `contact_id`
- determinar `owner`
- validar horário comercial
- validar idempotência
- adicionar metadata à execução
- registrar contexto no Langfuse

### Metadata importante
- `contact_id`
- `conversation_id`
- `clinic_id`
- `channel`
- `mode`
- `owner`
- `message_type`
- `doctor_id`
- `appointment_id`
- `kommo_lead_id`

---

## 4. Orquestrador (LangGraph)

### Responsabilidades
- classificar intenção
- decidir fluxo (SDR / suporte / financeiro / pós-consulta)
- consultar skills e prompts
- chamar tools
- decidir handoff humano
- disparar fluxos de emergência
- conduzir o fluxo comercial

### Fluxos centrais
- agendamento
- convênio
- financeiro
- pós-consulta
- emergência
- encaixe
- reativação

---

## 5. Supabase (Fonte da Verdade)

## Função
Armazenar e consolidar toda a operação do sistema.

---

# TABELAS PRINCIPAIS DO SUPABASE

## contacts
Armazena a identidade principal do paciente/lead.

### Campos sugeridos
- `id`
- `external_id`
- `full_name`
- `phone_e164`
- `birth_date` *(opcional)*
- `is_existing_patient` ✅
- `first_seen_at`
- `last_seen_at`
- `consent_status`
- `opt_out`
- `source`
- `notes`

### Importância
Aqui você identifica:
- se o cliente já é antigo
- se é paciente novo
- se já falou antes
- se pode receber mensagens

---

## conversations
Armazena o estado atual da conversa.

### Campos
- `id`
- `contact_id`
- `owner` (`ai` / `human`)
- `mode` (`sdr`, `support`, `finance`, `post_consulta`)
- `status`
- `paused_until`
- `last_message_at`
- `last_response_at`
- `last_intent`
- `last_stage`

---

## messages
Armazena todas as mensagens.

### Campos
- `id`
- `conversation_id`
- `contact_id`
- `provider_message_id`
- `direction`
- `message_type`
- `content`
- `media_url`
- `transcribed_text`
- `created_at`
- `trace_id`

---

## appointments
Armazena agendamentos sincronizados.

### Campos
- `id`
- `contact_id`
- `doctoralia_appointment_id`
- `doctor_id`
- `scheduled_at`
- `status`
- `is_future` ✅
- `was_realized` ✅
- `realized_at`
- `cancelled_at`
- `no_show`
- `created_by`
- `last_synced_at`

### Importância
Aqui você identifica:
- se o paciente já tem consulta marcada ✅
- se já compareceu
- se faltou
- se está em fluxo pós-consulta

---

## payments
Armazena cobranças e pagamentos.

### Campos
- `id`
- `contact_id`
- `appointment_id`
- `provider`
- `external_payment_id`
- `status`
- `amount`
- `payment_method`
- `payment_link`
- `paid_at`
- `expires_at`

---

## owners
Pode ser embutido em conversations, mas pode existir separado se quiser histórico.

### Campos
- `id`
- `contact_id`
- `owner`
- `changed_by`
- `reason`
- `created_at`

---

## crm_mirror
Espelho mínimo do Kommo.

### Campos
- `id`
- `contact_id`
- `kommo_lead_id`
- `kommo_contact_id`
- `pipeline_id`
- `stage_id`
- `stage_name`
- `tags`
- `last_synced_at`

---

## doctor_profiles
Base estruturada dos médicos.

### Campos
- `id`
- `doctoralia_id`
- `full_name`
- `display_name`
- `specialty`
- `crm`
- `bio_short`
- `bio_sales`
- `accepts_new_patients`
- `active`

---

## doctor_rules
Regras operacionais dos médicos.

### Campos
- `id`
- `doctor_id`
- `allows_squeeze_in`
- `squeeze_in_requires_approval`
- `teleconsultation_available`
- `min_patient_age`
- `max_patient_age`
- `notes`

---

## insurance_rules
Base estruturada de convênios.

### Campos
- `id`
- `doctor_id`
- `insurance_provider`
- `insurance_plan`
- `accepted`
- `notes`
- `updated_at`

---

## faq_entries
Base de conhecimento / RAG no Supabase. ✅

### Campos
- `id`
- `domain`
- `subcategory`
- `title`
- `question`
- `answer`
- `content`
- `doctor_id` *(opcional)*
- `insurance_provider` *(opcional)*
- `active`
- `version`
- `updated_at`

### Domínios sugeridos
- `doctors`
- `insurance`
- `scheduling`
- `payments`
- `compliance`
- `objections`
- `post_consulta`
- `faq_geral`

### Importância
Isso permite:
- FAQ centralizado no Supabase ✅
- versionamento
- filtro por domínio
- filtro por médico
- filtro por convênio

---

## rag_chunks
Chunks vetorizados da base.

### Campos
- `id`
- `faq_entry_id`
- `chunk_text`
- `embedding`
- `domain`
- `metadata`
- `created_at`

---

## events
Auditoria operacional.

### Campos
- `id`
- `contact_id`
- `conversation_id`
- `event_type`
- `payload`
- `trace_id`
- `created_at`

### Exemplos de evento
- `appointment_created`
- `payment_confirmed`
- `owner_changed`
- `human_handoff`
- `insurance_not_supported`
- `emergency_detected`

---

# REDIS — PAPEL NO SISTEMA

Redis deve existir mesmo usando Supabase.

## Redis não é a verdade
Redis é infra operacional.

## Use Redis para
- lock por contato
- rate limit de envio
- cooldown de mensagens
- cache leve
- controle de concorrência

### Casos práticos
- evitar que duas mensagens do mesmo paciente rodem em paralelo
- evitar respostas duplicadas
- limitar envios para não tomar bloqueio do WhatsApp

---

# RABBITMQ — PAPEL NO SISTEMA

RabbitMQ é o broker principal da fila.

## Use para
- enfileirar tarefas para workers
- separar filas por tipo
- retry
- priorização de jobs

### Filas sugeridas
- `realtime`
- `media`
- `sync`
- `reminders`
- `reactivation`

---

# CELERY — PAPEL NO SISTEMA

Celery é o executor assíncrono.

## Use para
- transcrição de áudio
- OCR
- reconciliação de pagamentos
- sync de CRM
- sync de Doctoralia
- envio agendado
- jobs demorados

---

# KESTRA — PAPEL NO SISTEMA

Kestra é o orquestrador de jobs agendados e workflows batch.

## Use para
- lembrete D-1
- lembrete D-0
- recaptação 30/60/90 dias
- sync periódico Doctoralia → Supabase → Kommo
- reconciliação de pagamentos
- importações
- atualizações periódicas de base de conhecimento

## Não usar para
- webhook principal do WhatsApp
- lógica síncrona do agente
- resposta em tempo real

---

# LANGFUSE — PAPEL NO SISTEMA

## Use para
- tracing do LangGraph
- spans por node
- custos de IA
- observabilidade
- prompt management

## Centralizar no Langfuse
- prompts do router
- prompts de classificação
- prompts de resposta por modo
- prompts de extração estruturada

## Não centralizar no Langfuse
- base inteira de FAQ
- convênios completos
- playbooks gigantes
- lógica de negócio

---

# KOMMO — PAPEL NO SISTEMA

Kommo é a camada comercial visual.

## Use para
- pipeline visual
- operação humana
- acompanhamento do lead
- tags
- Kanban

## O que sincronizar
- lead criado
- estágio
- tags
- owner
- consulta agendada
- consulta realizada
- no-show
- follow-up

## Regra
Kommo é espelho comercial.
Supabase continua sendo a verdade.

---

# DOCTORALIA — PAPEL NO SISTEMA

Doctoralia é a agenda externa oficial.

## Use para
- checar disponibilidade
- agendar
- cancelar
- remarcar
- consultar status da consulta

## O que sincronizar no Supabase
- appointment_id
- data/hora
- status
- realizada / no-show
- sync com Kommo

---

# IDENTIFICAÇÃO DE CLIENTE ANTIGO E CONSULTA MARCADA

## Cliente antigo
Determinar por:
- existência em `contacts`
- `is_existing_patient = true`
- histórico de `appointments`
- importação prévia do HiDoctor / Kommo

## Consulta marcada
Determinar por:
- `appointments.status in ('scheduled', 'confirmed')`
- `scheduled_at > now()`
- `is_future = true`

## Regras importantes
Se já for paciente antigo:
- tom pode ser diferente
- pode usar follow-up de retorno
- pode acionar pós-consulta

Se já tiver consulta marcada:
- não oferecer novo agendamento imediatamente
- oferecer confirmação, remarcação, suporte ou informações

---

# FAQ / RAG NO SUPABASE

## Estrutura recomendada
O FAQ deve ficar no Supabase de forma estruturada.

## Domínios de FAQ
- médicos
- convênios
- agendamento
- encaixe
- emergência
- pagamento
- localização
- horário
- remarcação
- objeções
- pós-consulta

## Estratégia de uso
1. ferramenta estruturada consulta tabelas críticas
2. se precisar de resposta contextual → RAG via `faq_entries + rag_chunks`
3. se ainda for ambíguo → handoff humano

## Importante
- decisões críticas não podem depender apenas do RAG
- convênio, agenda e regra operacional devem vir de tabela estruturada

---

# ESTRUTURA DE PASTAS FINAL

```text
app/
  api/
    routes/
    middleware/
    schemas/

  orchestrator/
    graph.py
    router.py
    state.py
    ownership.py
    idempotency.py
    handlers/

  directives/
    sdr_flow.md
    support_flow.md
    finance_flow.md
    post_consulta_flow.md
    emergency_protocol.md
    compliance_rules.md

  skills/
    humanizacao.md
    autoridade_medica.md
    objection_price.md
    objection_convenio.md
    scheduling_pitch.md
    followup.md

  prompts/
    local_fallbacks/
    schemas/

  tools/
    appointments.py
    insurance.py
    crm.py
    payments.py
    whatsapp.py
    notifications.py
    rag.py
    contacts.py
    doctors.py

  integrations/
    uazapi/
    doctoralia/
    kommo/
    payments/
    media/
    slack/
    sentry/
    openrouter/

  execution/
    workers/
      celery_app.py
      media_worker.py
      crm_sync_worker.py
      doctoralia_sync_worker.py
      payments_worker.py

    tasks/
      reminder_task.py
      reactivation_task.py
      doctoralia_sync_task.py
      payments_reconcile_task.py
      faq_reindex_task.py

    queue/
      rabbitmq.py
      redis_lock.py
      rate_limit.py

  database/
    models/
    repositories/
    supabase.py
    migrations/

  rag/
    ingest/
    retrieval/
    schemas/

  monitoring/
    middleware.py
    tracing.py
    langfuse.py
    alerts.py
    metrics.py

  utils/
    ids.py
    phone.py
    validators.py
    dates.py
    strings.py

kestra/
  flows/
    reminders_d1.yaml
    reminders_d0.yaml
    reactivation_30d.yaml
    reactivation_60d.yaml
    reactivation_90d.yaml
    doctoralia_sync.yaml
    payments_reconcile.yaml
    faq_reindex.yaml

scripts/
tests/
docs/
```

---

# VARIÁVEIS DE AMBIENTE (.env)

## App
```env
APP_ENV=production
APP_NAME=clinic-ai
APP_PORT=8000
LOG_LEVEL=INFO
TIMEZONE=America/Sao_Paulo
```

## Segurança
```env
WEBHOOK_SECRET=...
INTERNAL_API_TOKEN=...
```

## Supabase
```env
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_DB_URL=...
```

## OpenRouter
```env
OPENROUTER_API_KEY=...
DEFAULT_MODEL=...
FALLBACK_MODEL=...
```

## Uazapi
```env
UAZAPI_BASE_URL=...
UAZAPI_TOKEN=...
UAZAPI_INSTANCE=...
```

## Doctoralia
```env
DOCTORALIA_BASE_URL=...
DOCTORALIA_API_KEY=...
DOCTORALIA_CLIENT_ID=...
DOCTORALIA_CLIENT_SECRET=...
```

## Kommo
```env
KOMMO_BASE_URL=...
KOMMO_ACCESS_TOKEN=...
KOMMO_PIPELINE_ID=...
KOMMO_STAGE_NEW=...
KOMMO_STAGE_SCHEDULED=...
KOMMO_STAGE_REALIZED=...
KOMMO_STAGE_NO_SHOW=...
```

## Pagamentos
```env
OPENPIX_API_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
```

## RabbitMQ
```env
RABBITMQ_URL=amqp://user:password@rabbitmq:5672/
```

## Redis
```env
REDIS_URL=redis://redis:6379/0
```

## Slack
```env
SLACK_WEBHOOK_URL=...
```

## Sentry
```env
SENTRY_DSN=...
```

## Langfuse
```env
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=...
```

---

# FUNCIONALIDADES ESSENCIAIS QUE PRECISAM EXISTIR

## 1. Sistema de ownership
- AI ou HUMANO
- pause/resume
- horário comercial x não comercial

## 2. Idempotência
- não responder duas vezes
- não criar agendamento duplicado
- não duplicar update no Kommo

## 3. Rate limiting
- proteger WhatsApp
- controlar volume por contato

## 4. Consentimento / LGPD
- opt-in
- opt-out
- bloqueio de envios futuros

## 5. Emergência
- classificador determinístico
- interrupção do fluxo comercial

## 6. Histórico operacional completo
- tudo precisa virar evento no Supabase

## 7. Reconciliação
- status de consulta
- pagamentos
- espelho de CRM

## 8. Knowledge management
- FAQ versionado
- chunks atualizáveis
- reindexação periódica

---

# O QUE MAIS VALE ADICIONAR AO SISTEMA

Além do que já falamos, eu adicionaria:

## 1. `sync_state`
Tabela para controlar últimas sincronizações:
- Kommo
- Doctoralia
- Pagamentos
- FAQ/RAG

## 2. `message_templates`
Se quiser padronizar algumas mensagens sem depender sempre de prompt

## 3. `feature_flags`
Para ligar/desligar:
- IA fora do horário
- encaixe
- envio automático de Pix
- follow-up automático
- recaptação

## 4. `audit_log`
Se quiser um log ainda mais formal por mudança relevante

## 5. `business_hours`
Tabela/config da clínica para não hardcodar horário comercial

## 6. `doctor_aliases`
Para ajudar a IA a reconhecer nomes escritos de maneiras diferentes

---

# CHECKLIST FINAL

## Banco / Supabase
- [ ] tabelas principais criadas
- [ ] FAQ estruturado criado
- [ ] chunking / embeddings planejados
- [ ] sync_state criado
- [ ] feature_flags criado

## Infra
- [ ] API
- [ ] Worker
- [ ] RabbitMQ
- [ ] Redis
- [ ] Kestra
- [ ] volumes e healthchecks

## IA
- [ ] LangGraph
- [ ] Langfuse
- [ ] prompts críticos centralizados
- [ ] middleware de tracing

## Operação
- [ ] owner system
- [ ] rate limit
- [ ] idempotência
- [ ] consentimento
- [ ] emergency detector
- [ ] sync Kommo
- [ ] sync Doctoralia

---

# RESUMO FINAL

> Supabase é o cérebro de dados e estado  
> LangGraph é o raciocínio  
> Langfuse é a observabilidade e gestão de prompts  
> Redis é o controle operacional de concorrência  
> RabbitMQ + Celery executam o trabalho assíncrono  
> Kestra agenda e orquestra rotinas  
> Kommo mostra o Kanban  
> Doctoralia é a agenda externa  
> Todo o sistema conversa através do Supabase
