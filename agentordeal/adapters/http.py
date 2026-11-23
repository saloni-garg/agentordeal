"""HTTP adapter: POST {prompt, context} as JSON, parse {text, tool_calls, memory_writes}.

Rate limiting: transient failures (HTTP 429 and 5xx, and connection
errors) are retried with exponential backoff, honouring a Retry-After
header when the server sends one (capped). Defaults can be overridden
per-instance or via AGENTORDEAL_HTTP_RETRIES / AGENTORDEAL_HTTP_BACKOFF.
A target that still fails after retries returns an error response --
it fails closed, never leaks, and the scenario is scored on that.
"""
import json, os, time, urllib.request, urllib.error
from .base import BaseAdapter, AgentResponse, normalize_response

class HttpAdapter(BaseAdapter):
    def __init__(self, url, timeout=30, max_retries=None, backoff=None, backoff_cap=30.0):
        self.url, self.name, self.timeout = url, url, timeout
        self.max_retries = int(os.environ.get("AGENTORDEAL_HTTP_RETRIES", 3) if max_retries is None else max_retries)
        self.backoff = float(os.environ.get("AGENTORDEAL_HTTP_BACKOFF", 0.5) if backoff is None else backoff)
        self.backoff_cap = backoff_cap
        self.last_attempts = 0

    def _wait(self, attempt, retry_after=None):
        delay = self.backoff * (2 ** attempt)
        if retry_after:
            try: delay = max(delay, float(retry_after))
            except (TypeError, ValueError): pass
        time.sleep(min(self.backoff_cap, delay))

    def invoke(self, prompt, context=None):
        body = json.dumps({"prompt": prompt, "context": context or {}}).encode()
        last_err = None
        for attempt in range(self.max_retries + 1):
            self.last_attempts = attempt + 1
            req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return normalize_response(json.loads(r.read().decode() or "{}"))
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code == 429 or 500 <= e.code < 600:
                    if attempt < self.max_retries:
                        self._wait(attempt, e.headers.get("Retry-After") if e.headers else None)
                        continue
                break
            except Exception as e:  # connection errors etc: retry, then fail closed
                last_err = e
                if attempt < self.max_retries:
                    self._wait(attempt)
                    continue
                break
        return AgentResponse(text=f"[http adapter error: {last_err}]")
