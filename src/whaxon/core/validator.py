"""Deterministic validation engine (§32.2 / §33.1)."""
from __future__ import annotations

import re
from pathlib import Path

from whaxon.core.findings import Finding


class PayloadLoader:
    def __init__(self, payload_dir: Path):
        self.payload_dir = payload_dir
        self._cache: dict[str, list[str]] = {}

    def get_payloads(self, kind: str) -> list[str]:
        """Extract fenced payloads from the markdown for a given finding kind."""
        if kind in self._cache:
            return self._cache[kind]
        
        # Map finding kinds to vendored files
        mapping = {
            "sqli": "sql_injection.md",
            "sql_injection": "sql_injection.md",
            "xss": "xss.md",
            "command_injection": "command_injection.md",
            "lfi": "lfi_rfi.md",
            "rfi": "lfi_rfi.md",
            "crlf_injection": "crlf.md",
            "ssrf": "ssrf.md",
        }
        filename = mapping.get(kind)
        if not filename:
            return []
            
        path = self.payload_dir / filename
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8")
        # Match ```lang\n content \n```
        blocks = re.findall(r'```(?:[a-zA-Z0-9_-]+)?\n(.*?)```', content, re.DOTALL)
        
        payloads = []
        for b in blocks:
            # Split by newline, strip whitespace, ignore empty lines and comments
            for line in b.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    payloads.append(line)
        
        self._cache[kind] = payloads
        return payloads

