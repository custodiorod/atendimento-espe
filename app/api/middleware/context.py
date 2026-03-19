"""
Middleware de contexto — gera trace_id, conversation_id, resolve contact_id,
determina owner, valida horário comercial e idempotência.
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.trace_id = str(uuid.uuid4())
        # TODO: resolver contact_id, conversation_id, owner, horário comercial
        response = await call_next(request)
        response.headers["X-Trace-Id"] = request.state.trace_id
        return response
