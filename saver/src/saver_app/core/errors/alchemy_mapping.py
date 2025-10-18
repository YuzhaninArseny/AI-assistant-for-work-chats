from sqlalchemy.exc import IntegrityError, OperationalError
from psycopg.errors import UniqueViolation, ForeignKeyViolation, DeadlockDetected, SerializationFailure
from .domain import DuplicateMessageError, NotFoundError
from .repo import StorageUnavailable, TxConflict


def map_sqlalchemy_error(e: Exception, *, chat_id: int | None = None, message_id: int | None = None):
    if isinstance(e, IntegrityError):
        orig = getattr(e, "orig", None)
        if isinstance(orig, UniqueViolation):
            if chat_id is not None and message_id is not None:
                return DuplicateMessageError(chat_id, message_id)
            return DuplicateMessageError(chat_id if chat_id is not None else -1,
                                         message_id if message_id is not None else -1)
        if isinstance(orig, ForeignKeyViolation):
            return NotFoundError("related entity")
        return StorageUnavailable(e)

    if isinstance(e, OperationalError):
        orig = getattr(e, "orig", None)
        if isinstance(orig, (DeadlockDetected, SerializationFailure)):
            return TxConflict(e)
        return StorageUnavailable(e)

    return StorageUnavailable(e)
