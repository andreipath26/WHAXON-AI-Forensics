"""Scope enforcement — check whether a target is authorized for testing.

The scope file lives at `<data_dir>/scope.json` and looks like:

    {
      "engagement": "Acme Q3 pentest",
      "enabled": true,
      "in_scope": ["127.0.0.1", "acme.com", "*.acme.com", "10.0.0.0/24"],
      "out_of_scope": ["prod.acme.com"],
      "notes": "Testing window: Mon-Fri 09:00-18:00 UTC."
    }

Rules:
- out_of_scope always wins over in_scope.
- If enabled is false, every target is allowed. This is a deliberate,
  operator-set value; it must never be the result of a missing or
  malformed config file.
- If no scope file exists, a strict default is written on first load:
  loopback + RFC1918 only. Anything else is denied.
- A malformed scope file is a fatal error: refuse to run rather than
  silently allow everything.
- Supports exact hosts, wildcards (*.example.com), CIDR ranges, and bare IPs.
"""
from __future__ import annotations

import ipaddress
import json
import socket
import tempfile
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class ScopeMatch:
    allowed: bool
    reason: str = ""
    matched_rule: str = ""

    def to_dict(self) -> dict:
        return {"allowed": self.allowed, "reason": self.reason,
                "matched_rule": self.matched_rule}


class OutOfScopeError(RuntimeError):
    """Raised when a target is outside the declared scope and no override was given."""
    def __init__(self, target: str, reason: str, matched_rule: str = "") -> None:
        self.target = target
        self.reason = reason
        self.matched_rule = matched_rule
        super().__init__(f"Out of scope: {target} — {reason}")


def _normalize_target(raw: str) -> tuple[str, str]:
    """Return (host, kind) where kind is 'host', 'ip', or 'url'.

    - URLs are parsed and their host extracted.
    - Hostnames are lowercased.
    - Trailing dots are stripped.
    - A scheme-less host with a port (host:port) keeps just the host.
    """
    if not raw:
        return "", "host"
    raw = raw.strip()
    if "://" in raw:
        parsed = urlparse(raw)
        host = parsed.hostname or ""
        return host.lower().rstrip("."), "url"
    # Bare host or IP, possibly with :port
    host = raw.split("/", 1)[0]  # strip any path
    if ":" in host and not _looks_like_ipv6(host):
        host = host.rsplit(":", 1)[0]  # strip port
    host = host.lower().rstrip(".")
    try:
        ipaddress.ip_address(host)
        return host, "ip"
    except ValueError:
        return host, "host"


def _looks_like_ipv6(s: str) -> bool:
    return s.count(":") >= 2


def _rule_matches_host(rule: str, host: str) -> bool:
    """Match a rule against a host. Supports exact and wildcard (*.example.com)."""
    rule = rule.lower().rstrip(".")
    if rule == host:
        return True
    if rule.startswith("*."):
        suffix = rule[2:]
        # *.example.com matches sub.example.com but not example.com itself
        if host == suffix:
            return False
        return host.endswith("." + suffix)
    return False


def _rule_matches_ip(rule: str, ip: str) -> bool:
    """Match a rule against an IP. Supports exact and CIDR."""
    try:
        if "/" in rule:
            net = ipaddress.ip_network(rule, strict=False)
            addr = ipaddress.ip_address(ip)
            return addr in net
        else:
            return str(ipaddress.ip_address(rule)) == ip
    except ValueError:
        return False


def _is_ip_rule(rule: str) -> bool:
    """Return whether a scope rule is an IP literal or CIDR network."""
    try:
        if "/" in rule:
            ipaddress.ip_network(rule, strict=False)
        else:
            ipaddress.ip_address(rule)
        return True
    except ValueError:
        return False




