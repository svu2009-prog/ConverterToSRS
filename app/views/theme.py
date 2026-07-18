from __future__ import annotations

from typing import Dict

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


class Theme:
    DARK = "dark"
    LIGHT = "light"

    DARK_STYLE = """
    QMainWindow, QDialog, QWidget {
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    QGroupBox {
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        margin-top: 1ex;
        font-weight: bold;
        color: #d4d4d4;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    QPushButton {
        background-color: #0e639c;
        color: white;
        border: 1px solid #0e639c;
        border-radius: 4px;
        padding: 6px 16px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #1177bb;
    }
    QPushButton:pressed {
        background-color: #094771;
    }
    QPushButton:disabled {
        background-color: #3c3c3c;
        color: #6c6c6c;
    }
    QLineEdit {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 4px 8px;
    }
    QLineEdit:focus {
        border-color: #0e639c;
    }
    QTextEdit, QPlainTextEdit {
        background-color: #1a1a1a;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
    }
    QLabel {
        color: #d4d4d4;
    }
    QRadioButton, QCheckBox {
        color: #d4d4d4;
        spacing: 6px;
    }
    QRadioButton::indicator, QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
    QProgressBar {
        background-color: #2d2d2d;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        text-align: center;
        color: #d4d4d4;
        height: 22px;
    }
    QProgressBar::chunk {
        background-color: #0e639c;
        border-radius: 3px;
    }
    QStatusBar {
        background-color: #007acc;
        color: white;
    }
    QMenuBar {
        background-color: #2d2d2d;
        color: #d4d4d4;
    }
    QMenuBar::item:selected {
        background-color: #0e639c;
    }
    QMenu {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
    }
    QMenu::item:selected {
        background-color: #0e639c;
    }
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #424242;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #4f4f4f;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background-color: #2d2d2d;
        height: 12px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background-color: #424242;
        border-radius: 4px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #4f4f4f;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
    """

    LIGHT_STYLE = """
    QMainWindow, QDialog, QWidget {
        background-color: #f5f5f5;
        color: #1e1e1e;
    }
    QGroupBox {
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        margin-top: 1ex;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: 1px solid #0078d4;
        border-radius: 4px;
        padding: 6px 16px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #106ebe;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
    QPushButton:disabled {
        background-color: #e0e0e0;
        color: #a0a0a0;
    }
    QLineEdit {
        background-color: white;
        color: #1e1e1e;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 4px 8px;
    }
    QLineEdit:focus {
        border-color: #0078d4;
    }
    QTextEdit, QPlainTextEdit {
        background-color: white;
        color: #1e1e1e;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
    }
    QLabel {
        color: #1e1e1e;
    }
    QRadioButton, QCheckBox {
        color: #1e1e1e;
        spacing: 6px;
    }
    QRadioButton::indicator, QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
    QProgressBar {
        background-color: #e0e0e0;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        text-align: center;
        color: #1e1e1e;
        height: 22px;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 3px;
    }
    QStatusBar {
        background-color: #0078d4;
        color: white;
    }
    QMenuBar {
        background-color: #f0f0f0;
        color: #1e1e1e;
    }
    QMenuBar::item:selected {
        background-color: #0078d4;
        color: white;
    }
    QMenu {
        background-color: white;
        color: #1e1e1e;
        border: 1px solid #d0d0d0;
    }
    QMenu::item:selected {
        background-color: #0078d4;
        color: white;
    }
    QScrollBar:vertical {
        background-color: #f0f0f0;
        width: 12px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background-color: #f0f0f0;
        height: 12px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        border-radius: 4px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
    """

    @staticmethod
    def apply(theme_name: str) -> None:
        app = QApplication.instance()
        if app is None:
            return

        if theme_name == Theme.DARK:
            app.setStyleSheet(Theme.DARK_STYLE)
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#d4d4d4"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d2d"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#2d2d2d"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d4d4d4"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0e639c"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            app.setPalette(palette)
        else:
            app.setStyleSheet(Theme.LIGHT_STYLE)
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#f0f0f0"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d4"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            app.setPalette(palette)
