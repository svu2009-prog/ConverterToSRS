from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ProcessingReport:
    source_file: str = ""
    total_lines: int = 0
    duplicates_removed: int = 0
    errors_count: int = 0
    errors: List[str] = field(default_factory=list)
    final_count: int = 0
    created_files: List[str] = field(default_factory=list)
    list_type: str = ""

    def __str__(self) -> str:
        lines = [
            "=" * 40,
            "Отчёт об обработке",
            "=" * 40,
            f"Исходный файл: {self.source_file}",
            f"Тип списка: {self.list_type}",
            f"Всего строк: {self.total_lines}",
            f"Удалено дубликатов: {self.duplicates_removed}",
            f"Ошибок: {self.errors_count}",
            f"Итоговых записей: {self.final_count}",
            "Создано файлов:",
        ]
        for f in self.created_files:
            lines.append(f"  - {f}")
        if self.errors:
            lines.append("Ошибки:")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "total_lines": self.total_lines,
            "duplicates_removed": self.duplicates_removed,
            "errors_count": self.errors_count,
            "errors": self.errors,
            "final_count": self.final_count,
            "created_files": self.created_files,
            "list_type": self.list_type,
        }
