"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================
    # APP
    # =========================
    APP_ENV: Literal["development", "staging", "production"] = "production"
    APP_NAME: str = "clinic-ai"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "America/Sao_Paulo"
    CLINIC_NAME: str = "ESPE"

    # =========================
    # SECURITY / INTERNAL
    # =========================
    WEBHOOK_SECRET: str = Field(default="", min_length=1)
    INTERNAL_API_TOKEN: str = Field(default="", min_length=1)
    JWT_SECRET_KEY: str = Field(default="", min_length=1)
    ENCRYPTION_SECRET_KEY: str = Field(default="", min_length=1)

    # =========================
    # BUSINESS HOURS / OWNER
    # =========================
    ENABLE_AI_AFTER_HOURS: bool = True
    BUSINESS_HOURS_TIMEZONE: str = "America/Sao_Paulo"
    BUSINESS_HOURS_START: str = "08:00"
    BUSINESS_HOURS_END: str = "18:00"
    BUSINESS_HOURS_WEEKDAYS: str = "1,2,3,4,5"
    DEFAULT_OWNER_AFTER_HOURS: str = "ai"
    DEFAULT_OWNER_BUSINESS_HOURS: str = "human"
    DEFAULT_PAUSE_MINUTES: int = 480

    # =========================
    # API URLS
    # =========================
    API_BASE_URL: str = ""
    PUBLIC_WEBHOOK_BASE_URL: str = ""
    HEALTHCHECK_PATH: str = "/health"

    # =========================
    # SUPABASE
    # =========================
    SUPABASE_URL: str = Field(default="", min_length=1)
    SUPABASE_ANON_KEY: str = Field(default="", min_length=1)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="", min_length=1)
    SUPABASE_DB_URL: str = ""
    SUPABASE_SCHEMA: str = "public"

    # =========================
    # OPENROUTER / LLM
    # =========================
    OPENROUTER_API_KEY: str = Field(default="", min_length=1)
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = Field(default="", min_length=1)
    FALLBACK_MODEL: str = ""
    ROUTER_MODEL: str = ""
    EXTRACTION_MODEL: str = ""
    RAG_RESPONSE_MODEL: str = ""
    TEMPERATURE_DEFAULT: float = 0.2
    MAX_TOKENS_DEFAULT: int = 1200

    # =========================
    # LANGFUSE
    # =========================
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_ENABLED: bool = True

    # =========================
    # UAZAPI / WHATSAPP
    # =========================
    UAZAPI_BASE_URL: str = Field(default="", min_length=1)
    UAZAPI_TOKEN: str = Field(default="", min_length=1)
    UAZAPI_INSTANCE: str = Field(default="", min_length=1)
    UAZAPI_NUMBER: str = ""
    WHATSAPP_GROUP_NOTIFICATIONS_ID: str = ""
    WHATSAPP_SEND_TYPING: bool = False

    # =========================
    # DOCTORALIA
    # =========================
    DOCTORALIA_BASE_URL: str = ""
    DOCTORALIA_API_KEY: str = ""
    DOCTORALIA_CLIENT_ID: str = ""
    DOCTORALIA_CLIENT_SECRET: str = ""
    DOCTORALIA_WEBHOOK_SECRET: str = ""

    # =========================
    # KOMMO CRM
    # =========================
    KOMMO_BASE_URL: str = ""
    KOMMO_ACCESS_TOKEN: str = ""
    KOMMO_REFRESH_TOKEN: str = ""
    KOMMO_CLIENT_ID: str = ""
    KOMMO_CLIENT_SECRET: str = ""
    KOMMO_REDIRECT_URI: str = ""
    KOMMO_PIPELINE_ID: str = ""
    KOMMO_STAGE_NEW: str = ""
    KOMMO_STAGE_IN_SERVICE: str = ""
    KOMMO_STAGE_SCHEDULED: str = ""
    KOMMO_STAGE_CONFIRMED: str = ""
    KOMMO_STAGE_REALIZED: str = ""
    KOMMO_STAGE_NO_SHOW: str = ""
    KOMMO_STAGE_REACTIVATION: str = ""
    KOMMO_CUSTOM_FIELD_CONTACT_ID: str = ""
    KOMMO_CUSTOM_FIELD_OWNER_MODE: str = ""

    # =========================
    # PAYMENTS
    # =========================
    OPENPIX_API_KEY: str = ""
    OPENPIX_BASE_URL: str = ""
    OPENPIX_WEBHOOK_SECRET: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    ENABLE_PIX: bool = True
    ENABLE_STRIPE: bool = False
    PAYMENT_PROVIDER_DEFAULT: str = "openpix"

    # =========================
    # RABBITMQ
    # =========================
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    RABBITMQ_DEFAULT_QUEUE: str = "realtime"

    # =========================
    # REDIS
    # =========================
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_LOCK_DB: int = 1
    REDIS_RATE_LIMIT_DB: int = 2
    REDIS_CACHE_TTL_SECONDS: int = 300

    # =========================
    # CELERY
    # =========================
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/3"
    CELERY_TASK_DEFAULT_QUEUE: str = "realtime"
    CELERY_WORKER_CONCURRENCY: int = 2
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_TASK_SOFT_TIME_LIMIT: int = 240

    # =========================
    # KESTRA
    # =========================
    KESTRA_BASE_URL: str = ""
    KESTRA_API_TOKEN: str = ""
    KESTRA_NAMESPACE: str = "clinic_ai"
    KESTRA_ENABLED: bool = True

    # =========================
    # MEDIA / OCR / STT
    # =========================
    ENABLE_AUDIO_TRANSCRIPTION: bool = True
    ENABLE_IMAGE_OCR: bool = True
    ENABLE_DOCUMENT_PARSE: bool = True
    STT_PROVIDER: str = ""
    STT_API_KEY: str = ""
    OCR_PROVIDER: str = ""
    OCR_API_KEY: str = ""
    VISION_PROVIDER: str = ""
    VISION_API_KEY: str = ""
    MAX_MEDIA_FILE_MB: int = 20

    # =========================
    # RAG / FAQ
    # =========================
    ENABLE_RAG: bool = True
    EMBEDDING_PROVIDER: str = ""
    EMBEDDING_MODEL: str = ""
    VECTOR_STORE: str = "supabase"
    FAQ_REINDEX_CRON: str = "0 3 * * *"
    RAG_TOP_K: int = 5
    RAG_MIN_SCORE: float = 0.75

    # =========================
    # MONITORING / ALERTS
    # =========================
    SLACK_WEBHOOK_URL: str = ""
    SLACK_ALERTS_CHANNEL: str = ""
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.2

    # =========================
    # RATE LIMIT / ANTI-DUPLICATION
    # =========================
    IDEMPOTENCY_TTL_SECONDS: int = 3600
    WHATSAPP_RATE_LIMIT_PER_MINUTE: int = 20
    WHATSAPP_RATE_LIMIT_PER_HOUR: int = 300
    CONTACT_MESSAGE_COOLDOWN_SECONDS: int = 3

    # =========================
    # FEATURE FLAGS
    # =========================
    ENABLE_REACTIVATION: bool = True
    ENABLE_REMINDERS: bool = True
    ENABLE_POST_CONSULTA: bool = True
    ENABLE_INSURANCE_RAG: bool = True
    ENABLE_HUMAN_HANDOFF: bool = True
    ENABLE_SQUEEZE_IN_FLOW: bool = True
    ENABLE_EMERGENCY_DETECTOR: bool = True
    ENABLE_KOMMO_SYNC: bool = True
    ENABLE_DOCTORALIA_SYNC: bool = True

    # =========================
    # IMPORT / LEGACY DATA
    # =========================
    HIDOCTOR_IMPORT_ENABLED: bool = True
    HIDOCTOR_IMPORT_SOURCE: str = ""
    HIDOCTOR_IMPORT_SCHEDULE: str = "0 2 * * *"

    # =========================
    # OPTIONAL STORAGE
    # =========================
    STORAGE_PROVIDER: str = ""
    S3_BUCKET: str = ""
    S3_REGION: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""

    # =========================
    # TEST / DEV
    # =========================
    DEBUG: bool = False
    MOCK_DOCTORALIA: bool = False
    MOCK_KOMMO: bool = False
    MOCK_PAYMENTS: bool = False
    MOCK_UAZAPI: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
