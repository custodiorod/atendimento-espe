"""
Sistema de ownership — controla se a conversa está com AI ou HUMANO.
Gerencia pause/resume e transições de owner.
"""

from typing import Literal


OwnerType = Literal["ai", "human"]


def should_handoff_to_human(state) -> bool:
    """Decide se deve transferir para humano."""
    # TODO: implementar lógica de handoff
    return False


def is_business_hours() -> bool:
    """Verifica se está dentro do horário comercial."""
    # TODO: consultar tabela business_hours no Supabase
    return True
