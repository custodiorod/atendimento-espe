"""Worker: transcrição de áudio e OCR de imagens."""

from app.execution.workers.celery_app import celery_app


@celery_app.task(queue="media", bind=True, max_retries=3)
def transcribe_audio(self, media_url: str, contact_id: str, message_id: str):
    """Transcreve áudio recebido via WhatsApp."""
    # TODO: integrar com Whisper / OpenAI Audio
    pass


@celery_app.task(queue="media", bind=True, max_retries=3)
def process_image_ocr(self, media_url: str, contact_id: str, message_id: str):
    """Extrai texto de imagens (documentos, laudos, etc)."""
    # TODO: integrar com OCR
    pass
