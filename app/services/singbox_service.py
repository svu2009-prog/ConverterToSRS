from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SingBoxService:
    def __init__(self) -> None:
        self._executable: Optional[str] = None
        self._version: Optional[str] = None

    def check_available(self) -> Tuple[bool, str]:
        exe = self._find_executable()
        if exe is None:
            self._executable = None
            self._version = None
            return False, "sing-box не найден"

        try:
            result = subprocess.run(
                [exe, "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                first_line = result.stdout.strip().split("\n")[0]
                self._executable = exe
                self._version = first_line
                return True, first_line
            return False, result.stderr.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
            self._executable = None
            self._version = None
            return False, str(e)

    def is_available(self) -> bool:
        return self._executable is not None

    @property
    def version(self) -> Optional[str]:
        return self._version

    def compile_rule_set(self, json_path: str, srs_path: str) -> Tuple[bool, str]:
        if not self._executable:
            return False, "sing-box не найден"

        try:
            result = subprocess.run(
                [self._executable, "rule-set", "compile", "--output", srs_path, json_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr.strip() or result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Таймаут компиляции SRS"
        except Exception as e:
            return False, str(e)

    def _find_executable(self) -> Optional[str]:
        exe_name = "sing-box.exe" if sys.platform == "win32" else "sing-box"

        exe_path = shutil.which(exe_name)
        if exe_path:
            return exe_path

        local_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), exe_name)
        if os.path.isfile(local_path):
            return local_path

        return None

    def get_install_instructions(self) -> str:
        return (
            "Для установки sing-box используйте один из способов:\n\n"
            "1. Winget (рекомендуется):\n"
            "   winget install sing-box\n\n"
            "2. Scoop:\n"
            "   scoop install sing-box\n\n"
            "3. Chocolatey:\n"
            "   choco install sing-box\n\n"
            "4. Ручная установка:\n"
            "   - Скачайте архив с https://github.com/SagerNet/sing-box/releases\n"
            "   - Распакуйте в любую папку\n"
            "   - Добавьте папку в PATH или поместите sing-box.exe рядом с программой"
        )
