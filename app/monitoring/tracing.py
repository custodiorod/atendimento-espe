"""
Tracing com Langfuse — observabilidade do LangGraph.
"""

import os
from langfuse import Langfuse

_langfuse: Langfuse | None = None


def get_langfuse() -> Langfuse:
    global _langfuse
    if _langfuse is None:
        _langfuse = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
    return _langfuse


def create_trace(trace_id: str, name: str, metadata: dict = {}):
    """Cria um trace no Langfuse."""
    lf = get_langfuse()
    return lf.trace(id=trace_id, name=name, metadata=metadata)