def _atomic_write(path: Path, content: str) -> None:
    """Write a private config file atomically without following a predictable temp path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
        os.replace(tmp, path)
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


class ScopeManager:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._enabled = False
        self._engagement = ""
        self._in: list[str] = []
        self._out: list[str] = []
        self._notes = ""
        self.load()

    # ---- loading ----

    # Written to disk the first time the manager loads with no config present.
    _DEFAULT_SCOPE = {
        "engagement": "default",
        "enabled": True,
        "in_scope": [
            # IPv4 loopback + RFC1918
            "127.0.0.0/8",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
            # IPv6 loopback + link-local + unique-local
            "::1",
            "fe80::/10",
            "fc00::/7",
        ],
        "out_of_scope": [],
        "notes": (
            "Auto-generated default scope. Loopback and RFC1918 only. "
            "Edit this file to declare your engagement. To explicitly "
            "disable scope enforcement, set \"enabled\": false — that "
            "must be an operator decision, never a fallback."
        ),
    }

    def load(self) -> None:
        if not self.path.exists():
            # Fail closed: write a strict default, then use it.
            self.path.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(self.path, json.dumps(self._DEFAULT_SCOPE, indent=2))
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            # Fail closed: a broken config must not become "allow everything".
            raise RuntimeError(
                f"scope config at {self.path} is unreadable ({e}). "
                f"Fix or delete it to continue."
            ) from e
        if not isinstance(raw, dict):
            raise RuntimeError(
                f"scope config at {self.path} must contain a JSON object"
            )

        enabled = raw.get("enabled", True)
        # bool(value) is unsafe here: null, 0, and "" would silently disable
        # scope enforcement. Only the literal JSON booleans are valid.
        if type(enabled) is not bool:
            raise RuntimeError(
                f"scope config at {self.path} has invalid 'enabled'; "
                "expected true or false"
            )

        def _rules(key: str) -> list[str]:
            value = raw.get(key, [])
            if not isinstance(value, list) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                raise RuntimeError(
                    f"scope config at {self.path} has invalid '{key}'; "
                    "expected a list of non-empty strings"
                )
            return [item.strip() for item in value]

        engagement = raw.get("engagement", "")
        notes = raw.get("notes", "")
        if not isinstance(engagement, str) or not isinstance(notes, str):
            raise RuntimeError(
                f"scope config at {self.path} has invalid engagement or notes; "
                "expected strings"
            )

        self._enabled = enabled
        self._engagement = engagement
        self._in = _rules("in_scope")
        self._out = _rules("out_of_scope")
        self._notes = notes

    def save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(self.path, json.dumps(data, indent=2))
        try:
            from whaxon.core import override_log as _ovr
            _ovr.log_override(self.path.parent, "scope_edit", "scope.json")
        except Exception:
            pass
        self.load()

    # ---- properties ----

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def engagement(self) -> str:
        return self._engagement

    @property
    def in_scope(self) -> list[str]:
        return list(self._in)

    @property
    def out_of_scope(self) -> list[str]:
        return list(self._out)

    @property
    def notes(self) -> str:
        return self._notes

    def summary(self) -> dict:
        return {
            "enabled": self._enabled,
            "engagement": self._engagement,
            "in_scope": list(self._in),
            "out_of_scope": list(self._out),
            "notes": self._notes,
            "path": str(self.path),
        }

    # ---- the check ----

    def check(self, raw_target: str) -> ScopeMatch:
        if not self._enabled:
            return ScopeMatch(allowed=True, reason="scope disabled")

        host, kind = _normalize_target(raw_target)
        if not host:
            return ScopeMatch(allowed=False, reason="empty target", matched_rule="")

        # Direct host/IP rules are evaluated before DNS. Out-of-scope always wins.
        for rule in self._out:
            if _rule_matches_ip(rule, host) or _rule_matches_host(rule, host):
                return ScopeMatch(False, "matches out-of-scope rule", rule)

        resolved_ips: set[str] = set()
        ip_rules = [
            rule for rule in (*self._in, *self._out) if _is_ip_rule(rule)
        ]
        if kind == "ip":
            resolved_ips.add(str(ipaddress.ip_address(host)))
        elif ip_rules:
            # A hostname can resolve outside an IP/CIDR-only engagement. Check
            # its current A/AAAA answers before authorizing a network operation.
            # This is a preflight guard, not a substitute for network-level
            # egress enforcement: tools may resolve the name again at connect
            # time, so DNS rebinding must also be controlled at the network layer.
            try:
                answers = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
                for answer in answers:
                    address = str(answer[4][0]).split("%", 1)[0]
                    resolved_ips.add(str(ipaddress.ip_address(address)))
            except (OSError, ValueError):
                return ScopeMatch(
                    False,
                    "hostname resolution failed; scope cannot be confirmed",
                    host,
                )
            if not resolved_ips:
                return ScopeMatch(
                    False,
                    "hostname resolved to no addresses; scope cannot be confirmed",
                    host,
                )

        # Out-of-scope IP/CIDR rules also apply to hostname resolutions.
        for rule in self._out:
            for address in resolved_ips:
                if _rule_matches_ip(rule, address):
                    return ScopeMatch(
                        False, "resolved address matches out-of-scope rule", rule
                    )

        # An explicit hostname rule authorizes that hostname, subject to the
        # out-of-scope checks above. Otherwise every resolved address must
        # match an in-scope IP/CIDR rule; one in-scope answer is not enough if
        # the same name also resolves to an unauthorized address.
        for rule in self._in:
            if _rule_matches_host(rule, host):
                return ScopeMatch(True, "matches in-scope hostname rule", rule)

        if resolved_ips and all(
            any(_rule_matches_ip(rule, address) for rule in self._in)
            for address in resolved_ips
        ):
            matched = next(
                (
                    rule for rule in self._in
                    if any(_rule_matches_ip(rule, address) for address in resolved_ips)
                ),
                "",
            )
            return ScopeMatch(True, "all resolved addresses match in-scope rules", matched)

        return ScopeMatch(False, "no matching in-scope rule for host or resolved addresses", "")
