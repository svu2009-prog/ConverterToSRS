from __future__ import annotations

import ipaddress
import re
from typing import Optional


class EntryValidator:
    DOMAIN_PATTERN = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    )

    def is_valid_domain(self, entry: str) -> bool:
        entry = entry.strip().lower()
        if not entry:
            return False
        if entry.startswith("."):
            entry = entry[1:]
        return bool(self.DOMAIN_PATTERN.match(entry))

    def is_valid_ip(self, entry: str) -> bool:
        entry = entry.strip()
        if not entry:
            return False
        try:
            if "/" in entry:
                ipaddress.ip_network(entry, strict=False)
            else:
                ipaddress.ip_address(entry)
            return True
        except ValueError:
            return False

    def is_valid_ipv4(self, entry: str) -> bool:
        entry = entry.strip()
        try:
            if "/" in entry:
                net = ipaddress.ip_network(entry, strict=False)
                return net.version == 4
            addr = ipaddress.ip_address(entry)
            return addr.version == 4
        except ValueError:
            return False

    def is_valid_ipv6(self, entry: str) -> bool:
        entry = entry.strip()
        try:
            if "/" in entry:
                net = ipaddress.ip_network(entry, strict=False)
                return net.version == 6
            addr = ipaddress.ip_address(entry)
            return addr.version == 6
        except ValueError:
            return False
