from __future__ import annotations

from typing import List, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)


class MixedListDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Смешанный список")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        label = QLabel("Обнаружен смешанный список.\nРазделить его автоматически?")
        label.setWordWrap(True)
        layout.addWidget(label)
        button_layout = QHBoxLayout()
        self.yes_btn = QPushButton("Да")
        self.no_btn = QPushButton("Нет")
        self.cancel_btn = QPushButton("Отмена")

        self.yes_btn.clicked.connect(self.accept)
        self.no_btn.clicked.connect(self.reject)
        self.cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(self.yes_btn)
        button_layout.addWidget(self.no_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        self._choice: Optional[bool] = None

    def get_choice(self) -> Optional[bool]:
        result = self.exec()
        if result == QDialog.DialogCode.Accepted:
            return True
        elif result == QDialog.DialogCode.Rejected:
            return False
        return None


class SingBoxNotFoundDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("sing-box не найден")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        label = QLabel(
            "sing-box не найден.\n\n"
            "Для создания файлов SRS необходимо установить sing-box.\n"
            "Установить сейчас?"
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self.instructions = QTextEdit()
        self.instructions.setReadOnly(True)
        self.instructions.setMaximumHeight(200)
        layout.addWidget(self.instructions)

        button_layout = QHBoxLayout()
        self.yes_btn = QPushButton("Да")
        self.no_btn = QPushButton("Нет")
        self.recheck_btn = QPushButton("Повторная проверка")

        button_layout.addWidget(self.yes_btn)
        button_layout.addWidget(self.recheck_btn)
        button_layout.addWidget(self.no_btn)
        layout.addLayout(button_layout)

    def set_instructions(self, text: str) -> None:
        self.instructions.setPlainText(text)


class InvalidEntriesDialog(QDialog):
    def __init__(self, invalid_entries: List[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Невалидные записи")
        self.setMinimumSize(500, 400)
        self._all_entries: List[str] = list(invalid_entries)
        self._removed_entries: List[str] = []

        layout = QVBoxLayout(self)
        label = QLabel(f"Найдено невалидных записей: {len(invalid_entries)}")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        for entry in invalid_entries:
            item = QListWidgetItem(entry)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить выделенные")
        delete_btn.clicked.connect(self._delete_checked)
        keep_btn = QPushButton("Оставить все")
        keep_btn.clicked.connect(self._keep_all)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(keep_btn)
        layout.addLayout(btn_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _delete_checked(self) -> None:
        for i in range(self.list_widget.count() - 1, -1, -1):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self._removed_entries.append(item.text())
                self.list_widget.takeItem(i)

    def _keep_all(self) -> None:
        self.accept()

    def get_entries_to_keep(self) -> List[str]:
        result: List[str] = []
        for i in range(self.list_widget.count()):
            result.append(self.list_widget.item(i).text())
        return result

    def get_entries_to_delete(self) -> List[str]:
        return list(self._removed_entries)


class ReportDialog(QDialog):
    def __init__(self, report_text: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Отчёт об обработке")
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout(self)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(report_text)
        layout.addWidget(text_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Save)
        button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self._save_report)
        layout.addWidget(button_box)
        self._report_text = report_text

    def _save_report(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчёт", "report.txt", "TXT (*.txt);;JSON (*.json)")
        if path:
            import json
            try:
                if path.endswith(".json"):
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump({"report": self._report_text}, f, indent=2, ensure_ascii=False)
                else:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(self._report_text)
                QMessageBox.information(self, "Сохранено", f"Отчёт сохранён: {path}")
            except OSError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчёт: {e}")


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(350, 200)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("List Processor for sing-box")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(QLabel("Версия: 1.0"))
        layout.addWidget(QLabel("Платформа: Windows 10/11 x64"))
        layout.addWidget(QLabel("Разработано для обработки списков доменов и IP"))
        btn = QPushButton("Закрыть")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
