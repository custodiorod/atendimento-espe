"""Worker: sincronização com Kommo CRM."""

from app.execution.workers.celery_app import celery_app


@celery_app.task(queue="sync", bind=True, max_retries=3)
def sync_lead_to_kommo(self, contact_id: str, event_type: str, payload: dict):
    """Sincroniza lead/evento para o Kommo."""
    # TODO: integrar com Kommo API
    pass