class Validator:
    """Deterministic payload replay (§32.2 / §33.1).

    Only kinds with a known HTTP shape are replayed. Unknown or
    incomplete findings return 'candidate' with the reason, never a
    silent pass. No LLM. No subprocess. urllib only (R105, R103).
    """

    # Error signatures that prove an injection landed.
    # Specific SQL parser/driver error signatures. Bare DBMS names such as
    # "postgresql" or "sqlite" are not evidence: ordinary error pages and
    # decoy endpoints can contain those words without executing SQL.
    SQL_ERROR_MARKERS = (
        "you have an error in your sql syntax",
        "unclosed quotation mark after the character string",
        "syntax error at or near",
        "unterminated quoted string",
        "sqlstate[",
        "ora-00933",
        "ora-01756",
        "sqlite3.operationalerror: near",
        "sqlite error:",
        "mysql_fetch_array() expects parameter",
    )

    # Command-injection proof marker. The marker is built at execution time
    # by the shell (`$(printf ...)` expands, `""` concatenation joins), so
    # the literal payload never contains it. A response that merely reflects
    # the submitted value therefore cannot satisfy the check.
    CMDI_MARKER_PREFIX = "whaxon_cmdi_"

    REPLAYABLE = {"sqli": "sql", "sql_injection": "sql", "xss": "xss", "command_injection": "cmdi"}

    def __init__(self, payload_dir: Path, timing_threshold: float = 3.0):
        self.loader = PayloadLoader(payload_dir)
        self.timing_threshold = timing_threshold
        # Payload that produced the last verified result (proof export).
        self.last_payload: str | None = None

    def validate(self, finding: Finding, target_url: str | None = None) -> tuple[str, str]:
        """Return (status, reason). status in {verified, refuted, candidate}."""
        ctx = (finding.data or {}).get("_request_context")
        if ctx and ctx.get("url"):
            return self._replay_ctx(ctx, target_url=target_url, kind=finding.kind)
        kind = finding.kind
        if kind not in self.REPLAYABLE:
            return "candidate", f"kind {kind!r} is not directly replayable"
        if not target_url:
            return "candidate", "no target URL supplied"
        param = (finding.data or {}).get("parameter")
        if not param:
            return "candidate", "finding has no parameter to inject"

        if kind == "command_injection":
            return self._validate_command_injection(target_url, param)

        # Validation probes are deliberately curated and non-destructive.
        # Vendored Markdown files are reference material, not executable probe
        # lists: their first fenced examples can be documentation, destructive
        # payloads, or data-exfiltration demos.
        payload = self._safe_probe(kind)
        if payload is None:
            return "candidate", f"no safe validation probe for kind {kind!r}"

        family = self.REPLAYABLE[kind]
        markers = self.SQL_ERROR_MARKERS if family == "sql" else ()

        try:
            baseline_samples = [self._fetch(target_url, param, "whaxon_baseline") for _ in range(3)]
            injected_samples = [self._fetch(target_url, param, payload) for _ in range(3)]
        except Exception as e:
            return "candidate", f"replay failed: {e}"

        # Median of 3 samples per side: robust to single-sample jitter,
        # which is what makes a single slow response untrustworthy as
        # proof of a timing-based injection.
        import statistics as _stats
        base_t = _stats.median(s[1] for s in baseline_samples)
        inj_t = _stats.median(s[1] for s in injected_samples)
        delta = inj_t - base_t
        # Timing alone is evidence for a blind-injection hypothesis, not
        # proof: network jitter and target load can produce the same delta.
        # Keep it as a candidate unless a payload-specific marker confirms
        # the issue. This avoids upgrading timing-only observations to verified.
        timing_reason = (
            f"timing delta (median of 3) {delta:.2f}s >= "
            f"{self.timing_threshold:.1f}s; timing-only result is inconclusive"
            if delta >= self.timing_threshold else None
        )

        baseline_bodies = [(sample[0] or "").lower() for sample in baseline_samples]
        injected_bodies = [(sample[0] or "").lower() for sample in injected_samples]
        for m in markers:
            if (all(m in body for body in injected_bodies)
                    and all(m not in body for body in baseline_bodies)):
                self.last_payload = payload
                return "verified", f"SQL error signature {m!r} appeared consistently only after a quote probe"
        if family == "xss" and (
            all(self._xss_probe_is_executable(sample[0] or "", payload) for sample in injected_samples)
            and all(not self._xss_probe_is_executable(sample[0] or "", payload) for sample in baseline_samples)
        ):
            self.last_payload = payload
            return "verified", "unique non-destructive XSS probe parsed as an active SVG event handler in all injected responses"
        if timing_reason:
            return "candidate", timing_reason
        # Failure to reproduce is not proof that a finding is false: the
        # parameter, method, auth state, or payload may not match.
        return "candidate", "replay produced no conclusive, payload-specific proof"

    @staticmethod
    def _xss_probe_is_executable(body: str, payload: str) -> bool:
        """Confirm the unique probe parses as an active SVG event handler.

        Raw substring reflection is insufficient: markup inside a textarea,
        script block, or HTML comment is not parsed as an SVG element.
        """
        from html.parser import HTMLParser

        match = re.search(r"whaxon_xss_[0-9a-f]{12}", payload)
        if not match:
            return False
        token = match.group(0)

        class _ProbeParser(HTMLParser):
            found = False

            def handle_starttag(self, tag, attrs):
                if tag.lower() != "svg":
                    return
                values = {name.lower(): value or "" for name, value in attrs}
                handler = values.get("onload", "")
                if token in handler and "console.log" in handler:
                    self.found = True

            def handle_startendtag(self, tag, attrs):
                self.handle_starttag(tag, attrs)

        parser = _ProbeParser(convert_charrefs=True)
        try:
            parser.feed(body)
            parser.close()
        except Exception:
            return False
        return parser.found

    @staticmethod
    def _safe_probe(kind: str) -> str | None:
        """Return a bounded, non-destructive probe for automatic validation."""
        if kind in ("sqli", "sql_injection"):
            # A quote can elicit a parser error without data extraction or
            # attempted state modification.
            return "'"
        if kind == "xss":
            import secrets
            token = secrets.token_hex(6)
            # No network calls, cookie access, storage access, or state change.
            return f"<svg onload=\"console.log('whaxon_xss_{token}')\"></svg>"
        return None

    @classmethod
    def _cmdi_probes(cls) -> list[tuple[str, str]]:
        """Return (payload, marker) command-injection probes for one run.

        Each probe appends one shell separator and an `echo` of a per-run
        marker. The marker is split so that the submitted string does not
        contain it: `$(printf <hex>)` is evaluated by the shell, and
        `abcd""efgh` is joined by quote removal. Only real execution of the
        injected command can put the marker in the response.
        """
        import secrets

        token = secrets.token_hex(4)
        head, tail = token[:4], token[4:]
        marker = f"{cls.CMDI_MARKER_PREFIX}{token}"
        payloads = (
            f"x;echo {cls.CMDI_MARKER_PREFIX}$(printf {token})",
            f'x;echo {cls.CMDI_MARKER_PREFIX}{head}""{tail}',
            f"x|echo {cls.CMDI_MARKER_PREFIX}$(printf {token})",
            f"x&&echo {cls.CMDI_MARKER_PREFIX}$(printf {token})",
        )
        return [(p, marker) for p in payloads if marker not in p]

    def _validate_command_injection(self, url: str, param: str) -> tuple[str, str]:
        """Replay canary probes and verify the target's shell produced them."""
        try:
            baseline_body, _ = self._fetch(url, param, "whaxon_baseline")
        except Exception as e:
            return "candidate", f"replay failed: {e}"
        baseline_l = (baseline_body or "").lower()

        for payload, marker in self._cmdi_probes():
            try:
                body, _ = self._fetch(url, param, payload)
            except Exception as e:
                return "candidate", f"replay failed: {e}"
            if marker.lower() in (body or "").lower() and marker.lower() not in baseline_l:
                self.last_payload = payload
                return "verified", (
                    f"command output marker {marker!r} appeared only after injection "
                    f"(payload {payload!r})"
                )

        # Reflection of the payload is not proof: without the marker the
        # result stays a candidate for a human to check.
        return "candidate", (
            "no command-execution canary appeared in the response "
            "(payload reflection alone is not proof)"
        )

    def revalidate(self, finding: Finding, target_url: str | None = None) -> tuple[str, str]:
        """Re-run a previously verified finding and report the outcome.

        Returns ("fixed", reason) if the finding no longer reproduces,
        ("still_vulnerable", reason) if it does. The distinction is:
        a finding was "verified" before; if the replay still produces
        the marker, it is not fixed; if it does not, it is.
        """
        status, reason = self.validate(finding, target_url=target_url)
        if status == "verified":
            return "still_vulnerable", f"replay still verifies: {reason}"
        if status == "refuted":
            return "fixed", f"replay no longer verifies: {reason}"
        if status == "candidate":
            return "inconclusive", f"replay was inconclusive: {reason}"
        return "candidate", f"unexpected revalidation status: {status}"

    @staticmethod
    def _fetch(url: str, param: str, value: str) -> tuple[str, float]:
        """Fetch a query-parameter variant without following redirects."""
        import time
        import urllib.error
        import urllib.request
        from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("validation URL must be an absolute HTTP(S) URL")
        q = dict(parse_qsl(parsed.query))
        q[param] = value
        new_url = urlunparse(parsed._replace(query=urlencode(q)))

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise urllib.error.HTTPError(
                    req.full_url, code, "redirect blocked by validator", headers, fp
                )

        opener = urllib.request.build_opener(NoRedirect)
        req = urllib.request.Request(new_url, headers={"User-Agent": "whaxon-validate/0.11"})
        t0 = time.monotonic()
        try:
            with opener.open(req, timeout=10) as r:
                body = r.read(20000).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if 300 <= exc.code < 400:
                raise ValueError(f"redirect blocked by validator (HTTP {exc.code})") from exc
            raise
        return body, time.monotonic() - t0

    def _replay_ctx(self, ctx: dict, target_url: str | None = None, kind: str | None = None) -> tuple[str, str]:
        """Replay a finding's full HTTP context (method, url, headers, body).

        C-03 hardening applied:
        1. Method allowlist.
        2. URL must match the target host (if target_url is provided).
        3. Redirects are disabled.
        4. Auth/Cookie headers are stripped.
        """
        import time
        import urllib.error
        import urllib.request
        from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

        method = (ctx.get("method") or "GET").upper()
        # Automatic verification must not replay requests that may mutate data.
        if method not in ("GET", "HEAD", "OPTIONS"):
            return "candidate", f"automatic replay of {method} is disabled because it may change target state"

        url = ctx.get("url")
        if not isinstance(url, str):
            return "candidate", "request context has no valid url"
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
            return "candidate", "request context URL must be absolute HTTP(S)"

        # Constrain destination URL to the authorized target host and port.
        if target_url:
            target_parsed = urlparse(target_url)
            ctx_port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
            target_port = target_parsed.port or (443 if target_parsed.scheme == "https" else 80)
            if parsed_url.hostname.lower() != (target_parsed.hostname or "").lower() or ctx_port != target_port:
                return "candidate", "context URL does not match the authorized target host/port"

        headers = ctx.get("headers") or {"User-Agent": "whaxon-validate/0.11"}
        
        # Check 4: Strip auth/cookie headers to prevent leaking them
        headers = {k: v for k, v in headers.items() if k.lower() not in ("authorization", "cookie")}
        if "User-Agent" not in headers and "user-agent" not in [k.lower() for k in headers]:
            headers["User-Agent"] = "whaxon-validate/0.11"

        param = ctx.get("parameter")
        body_template = ctx.get("body")

        payload = None
        cmdi_marker = ""
        if kind == "command_injection":
            payload, cmdi_marker = self._cmdi_probes()[0]
        elif kind in ("sqli", "sql_injection", "xss"):
            payload = self._safe_probe(kind)

        if not payload:
            data = body_template.encode() if body_template and method in ("POST", "PUT", "PATCH") else None
            final_url = url
        elif method in ("POST", "PUT", "PATCH"):
            if body_template and "{payload}" in body_template:
                body_str = body_template.replace("{payload}", payload)
            elif body_template and param:
                pairs = dict(parse_qsl(body_template))
                pairs[param] = payload
                body_str = urlencode(pairs)
            else:
                body_str = urlencode({(param or "q"): payload})
            data = body_str.encode()
            final_url = url
        else:
            parsed = urlparse(url)
            q = dict(parse_qsl(parsed.query))
            q[param or "q"] = payload
            final_url = urlunparse(parsed._replace(query=urlencode(q)))
            data = None

        # Check 3: Disable redirects
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise urllib.error.HTTPError(
                    req.full_url, code, f"redirect to {newurl} blocked by validator", headers, fp
                )

        opener = urllib.request.build_opener(NoRedirect)

        def request_once(request_url: str, request_data: bytes | None) -> tuple[str, float]:
            t0 = time.monotonic()
            req = urllib.request.Request(
                request_url, data=request_data, headers=headers, method=method
            )
            try:
                with opener.open(req, timeout=10) as response:
                    body = response.read(20000).decode("utf-8", errors="replace")
            except urllib.error.HTTPError as exc:
                if 300 <= exc.code < 400:
                    raise ValueError(f"redirect blocked by validator (HTTP {exc.code})") from exc
                raise
            return body, time.monotonic() - t0

        try:
            # Establish a neutral baseline and compare repeated samples. A
            # single slow injected request is not proof of a vulnerability.
            baseline_url = url
            if payload and param:
                parsed_base = urlparse(url)
                baseline_q = dict(parse_qsl(parsed_base.query))
                baseline_q[param] = "whaxon_baseline"
                baseline_url = urlunparse(parsed_base._replace(query=urlencode(baseline_q)))
            baseline_samples = [request_once(baseline_url, None) for _ in range(3)]
            injected_samples = [request_once(final_url, data) for _ in range(3)]
        except urllib.error.HTTPError as exc:
            return "candidate", f"replay failed: HTTP {exc.code}"
        except Exception as exc:
            return "candidate", f"replay failed: {exc}"

        import statistics as _stats
        base_elapsed = _stats.median(sample[1] for sample in baseline_samples)
        injected_elapsed = _stats.median(sample[1] for sample in injected_samples)
        delta = injected_elapsed - base_elapsed
        baseline_l = (baseline_samples[0][0] or "").lower()
        injected_l = (injected_samples[0][0] or "").lower()
        baseline_bodies = [(sample[0] or "").lower() for sample in baseline_samples]
        injected_bodies = [(sample[0] or "").lower() for sample in injected_samples]

        if delta >= self.timing_threshold:
            return "candidate", (
                f"timing signal only: median injected-baseline delta {delta:.2f}s; "
                "needs independent confirmation"
            )
        if cmdi_marker and cmdi_marker.lower() in injected_l and cmdi_marker.lower() not in baseline_l:
            if payload:
                self.last_payload = payload
            return "verified", f"command-execution canary {cmdi_marker!r} appeared only after injection"
        if kind in ("sqli", "sql_injection"):
            for marker in self.SQL_ERROR_MARKERS:
                if (all(marker in body for body in injected_bodies)
                        and all(marker not in body for body in baseline_bodies)):
                    self.last_payload = payload
                    return "verified", f"SQL error signature {marker!r} appeared consistently only after a quote probe"
        if kind == "xss" and payload and (
            all(self._xss_probe_is_executable(sample[0] or "", payload) for sample in injected_samples)
            and all(not self._xss_probe_is_executable(sample[0] or "", payload) for sample in baseline_samples)
        ):
            self.last_payload = payload
            return "verified", "unique non-destructive XSS probe parsed as an active SVG event handler in all injected responses"
        return "candidate", "context replay produced no conclusive, payload-specific proof"
