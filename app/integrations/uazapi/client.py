"""
Cliente Uazapi — envio e recebimento de mensagens WhatsApp.

Instância: Secretaria (espemed)
Status: connected
"""

import os
import httpx
from typing import Optional

UAZAPI_BASE_URL = os.environ.get("UAZAPI_BASE_URL", "https://espemed.uazapi.com")
UAZAPI_TOKEN = os.environ.get("UAZAPI_TOKEN", "bf7113b8-f5d6-476e-a49b-db4c0e05b041")


def _headers() -> dict:
    return {"token": UAZAPI_TOKEN, "Content-Type": "application/json"}


async def get_status() -> dict:
    """Retorna o status da instância WhatsApp."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{UAZAPI_BASE_URL}/instance/status",
            headers=_headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()


async def send_text(to: str, message: str) -> dict:
    """
    Envia mensagem de texto para um número WhatsApp.

    Args:
        to: Número no formato E.164 sem '+' (ex: 5521999999999)
        message: Texto da mensagem
    """
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{UAZAPI_BASE_URL}/send/text",
            headers=_headers(),
            json={"number": to, "text": message},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()


async def send_image(to: str, image_url: str, caption: Optional[str] = None) -> dict:
    """Envia imagem para um número WhatsApp."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{UAZAPI_BASE_URL}/send/image",
            headers=_headers(),
            json={"number": to, "url": image_url, "caption": caption or ""},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()


async def send_audio(to: str, audio_url: str) -> dict:
    """Envia áudio (PTT) para um número WhatsApp."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{UAZAPI_BASE_URL}/send/audio",
            headers=_headers(),
            json={"number": to, "url": audio_url},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()


async def send_document(to: str, document_url: str, filename: str) -> dict:
    """Envia documento para um número WhatsApp."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{UAZAPI_BASE_URL}/send/document",
            headers=_headers(),
            json={"number": to, "url": document_url, "filename": filename},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()


async def set_webhook(webhook_url: str) -> dict:
    """Configura o webhook de recebimento de mensagens."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{UAZAPI_BASE_URL}/instance/webhook",
            headers=_headers(),
            json={"webhook": webhook_url, "webhookEnabled": True},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()


async def get_webhook() -> dict:
    """Retorna a configuração atual do webhook."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{UAZAPI_BASE_URL}/instance/status",
            headers=_headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
