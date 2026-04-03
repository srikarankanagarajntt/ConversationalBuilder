"""Custom application exceptions with HTTP status codes."""
from fastapi import HTTPException, status


class SessionNotFoundError(HTTPException):
    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )


class CvSchemaValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        )


class ExportNotReadyError(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"CV is not ready for export: {reason}",
        )


class LLMServiceError(HTTPException):
    def __init__(self, detail: str = "LLM service error."):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class UnsupportedFileTypeError(HTTPException):
    def __init__(self, mime: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{mime}' is not supported.",
        )
