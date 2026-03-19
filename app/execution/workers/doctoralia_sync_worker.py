"""Worker: sincronização com Doctoralia."""

from app.execution.workers.celery_app import celery_app


@celery_app.task(queue="sync", bind=True, max_retries=3)
def sync_appointment_from_doctoralia(self, appointment_id: str):
    """Sincroniza agendamento do Doctoralia para o Supabase."""
    # TODO: integrar com Doctoralia API
    pass
