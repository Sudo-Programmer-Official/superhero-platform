import json
import logging
import sys
from datetime import datetime, timezone

from .context import request_id_ctx, tenant_id_ctx


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "") or request_id_ctx.get(),
            "tenant_id": getattr(record, "tenant_id", "") or tenant_id_ctx.get(),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "path"):
            payload["path"] = record.path
        if hasattr(record, "method"):
            payload["method"] = record.method
        if hasattr(record, "status_code"):
            payload["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            payload["duration_ms"] = record.duration_ms
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_ctx.get()
        if not hasattr(record, "tenant_id"):
            record.tenant_id = tenant_id_ctx.get()
        return True


def configure_logging(log_level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())
    root.addHandler(handler)

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
