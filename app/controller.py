from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from app.models.list_processor import ListProcessor
from app.models.report import ProcessingReport
from app.utils.logger import LogManager
from app.utils.settings import Settings
from app.views.dialogs import AboutDialog, ReportDialog
from app.views.main_window import MainWindow
from app.views.theme import Theme


class LogSignalHandler(logging.Handler):
    def __init__(self, signal: Signal) -> None:
        super().__init__()
        self._signal = signal
        self.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))
        self.setLevel(logging.INFO)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        try:
            self._signal.emit(msg)
        except RuntimeError:
            pass


class Controller(QObject):
    log_message = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._settings = Settings()
        self._processor = ListProcessor()
        self._main_window: Optional[MainWindow] = None

        LogManager().setup()
        handler = LogSignalHandler(self.log_message)
        LogManager().add_gui_handler(handler)
        self.log_message.connect(self._on_log_message)

        self._settings.load()

    def start(self) -> None:
        app = QApplication.instance()
        if app is None:
            return

        theme = self._settings.theme
        Theme.apply(theme)

        self._main_window = MainWindow(self._processor, self)
        self._main_window.show()

    def log(self, message: str) -> None:
        logging.info(message)

    def _on_log_message(self, message: str) -> None:
        if self._main_window:
            from app.views.main_window import MainWindow
            self._main_window._log_view.appendPlainText(message)

    def show_report(self, report_text: str) -> None:
        if self._main_window:
            dlg = ReportDialog(report_text, self._main_window)
            dlg.exec()

    def show_about(self) -> None:
        if self._main_window:
            dlg = AboutDialog(self._main_window)
            dlg.exec()

    def set_theme(self, theme_name: str) -> None:
        self._settings.theme = theme_name
        self._settings.save()
        Theme.apply(theme_name)

    @property
    def processor(self) -> ListProcessor:
        return self._processor
