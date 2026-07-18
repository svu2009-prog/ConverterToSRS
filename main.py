#!/usr/bin/env python3
from __future__ import annotations

import sys


def main() -> None:
    from PySide6.QtWidgets import QApplication
    from app.controller import Controller

    app = QApplication(sys.argv)
    app.setApplicationName("List Processor for sing-box")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ConverterToSRS")

    controller = Controller()
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
