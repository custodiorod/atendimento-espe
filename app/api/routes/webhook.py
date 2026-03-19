from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    # TODO: normalizar payload, validar idempotência, chamar orchestrator
    pass


@router.post("/webhook/payments")
async def payments_webhook(request: Request):
    # TODO: processar webhook de pagamento
    pass


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/internal/reprocess")
async def reprocess(request: Request):
    # TODO: reprocessar mensagem manualmente
    pass


@router.post("/internal/send-message")
async def send_message(request: Request):
    # TODO: enviar mensagem via Uazapi
    pass
