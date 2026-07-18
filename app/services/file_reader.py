from __future__ import annotations

import logging
import os
from typing import List, Optional

import chardet

logger = logging.getLogger(__name__)

try:
    from docx import Document as DocxDocument

    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class FileReader:
    SUPPORTED_EXTENSIONS = {".txt", ".lst", ".doc", ".docx"}

    @staticmethod
    def read_file(file_path: str) -> List[str]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in FileReader.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Неподдерживаемый формат файла: {ext}")

        if ext in (".doc", ".docx"):
            return FileReader._read_docx(file_path)
        return FileReader._read_text(file_path)

    @staticmethod
    def _read_text(file_path: str) -> List[str]:
        raw_data = FileReader._read_raw(file_path)
        encoding = FileReader._detect_encoding(raw_data)
        logger.info(f"Определена кодировка: {encoding}")
        text = raw_data.decode(encoding, errors="replace")
        return text.splitlines()

    @staticmethod
    def _read_raw(file_path: str) -> bytes:
        with open(file_path, "rb") as f:
            return f.read()

    @staticmethod
    def _detect_encoding(raw_data: bytes) -> str:
        if raw_data.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        result = chardet.detect(raw_data)
        encoding = result.get("encoding", "utf-8") or "utf-8"
        encoding = encoding.lower()
        if encoding == "ascii":
            encoding = "utf-8"
        return encoding

    @staticmethod
    def _read_docx(file_path: str) -> List[str]:
        if not HAS_DOCX:
            raise ImportError("python-docx не установлен. Установите: pip install python-docx")
        doc = DocxDocument(file_path)
        lines: List[str] = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                lines.append(text)
        return lines

    @staticmethod
    def supports_drag_drop(file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in FileReader.SUPPORTED_EXTENSIONS
