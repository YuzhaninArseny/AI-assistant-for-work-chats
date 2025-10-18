from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        http_status: int,
        ctx: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        retryable: bool = False,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        self.ctx = ctx
        self.cause = cause
        self.retryable = retryable

    def to_response_dict(self) -> dict[str, Any]:
        # что уходит наружу
        return {"error": {"code": self.code, "message": self.message, "ctx": self.ctx}}

    @staticmethod
    def validation(msg: str = "Invalid input", ctx: dict | None = None) -> "AppError":
        return AppError("VALIDATION_ERROR", msg, 400, ctx)

    @staticmethod
    def not_found(what: str, ctx: dict | None = None) -> "AppError":
        return AppError(f"{what.upper()}_NOT_FOUND", f"{what} not found", 404, ctx)

    @staticmethod
    def conflict(code: str, msg: str, ctx: dict | None = None) -> "AppError":
        return AppError(code, msg, 409, ctx)

    @staticmethod
    def unavailable(msg: str = "Service unavailable", cause: Exception | None = None, retryable: bool = True) -> "AppError":
        return AppError("SERVICE_UNAVAILABLE", msg, 503, cause=cause, retryable=retryable)
