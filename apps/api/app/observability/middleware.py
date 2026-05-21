import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .context import request_id_ctx, tenant_id_ctx

logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        tenant_id = request.headers.get("x-tenant-id", "default")

        req_token = request_id_ctx.set(request_id)
        tenant_token = tenant_id_ctx.set(tenant_id)
        start = time.perf_counter()

        try:
            response = await call_next(request)
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request.complete",
                extra={
                    "event": "request.complete",
                    "request_id": request_id,
                    "tenant_id": tenant_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": elapsed_ms,
                    "status_code": getattr(locals().get("response"), "status_code", 500),
                },
            )
            request_id_ctx.reset(req_token)
            tenant_id_ctx.reset(tenant_token)

        response.headers["x-request-id"] = request_id
        response.headers["x-tenant-id"] = tenant_id
        return response
