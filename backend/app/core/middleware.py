"""
TraceData Backend — Request ID Middleware.

Cross-cutting concern: assigns a unique ID to every HTTP request so that
all log lines emitted during that request share the same correlation ID.

Why this matters:
    Without correlation IDs, debugging a production error requires reading
    ALL log lines and mentally joining them by timestamp — very painful.

    With correlation IDs:
        grep "a3f9b1c2" logs/backend.log
        → shows every log line (DB query, agent call, response) for that one request.

How it works:
    1. Client sends a request (optionally with X-Request-ID header).
    2. This middleware reads the header (or generates a UUID if missing).
    3. The ID is stored in a ContextVar — a thread/coroutine-local variable.
    4. The logging Filter (in core/logging.py) reads the ContextVar and
       injects request_id into every log record for the duration of the request.
    5. The ID is also echoed back in the response via X-Request-ID header,
       so the frontend/client can reference it when reporting issues.
"""

import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging import reset_request_id, set_request_id

# ── ContextVar ────────────────────────────────────────────────────────────────
# DEPRECATED: The ContextVar has been moved to `core.logging` so it can be 
# shared between the API and the Agents.


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that assigns a unique ID to every incoming HTTP request.

    Reads from:  X-Request-ID header (if sent by client or upstream proxy)
    Generates:   UUID4 if the header is absent
    Writes to:   ContextVar (for logging) + X-Request-ID response header

    This middleware runs BEFORE the route handler, so the request_id is
    available in all log lines emitted by the handler and its dependencies.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: object) -> Response:
        # Honour an incoming request ID from a gateway/load balancer
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())

        # Store in ContextVar — visible to all log lines in this request
        token = set_request_id(request_id)
        try:
            response: Response = await call_next(request)  # type: ignore[operator]
        finally:
            # Reset the ContextVar after the request completes (good hygiene)
            reset_request_id(token)

        # Echo the ID back so clients/frontend can reference it
        response.headers[self.header_name] = request_id
        return response
