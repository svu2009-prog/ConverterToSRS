from __future__ import annotations

import logging
import os
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.models.list_types import ListType, RuleSetVersion
from app.models.report import ProcessingReport
from app.services.file_reader import FileReader
from app.utils.settings import Settings

logger = logging.getLogger(__name__)


class ProcessingThread(QThread):
    progress_updated = Signal(int, str)
    processing_finished = Signal(object)
    processing_error = Signal(str)

    def __init__(self, processor, file_path: str, rule_version: RuleSetVersion,
                 create_lst: bool, create_json: bool, create_srs: bool) -> None:
        super().__init__()
        self._processor = processor
        self._file_path = file_path
        self._rule_version = rule_version
        self._create_lst = create_lst
        self._create_json = create_json
        self._create_srs = create_srs

    def run(self) -> None:
        try:
            report = self._processor.process_file(
                file_path=self._file_path,
                rule_version=self._rule_version,
                create_lst=self._create_lst,
                create_json=self._create_json,
                create_srs=self._create_srs,
                progress_callback=self._on_progress,
            )
            self.processing_finished.emit(report)
        except Exception as e:
            logger.exception("Ошибка обработки")
            self.processing_error.emit(str(e))

    def _on_progress(self, value: int, stage: str) -> None:
        self.progress_updated.emit(value, stage)


