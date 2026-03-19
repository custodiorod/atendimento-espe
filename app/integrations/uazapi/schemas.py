"""
Schemas do payload de webhook da Uazapi.
"""

from typing import Optional, Literal
from pydantic import BaseModel


class UazapiMessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str


class UazapiMessage(BaseModel):
    key: UazapiMessageKey
    pushName: Optional[str] = None
    message: Optional[dict] = None
    messageType: Optional[str] = None
    messageTimestamp: Optional[int] = None
    instanceId: Optional[str] = None
    source: Optional[str] = None


class UazapiWebhookPayload(BaseModel):
    event: str
    instance: Optional[str] = None
    data: Optional[dict] = None

    def get_phone(self) -> Optional[str]:
        """Extrai o número de telefone do remetente."""
        try:
            remote_jid = self.data["key"]["remoteJid"]
            return remote_jid.split("@")[0]
        except (KeyError, TypeError):
            return None

    def get_text(self) -> Optional[str]:
        """Extrai o texto da mensagem."""
        try:
            msg = self.data.get("message", {})
            return msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text") or None
        except (AttributeError, TypeError):
            return None

    def get_message_type(self) -> Optional[str]:
        """Retorna o tipo da mensagem (text, image, audio, document, etc)."""
        try:
            return self.data.get("messageType")
        except AttributeError:
            return None

    def is_from_me(self) -> bool:
        """Retorna True se a mensagem foi enviada pela própria instância."""
        try:
            return self.data["key"]["fromMe"]
        except (KeyError, TypeError):
            return False
