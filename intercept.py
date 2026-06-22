"""
API Interceptor — mitmproxy addon
Reads rules from rules.json in the same directory.
Reload rules without restart: touch rules.json (or just edit and save it).

Usage:
    mitmdump -s intercept.py --listen-port 8090
    mitmproxy -s intercept.py --listen-port 8090   (interactive TUI)
"""

import json
import os
import time
from mitmproxy import http
from mitmproxy import ctx

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")


def _load_rules():
    try:
        with open(RULES_FILE) as f:
            rules = json.load(f)
        return [r for r in rules if r.get("enabled", True)]
    except Exception as e:
        ctx.log.error(f"[interceptor] Failed to load rules.json: {e}")
        return []


class APIInterceptor:
    def __init__(self):
        self._rules = []
        self._rules_mtime = 0

    def _refresh_rules(self):
        try:
            mtime = os.path.getmtime(RULES_FILE)
        except OSError:
            return
        if mtime != self._rules_mtime:
            self._rules = _load_rules()
            self._rules_mtime = mtime
            ctx.log.info(f"[interceptor] Loaded {len(self._rules)} active rule(s) from rules.json")

    def response(self, flow: http.HTTPFlow):
        self._refresh_rules()

        url = flow.request.pretty_url

        for rule in self._rules:
            pattern = rule.get("match_url", "")
            if pattern and pattern not in url:
                continue

            name = rule.get("name", pattern)
            original_status = flow.response.status_code

            # Override status code
            new_status = rule.get("response_status")
            if new_status is not None:
                flow.response.status_code = new_status

            # Override body
            body = rule.get("response_body")
            if body is not None:
                flow.response.text = json.dumps(body)

            # Override or add headers
            extra_headers = rule.get("response_headers", {})
            for key, value in extra_headers.items():
                flow.response.headers[key] = value

            # Ensure JSON content-type if we set a body and no header override
            if body is not None and "response_headers" not in rule:
                flow.response.headers["Content-Type"] = "application/json"

            ctx.log.info(
                f"[interceptor] MATCHED rule '{name}' | {flow.request.method} {url} "
                f"| status {original_status} -> {flow.response.status_code}"
            )
            return  # first matching rule wins

    def done(self):
        ctx.log.info("[interceptor] Shutting down.")


addons = [APIInterceptor()]
