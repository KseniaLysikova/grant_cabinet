import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings


def validate_upload_file(file: UploadFile, file_size: int) -> None:
    ext = Path(file.filename or "").suffix.lower()

    if ext not in settings.allowed_extensions_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла. Разрешены: {', '.join(sorted(settings.allowed_extensions_set))}",
        )

    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимум: {settings.max_file_size_mb} MB",
        )


def build_storage_name(original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"


def ensure_upload_dir() -> None:
    os.makedirs(settings.upload_dir, exist_ok=True)