class MainWindow(QMainWindow):
    def __init__(self, processor, controller) -> None:
        super().__init__()
        self._processor = processor
        self._controller = controller
        self._settings = Settings()
        self._current_file: Optional[str] = None
        self._current_list_type: Optional[ListType] = None
        self._raw_lines: List[str] = []
        self._thread: Optional[ProcessingThread] = None

        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()
        self._restore_settings()
        self._check_singbox()

    def _setup_ui(self) -> None:
        self.setWindowTitle("List Processor for sing-box")
        self.setMinimumSize(700, 650)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)

        file_group = QGroupBox("Файл")
        file_layout = QHBoxLayout(file_group)
        self._file_path_edit = QLineEdit()
        self._file_path_edit.setReadOnly(True)
        self._file_path_edit.setPlaceholderText("Выберите файл для обработки...")
        self._browse_btn = QPushButton("Обзор")
        self._browse_btn.clicked.connect(self._on_browse)
        file_layout.addWidget(self._file_path_edit)
        file_layout.addWidget(self._browse_btn)
        main_layout.addWidget(file_group)

        info_group = QGroupBox("Информация")
        info_layout = QHBoxLayout(info_group)

        info_left = QVBoxLayout()
        self._type_label = QLabel("Тип списка: —")
        self._count_label = QLabel("Количество записей: —")
        info_left.addWidget(self._type_label)
        info_left.addWidget(self._count_label)

        info_right = QVBoxLayout()
        self._dup_label = QLabel("Удалено дубликатов: —")
        self._error_label = QLabel("Ошибок: —")
        info_right.addWidget(self._dup_label)
        info_right.addWidget(self._error_label)

        info_layout.addLayout(info_left)
        info_layout.addLayout(info_right)
        main_layout.addWidget(info_group)

        version_group = QGroupBox("Версия Rule Set")
        version_layout = QHBoxLayout(version_group)
        self._version_radios: List[Tuple[QRadioButton, RuleSetVersion]] = []
        for v in [RuleSetVersion.V1, RuleSetVersion.V2, RuleSetVersion.V3, RuleSetVersion.V4]:
            rb = QRadioButton(f"Version {v.value}")
            if v == RuleSetVersion.V3:
                rb.setChecked(True)
            self._version_radios.append((rb, v))
            version_layout.addWidget(rb)
        version_layout.addStretch()
        main_layout.addWidget(version_group)

        output_group = QGroupBox("Выходные файлы")
        output_layout = QHBoxLayout(output_group)
        self._create_lst_cb = QCheckBox("Создать LST")
        self._create_lst_cb.setChecked(True)
        self._create_json_cb = QCheckBox("Создать JSON")
        self._create_json_cb.setChecked(True)
        self._create_srs_cb = QCheckBox("Создать SRS")
        self._create_srs_cb.setChecked(True)
        output_layout.addWidget(self._create_lst_cb)
        output_layout.addWidget(self._create_json_cb)
        output_layout.addWidget(self._create_srs_cb)
        output_layout.addStretch()
        main_layout.addWidget(output_group)

        log_group = QGroupBox("Журнал")
        log_layout = QVBoxLayout(log_group)
        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMaximumBlockCount(1000)
        log_layout.addWidget(self._log_view)
        log_btn_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Очистить журнал")
        clear_log_btn.clicked.connect(self._log_view.clear)
        save_log_btn = QPushButton("Сохранить журнал")
        save_log_btn.clicked.connect(self._save_log)
        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addWidget(save_log_btn)
        log_btn_layout.addStretch()
        log_layout.addLayout(log_btn_layout)
        main_layout.addWidget(log_group)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 10)
        self._progress_bar.setValue(0)
        self._progress_bar.hide()
        main_layout.addWidget(self._progress_bar)

        btn_layout = QHBoxLayout()
        self._process_btn = QPushButton("Начать обработку")
        self._process_btn.clicked.connect(self._on_process)
        self._process_btn.setEnabled(False)
        open_folder_btn = QPushButton("Открыть папку")
        open_folder_btn.clicked.connect(self._open_output_folder)
        self._exit_btn = QPushButton("Выход")
        self._exit_btn.clicked.connect(self.close)

        btn_layout.addWidget(self._process_btn)
        btn_layout.addWidget(open_folder_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._exit_btn)
        main_layout.addLayout(btn_layout)

        singbox_layout = QHBoxLayout()
        self._singbox_label = QLabel("sing-box: проверка...")
        self._singbox_label.setStyleSheet("color: gray;")
        check_sb_btn = QPushButton("Проверить новую версию")
        check_sb_btn.clicked.connect(self._check_singbox)
        singbox_layout.addWidget(self._singbox_label)
        singbox_layout.addStretch()
        singbox_layout.addWidget(check_sb_btn)
        main_layout.addLayout(singbox_layout)

        self.statusBar().showMessage("Готово")
        self.setAcceptDrops(True)

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        open_action = QAction("Открыть...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._on_browse)
        file_menu.addAction(open_action)

        save_report_action = QAction("Сохранить отчёт...", self)
        save_report_action.setShortcut(QKeySequence("Ctrl+S"))
        save_report_action.triggered.connect(self._save_report)
        file_menu.addAction(save_report_action)

        file_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        settings_menu = menubar.addMenu("Настройки")
        theme_menu = QMenu("Тема оформления", self)
        dark_action = QAction("Тёмная", self)
        dark_action.triggered.connect(lambda: self._controller.set_theme("dark"))
        light_action = QAction("Светлая", self)
        light_action.triggered.connect(lambda: self._controller.set_theme("light"))
        theme_menu.addAction(dark_action)
        theme_menu.addAction(light_action)
        settings_menu.addMenu(theme_menu)

        help_menu = menubar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._controller.show_about)
        help_menu.addAction(about_action)

    def _setup_shortcuts(self) -> None:
        from PySide6.QtGui import QShortcut
        QShortcut(QKeySequence("F5"), self).activated.connect(self._on_process)

    def _on_browse(self) -> None:
        folder = self._settings.get("last_folder", "")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            folder,
            "Поддерживаемые файлы (*.txt *.lst *.doc *.docx);;Все файлы (*.*)",
        )
        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str) -> None:
        try:
            self._current_file = file_path
            self._file_path_edit.setText(file_path)
            self._settings.last_folder = os.path.dirname(file_path)
            self._settings.save()

            raw_lines = FileReader.read_file(file_path)
            self._raw_lines = raw_lines
            self._update_info(raw_lines)

            self._process_btn.setEnabled(True)
            self._controller.log(f"Файл открыт: {os.path.basename(file_path)}")
            self._controller.log(f"Всего строк: {len(raw_lines)}")
        except Exception as e:
            logger.exception("Ошибка открытия файла")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
            self._controller.log(f"Ошибка: {e}")

    def _update_info(self, lines: List[str]) -> None:
        from app.services.validator import EntryValidator
        val = EntryValidator()

        clean = [l.strip() for l in lines if l.strip() and not l.strip().startswith(("#", ";", "//"))]
        has_domains = any(val.is_valid_domain(l) for l in clean)
        has_ips = any(val.is_valid_ip(l) for l in clean)

        if has_domains and has_ips:
            self._current_list_type = ListType.MIXED
            list_type_str = "Смешанный"
        elif has_domains:
            self._current_list_type = ListType.DOMAINS
            list_type_str = "Domains"
        elif has_ips:
            has_v6 = any(":" in l and val.is_valid_ip(l) for l in clean)
            self._current_list_type = ListType.IPV6 if has_v6 else ListType.IPV4
            list_type_str = "IPv6" if has_v6 else "IPv4"
        else:
            self._current_list_type = ListType.DOMAINS
            list_type_str = "—"

        self._type_label.setText(f"Тип списка: {list_type_str}")
        self._count_label.setText(f"Количество записей: {len(clean)}")

        valid_count = sum(1 for l in clean if val.is_valid_domain(l) or val.is_valid_ip(l))
        invalid_count = len(clean) - valid_count
        self._error_label.setText(f"Ошибок: {invalid_count}")

    def _on_process(self) -> None:
        if not self._current_file:
            return

        valid, invalid = self._processor.validate_lines(self._raw_lines)
        if invalid:
            from app.views.dialogs import InvalidEntriesDialog
            dlg = InvalidEntriesDialog(invalid, self)
            result = dlg.exec()
            if result == QDialog.DialogCode.Accepted:
                deleted = dlg.get_entries_to_delete()
                kept = dlg.get_entries_to_keep()
                self._controller.log(f"Невалидные записи: {len(invalid)}, удалено: {len(deleted)}, оставлено: {len(kept)}")
            else:
                self._controller.log("Обработка отменена пользователем")
                return

        if self._current_list_type == ListType.MIXED:
            from app.views.dialogs import MixedListDialog
            dlg = MixedListDialog(self)
            choice = dlg.get_choice()
            if choice is None:
                return
            if choice:
                self._controller.log("Смешанный список: автоматическое разделение")
                self._start_processing()
            else:
                self._controller.log("Смешанный список: обработка как единого")
                self._start_processing()
        else:
            self._start_processing()

    def _start_processing(self) -> None:
        if self._thread and self._thread.isRunning():
            return

        rule_version = self._get_selected_version()
        create_lst = self._create_lst_cb.isChecked()
        create_json = self._create_json_cb.isChecked()
        create_srs = self._create_srs_cb.isChecked() and self._processor.check_singbox()[0]

        self._process_btn.setEnabled(False)
        self._progress_bar.show()
        self._progress_bar.setValue(0)

        self._thread = ProcessingThread(
            processor=self._processor,
            file_path=self._current_file,
            rule_version=rule_version,
            create_lst=create_lst,
            create_json=create_json,
            create_srs=create_srs,
        )
        self._thread.progress_updated.connect(self._on_progress)
        self._thread.processing_finished.connect(self._on_processing_finished)
        self._thread.processing_error.connect(self._on_processing_error)
        self._thread.start()

    def _get_selected_version(self) -> RuleSetVersion:
        for rb, version in self._version_radios:
            if rb.isChecked():
                return version
        return RuleSetVersion.V3

    @Slot(int, str)
    def _on_progress(self, value: int, stage: str) -> None:
        self._progress_bar.setValue(value)
        self.statusBar().showMessage(stage)
        self._controller.log(stage)

    @Slot(object)
    def _on_processing_finished(self, report: ProcessingReport) -> None:
        self._progress_bar.setValue(10)
        self._process_btn.setEnabled(True)
        self.statusBar().showMessage("Готово")

        fin_count = len(self._raw_lines) if hasattr(self, '_raw_lines') else 0

        if report.created_files:
            self._controller.log(f"Создано файлов: {', '.join(report.created_files)}")

        self._dup_label.setText(f"Удалено дубликатов: {report.duplicates_removed}")
        self._error_label.setText(f"Ошибок: {report.errors_count}")

        self._controller.show_report(str(report))
        self._settings.save()

    @Slot(str)
    def _on_processing_error(self, error_msg: str) -> None:
        self._progress_bar.hide()
        self._process_btn.setEnabled(True)
        self.statusBar().showMessage("Ошибка")
        QMessageBox.critical(self, "Ошибка обработки", error_msg)
        self._controller.log(f"Ошибка: {error_msg}")

    def _check_singbox(self) -> None:
        available, info = self._processor.check_singbox()
        if available:
            self._singbox_label.setText(f"sing-box {info}")
            self._singbox_label.setStyleSheet("color: #4ec94e; font-weight: bold;")
            self._controller.log(f"sing-box найден: {info}")
        else:
            self._singbox_label.setText("sing-box не найден")
            self._singbox_label.setStyleSheet("color: #f14c4c; font-weight: bold;")
            self._controller.log("sing-box не найден")
            self._show_singbox_install_dialog()

    def _show_singbox_install_dialog(self) -> None:
        from app.views.dialogs import SingBoxNotFoundDialog
        dlg = SingBoxNotFoundDialog(self)
        dlg.set_instructions(self._processor.get_singbox_service().get_install_instructions())
        dlg.yes_btn.clicked.connect(lambda: self._install_singbox(dlg))
        dlg.recheck_btn.clicked.connect(lambda: self._recheck_singbox(dlg))
        dlg.exec()

    def _install_singbox(self, dialog: SingBoxNotFoundDialog) -> None:
        dialog.close()
        QMessageBox.information(
            self, "Установка sing-box",
            "Выберите способ установки:\n\n"
            "1. Winget: winget install sing-box\n"
            "2. Scoop: scoop install sing-box\n"
            "3. Chocolatey: choco install sing-box\n\n"
            "Или скачайте вручную с GitHub и добавьте в PATH.\n\n"
            "После установки нажмите ОК для повторной проверки."
        )
        self._check_singbox()

    def _recheck_singbox(self, dialog: SingBoxNotFoundDialog) -> None:
        dialog.close()
        self._check_singbox()

    def _open_output_folder(self) -> None:
        if self._current_file:
            folder = os.path.dirname(self._current_file)
            os.startfile(folder)
        else:
            QMessageBox.information(self, "Информация", "Сначала откройте файл для обработки.")

    def _save_log(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить журнал", "log.txt", "TXT (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._log_view.toPlainText())
                QMessageBox.information(self, "Сохранено", f"Журнал сохранён: {path}")
            except OSError as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить журнал: {e}")

    def _save_report(self) -> None:
        from app.views.dialogs import ReportDialog
        report_text = self._log_view.toPlainText()
        if report_text.strip():
            dlg = ReportDialog(report_text, self)
            dlg.exec()

    def _restore_settings(self) -> None:
        geometry = self._settings.window_geometry
        if geometry:
            self.resize(geometry.get("width", 700), geometry.get("height", 650))

        version = self._settings.rule_set_version
        for rb, v in self._version_radios:
            if v == version:
                rb.setChecked(True)
                break

        self._create_lst_cb.setChecked(self._settings.create_lst)
        self._create_json_cb.setChecked(self._settings.create_json)
        self._create_srs_cb.setChecked(self._settings.create_srs)

    def closeEvent(self, event) -> None:
        self._settings.window_geometry = {"width": self.width(), "height": self.height()}
        self._settings.rule_set_version = self._get_selected_version()
        self._settings.create_lst = self._create_lst_cb.isChecked()
        self._settings.create_json = self._create_json_cb.isChecked()
        self._settings.create_srs = self._create_srs_cb.isChecked()
        self._settings.save()
        super().closeEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and FileReader.supports_drag_drop(url.toLocalFile()):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if FileReader.supports_drag_drop(file_path):
                    self._load_file(file_path)
                    return
