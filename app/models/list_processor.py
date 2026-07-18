from __future__ import annotations

import json
import logging
import os
import re
from typing import List, Optional, Tuple

from app.models.list_types import ListType, OutputFileType, RuleSetVersion
from app.models.report import ProcessingReport
from app.services.file_reader import FileReader
from app.services.singbox_service import SingBoxService
from app.services.validator import EntryValidator

logger = logging.getLogger(__name__)

COMMENT_PREFIXES = ("#", ";", "//")


class ListProcessor:
    def __init__(self) -> None:
        self._validator = EntryValidator()
        self._singbox = SingBoxService()

    def process_file(
        self,
        file_path: str,
        rule_version: RuleSetVersion = RuleSetVersion.V3,
        create_lst: bool = True,
        create_json: bool = True,
        create_srs: bool = True,
        progress_callback=None,
    ) -> ProcessingReport:
        report = ProcessingReport()
        report.source_file = os.path.basename(file_path)
        output_dir = os.path.dirname(file_path)

        self._update_progress(progress_callback, 0, "Чтение файла")
        raw_lines = FileReader.read_file(file_path)
        report.total_lines = len(raw_lines)
        logger.info(f"Файл открыт: {file_path}, строк: {report.total_lines}")

        self._update_progress(progress_callback, 1, "Удаление пустых строк и пробелов")
        lines = self._clean_lines(raw_lines)

        self._update_progress(progress_callback, 2, "Удаление комментариев")
        lines = self._remove_comments(lines)

        self._update_progress(progress_callback, 3, "Проверка валидности")
        valid_lines, invalid_lines = self._validate_entries(lines)
        report.errors = invalid_lines
        report.errors_count = len(invalid_lines)

        if not valid_lines:
            logger.warning("Нет валидных записей после обработки")
            report.final_count = 0
            return report

        list_type = self._detect_list_type(valid_lines)
        report.list_type = list_type.name.lower()

        if list_type == ListType.MIXED:
            domains, ips = self._split_mixed(valid_lines)
        else:
            domains = valid_lines if list_type == ListType.DOMAINS else []
            ips = valid_lines if list_type in (ListType.IPV4, ListType.IPV6) else []

        if domains:
            self._update_progress(progress_callback, 4, "Удаление дубликатов (домены)")
            domains_before = len(domains)
            domains = self._remove_duplicates(domains)
            report.duplicates_removed += domains_before - len(domains)

            self._update_progress(progress_callback, 5, "Сортировка (домены)")
            domains = self._sort_domains(domains)

        if ips:
            self._update_progress(progress_callback, 4, "Удаление дубликатов (IP)")
            ips_before = len(ips)
            ips = self._remove_duplicates(ips)
            report.duplicates_removed += ips_before - len(ips)

            self._update_progress(progress_callback, 5, "Сортировка (IP)")
            ips = self._sort_ips(ips)

        report.final_count = len(domains) + len(ips)
        base_name = os.path.splitext(report.source_file)[0]
        output_sets = self._build_output_sets(base_name, list_type, domains, ips)

        for suffix, entries, out_type in output_sets:
            if not entries:
                continue

            if create_json and out_type == OutputFileType.JSON:
                self._update_progress(progress_callback, 6, f"Создание JSON: {suffix}")
                json_path = self._write_json(output_dir, suffix, entries, list_type, rule_version)
                report.created_files.append(os.path.basename(json_path))

                if create_srs and self._singbox.is_available():
                    self._update_progress(progress_callback, 8, f"Компиляция SRS: {suffix}")
                    srs_path = os.path.join(output_dir, f"{suffix}.srs")
                    success, error = self._singbox.compile_rule_set(json_path, srs_path)
                    if success:
                        report.created_files.append(os.path.basename(srs_path))
                        logger.info(f"SRS успешно создан: {srs_path}")
                    else:
                        logger.error(f"Ошибка компиляции SRS: {error}")

            if create_lst and out_type == OutputFileType.LST:
                self._update_progress(progress_callback, 7, f"Создание LST: {suffix}")
                lst_path = self._write_lst(output_dir, suffix, entries)
                report.created_files.append(os.path.basename(lst_path))

        self._update_progress(progress_callback, 10, "Готово")
        return report

    def _update_progress(self, callback, value: int, stage: str) -> None:
        if callback:
            callback(value, stage)

    def _clean_lines(self, lines: List[str]) -> List[str]:
        cleaned = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned.append(line)
        return cleaned

    def _remove_comments(self, lines: List[str]) -> List[str]:
        result = []
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(p) for p in COMMENT_PREFIXES):
                continue
            result.append(line)
        return result

    def _validate_entries(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        valid: List[str] = []
        invalid: List[str] = []
        for line in lines:
            if self._validator.is_valid_domain(line) or self._validator.is_valid_ip(line):
                valid.append(line)
            else:
                invalid.append(line)
        return valid, invalid

    def _detect_list_type(self, entries: List[str]) -> ListType:
        has_domains = False
        has_ips = False
        for entry in entries:
            if self._validator.is_valid_domain(entry):
                has_domains = True
            if self._validator.is_valid_ip(entry):
                if ":" in entry:
                    has_ips = True
                else:
                    has_ips = True
        if has_domains and has_ips:
            return ListType.MIXED
        if has_domains:
            return ListType.DOMAINS
        if has_ips:
            if any(":" in e for e in entries):
                return ListType.IPV6
            return ListType.IPV4
        return ListType.DOMAINS

    def _split_mixed(self, entries: List[str]) -> Tuple[List[str], List[str]]:
        domains: List[str] = []
        ips: List[str] = []
        for entry in entries:
            if self._validator.is_valid_domain(entry):
                domains.append(entry)
            elif self._validator.is_valid_ip(entry):
                ips.append(entry)
        return domains, ips

    def _remove_duplicates(self, entries: List[str]) -> List[str]:
        seen: set = set()
        result: List[str] = []
        for entry in entries:
            key = entry.strip().lower()
            if key not in seen:
                seen.add(key)
                result.append(entry)
        return result

    def _sort_domains(self, domains: List[str]) -> List[str]:
        return sorted(domains, key=lambda d: d.lower())

    def _sort_ips(self, ips: List[str]) -> List[str]:
        import ipaddress

        def ip_sort_key(ip_str: str) -> tuple:
            try:
                if "/" in ip_str:
                    net = ipaddress.ip_network(ip_str, strict=False)
                    return (0, net.network_address, net.prefixlen)
                addr = ipaddress.ip_address(ip_str)
                return (0, addr, 0)
            except ValueError:
                return (1, ip_str, 0)

        return sorted(ips, key=ip_sort_key)

    def _build_output_sets(
        self, base_name: str, list_type: ListType, domains: List[str], ips: List[str]
    ) -> List[Tuple[str, List[str], OutputFileType]]:
        sets: List[Tuple[str, List[str], OutputFileType]] = []
        if list_type == ListType.MIXED:
            if domains:
                sets.append((f"{base_name}_domains", domains, OutputFileType.JSON))
                sets.append((f"{base_name}_domains", domains, OutputFileType.LST))
            if ips:
                sets.append((f"{base_name}_ips", ips, OutputFileType.JSON))
                sets.append((f"{base_name}_ips", ips, OutputFileType.LST))
        else:
            entries = domains or ips
            sets.append((base_name, entries, OutputFileType.JSON))
            sets.append((base_name, entries, OutputFileType.LST))
        return sets

    def _write_json(
        self,
        output_dir: str,
        suffix: str,
        entries: List[str],
        list_type: ListType,
        version: RuleSetVersion,
    ) -> str:
        is_domain = self._detect_list_type(entries) == ListType.DOMAINS
        if is_domain:
            key = "domain_suffix"
            values = entries
        else:
            key = "ip_cidr"
            values = [self._ensure_cidr(ip) for ip in entries]

        data: dict = {"version": version.value, "rules": [{key: values}]}

        json_path = os.path.join(output_dir, f"{suffix}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON создан: {json_path}")
        return json_path

    def _ensure_cidr(self, ip_str: str) -> str:
        if "/" in ip_str:
            return ip_str
        return f"{ip_str}/32"

    def _write_lst(self, output_dir: str, suffix: str, entries: List[str]) -> str:
        lst_path = os.path.join(output_dir, f"{suffix}.lst")
        with open(lst_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(entry + "\n")
        logger.info(f"LST создан: {lst_path}")
        return lst_path

    def validate_lines(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        cleaned = self._clean_lines(lines)
        cleaned = self._remove_comments(cleaned)
        return self._validate_entries(cleaned)

    def check_singbox(self) -> Tuple[bool, str]:
        return self._singbox.check_available()

    def get_singbox_service(self) -> SingBoxService:
        return self._singbox
