"""
Estado do LangGraph — define o contexto de cada execução do grafo.
"""

from typing import Optional, Literal
from pydantic import BaseModel


class ConversationState(BaseModel):
    trace_id: str
    contact_id: str
    conversation_id: str
    clinic_id: Optional[str] = None
    channel: str = "whatsapp"
    owner: Literal["ai", "human"] = "ai"
    mode: Literal["sdr", "support", "finance", "post_consulta"] = "sdr"
    message_type: Optional[str] = None
    doctor_id: Optional[str] = None
    appointment_id: Optional[str] = None
    kommo_lead_id: Optional[str] = None
    last_intent: Optional[str] = None
    last_stage: Optional[str] = None
    messages: list = []
