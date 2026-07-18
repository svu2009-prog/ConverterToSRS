from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from app.models.list_types import RuleSetVersion


class Settings:
    _instance: Optional["Settings"] = None
    _data: Dict[str, Any] = {}
    _file_path: Optional[str] = None

    DEFAULTS: Dict[str, Any] = {
        "last_folder": "",
        "rule_set_version": 3,
        "create_lst": True,
        "create_json": True,
        "create_srs": True,
        "theme": "dark",
        "window_geometry": None,
    }

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, file_path: Optional[str] = None) -> None:
        if file_path is None:
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            file_path = os.path.join(app_dir, "settings.json")
        self._file_path = file_path
        self._data = dict(self.DEFAULTS)

        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        if self._file_path:
            try:
                with open(self._file_path, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, indent=2, ensure_ascii=False)
            except OSError:
                pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    @property
    def last_folder(self) -> str:
        return self._data.get("last_folder", "")

    @last_folder.setter
    def last_folder(self, value: str) -> None:
        self._data["last_folder"] = value

    @property
    def rule_set_version(self) -> RuleSetVersion:
        val = self._data.get("rule_set_version", 3)
        return RuleSetVersion(val)

    @rule_set_version.setter
    def rule_set_version(self, version: RuleSetVersion) -> None:
        self._data["rule_set_version"] = version.value

    @property
    def create_lst(self) -> bool:
        return self._data.get("create_lst", True)

    @create_lst.setter
    def create_lst(self, value: bool) -> None:
        self._data["create_lst"] = value

    @property
    def create_json(self) -> bool:
        return self._data.get("create_json", True)

    @create_json.setter
    def create_json(self, value: bool) -> None:
        self._data["create_json"] = value

    @property
    def create_srs(self) -> bool:
        return self._data.get("create_srs", True)

    @create_srs.setter
    def create_srs(self, value: bool) -> None:
        self._data["create_srs"] = value

    @property
    def theme(self) -> str:
        return self._data.get("theme", "dark")

    @theme.setter
    def theme(self, value: str) -> None:
        self._data["theme"] = value

    @property
    def window_geometry(self) -> Optional[Dict[str, int]]:
        return self._data.get("window_geometry")

    @window_geometry.setter
    def window_geometry(self, value: Optional[Dict[str, int]]) -> None:
        self._data["window_geometry"] = value
