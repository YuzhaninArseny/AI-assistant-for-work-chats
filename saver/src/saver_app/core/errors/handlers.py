from __future__ import annotations
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .base import AppError

logger = logging.getLogger("errors")


async def _app_error_handler(request: Request, exc: AppError):
    logger.warning(
        "app_error code=%s http=%s ctx=%s retryable=%s path=%s",
        exc.code, exc.http_status, exc.ctx, exc.retryable, request.url.path,
    )
    return JSONResponse(status_code=exc.http_status, content=exc.to_response_dict())


async def _request_validation_error_handler(request: Request, exc: RequestValidationError):
    errs = exc.errors() or []
    first = errs[0] if errs else None
    ctx = {"loc": first.get("loc"), "msg": first.get("msg")} if first else None
    logger.warning("request_validation path=%s errors=%s", request.url.path, errs)
    body = {"error": {"code": "VALIDATION_ERROR", "message": "Invalid request", "ctx": ctx}}
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)


async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning("http_exception status=%s detail=%r path=%s", exc.status_code, exc.detail, request.url.path)
    body = {
        "error": {
            "code": "HTTP_ERROR",
            "message": exc.detail if isinstance(exc.detail, str) else "HTTP error",
            "ctx": {"status": exc.status_code},
        }
    }
    return JSONResponse(status_code=exc.status_code, content=body)


async def _unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception path=%s", request.url.path, exc_info=exc)
    body = {"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}}
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(RequestValidationError, _request_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
