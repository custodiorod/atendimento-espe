"""Worker: reconciliação de pagamentos."""

from app.execution.workers.celery_app import celery_app


@celery_app.task(queue="sync", bind=True, max_retries=3)
def reconcile_payment(self, payment_id: str):
    """Reconcilia status de pagamento."""
    # TODO: integrar com OpenPix / Stripe
    pass
