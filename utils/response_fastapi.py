"""
FastAPI response helpers.
Same envelope format as the Flask APIResponse so the frontend stays unchanged.
"""
from datetime import datetime
from typing import Any, Optional

from fastapi.responses import JSONResponse


def ok(data: Any = None, message: Optional[str] = None, status: int = 200) -> JSONResponse:
    body: dict = {"success": True, "timestamp": datetime.now().isoformat()}
    if data is not None:
        body["data"] = data
    if message:
        body["message"] = message
    return JSONResponse(body, status_code=status)


def created(data: Any, message: str = "Resource created successfully") -> JSONResponse:
    return ok(data, message, 201)


def err(message: str, status: int = 400, code: Optional[str] = None) -> JSONResponse:
    body: dict = {"success": False, "error": message, "timestamp": datetime.now().isoformat()}
    if code:
        body["error_code"] = code
    return JSONResponse(body, status_code=status)


def not_found(message: str = "Resource not found") -> JSONResponse:
    return err(message, 404, "NOT_FOUND")


def unauthorized(message: str = "Unauthorized") -> JSONResponse:
    return err(message, 401, "UNAUTHORIZED")


def validation_error(message: str) -> JSONResponse:
    return err(message, 400, "VALIDATION_ERROR")


def server_error(message: str = "Internal server error") -> JSONResponse:
    return err(message, 500, "SERVER_ERROR")
