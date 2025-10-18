from .base import AppError


class ValidationError(AppError):
    def __init__(self, message: str = "Invalid input", ctx: dict | None = None):
        super().__init__(code="VALIDATION_ERROR", message=message, http_status=400, ctx=ctx)


class SemanticRuleViolation(AppError):
    def __init__(self, message: str = "Semantic rule violated", ctx: dict | None = None):
        super().__init__(code="SEMANTIC_RULE_VIOLATION", message=message, http_status=422, ctx=ctx)


class DuplicateMessageError(AppError):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(
            "MSG_DUPLICATE",
            "Message already exists",
            409,
            {"chat_id": chat_id, "message_id": message_id},
        )


class NotFoundError(AppError):
    def __init__(self, what: str, ctx: dict | None = None):
        super().__init__(code=f"{what.upper()}_NOT_FOUND", message=f"{what} not found", http_status=404, ctx=ctx)
