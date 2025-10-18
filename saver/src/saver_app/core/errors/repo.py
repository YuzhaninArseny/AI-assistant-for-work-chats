from .base import AppError


class StorageUnavailable(AppError):
    def __init__(self, cause: Exception | None = None):
        super().__init__("STORAGE_UNAVAILABLE", "Storage is unavailable", 503, cause=cause, retryable=True)


class TxConflict(AppError):
    def __init__(self, cause: Exception | None = None):
        super().__init__("TX_CONFLICT", "Transaction conflict (retry)", 500, cause=cause, retryable=True)
