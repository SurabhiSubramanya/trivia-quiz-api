import uuid
import time
import json
import logging
import contextvars

from starlette.middleware.base import BaseHTTPMiddleware

from app.metrics import http_requests_total, http_request_duration_seconds

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = str(uuid.uuid4())
        request_id_var.set(rid)
        t0 = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - t0
        logging.getLogger("access").info(json.dumps({
            "request_id": rid,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        }))
        response.headers["X-Request-ID"] = rid
        return response


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        t0 = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - t0
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            http_status=str(response.status_code),
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)
        return response
