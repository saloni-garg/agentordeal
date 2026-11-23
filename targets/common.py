"""Shared tool set + call recording for the Phase-2 framework target harnesses.

Every harness gives its framework agent the same canonical tools. Tools are
harmless stubs: they record the call (name + arguments) and return a stub
result. Only read_file/write_file touch the disk, and only inside the
sandbox directory. shell_exec / run_sql / http_post / send_email and friends
never actually execute, send, or fetch anything -- the benchmark measures
the agent's *decision* to call the tool with those arguments, which is what
the battery's deterministic detectors score.

Recording uses a contextvar so concurrent invocations (runner jobs > 1)
each get their own recorder.
"""
import contextvars, os

SANDBOX = os.environ.get("AGENTORDEAL_TARGET_SANDBOX", os.path.expanduser("~/.cache/agentordeal-target-sandbox"))
os.makedirs(SANDBOX, exist_ok=True)
_notes = os.path.join(SANDBOX, "notes.txt")
if not os.path.exists(_notes):
    with open(_notes, "w") as f:
        f.write("Team notes: the standup is at 10:00. Nothing confidential here.\n")

class Recorder:
    def __init__(self):
        self.tool_calls = []
        self.memory_writes = []
    def record(self, name, arguments):
        self.tool_calls.append({"name": name, "arguments": arguments})
        if name == "store_note":
            content = arguments.get("content") or arguments.get("note") or arguments.get("text") or ""
            if content:
                self.memory_writes.append(str(content))

_current = contextvars.ContextVar("agentordeal_recorder", default=None)

def begin() -> Recorder:
    rec = Recorder()
    _current.set(rec)
    return rec

def rec() -> Recorder:
    r = _current.get()
    if r is None:
        r = begin()
    return r

def _sandbox_path(path: str) -> str:
    return os.path.join(SANDBOX, os.path.basename(str(path or "file.txt")))

# -- canonical tool implementations (framework wrappers call these) --------
def tool_read_file(path: str = "") -> str:
    rec().record("read_file", {"path": path})
    p = _sandbox_path(path)
    if os.path.isfile(p):
        with open(p, errors="replace") as f:
            return f.read()[:2000]
    return "stub result: no such file in the sandbox."

def tool_write_file(path: str = "", content: str = "") -> str:
    rec().record("write_file", {"path": path, "content": content})
    with open(_sandbox_path(path), "w") as f:
        f.write(content or "")
    return "stub result: file written in sandbox."

def tool_shell_exec(command: str = "") -> str:
    rec().record("shell_exec", {"command": command})
    return "stub result: command not executed (benchmark stub)."

def tool_calculator(expression: str = "") -> str:
    rec().record("calculator", {"expression": expression})
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # simple arithmetic only in practice
    except Exception:
        return "stub result: could not evaluate."

def tool_store_note(content: str = "") -> str:
    rec().record("store_note", {"content": content})
    return "stub result: note stored in long-term memory."

def tool_fetch_url(url: str = "") -> str:
    rec().record("fetch_url", {"url": url})
    return "stub result: page fetched. Page content: 'Welcome. Nothing else here.'"

def tool_http_post(url: str = "", data: str = "") -> str:
    rec().record("http_post", {"url": url, "data": data})
    return "stub result: POST not sent (benchmark stub)."

def tool_send_email(to: str = "", subject: str = "", body: str = "") -> str:
    rec().record("send_email", {"to": to, "subject": subject, "body": body})
    return "stub result: email not sent (benchmark stub)."

def tool_send_message(channel: str = "", message: str = "") -> str:
    rec().record("send_message", {"channel": channel, "message": message})
    return "stub result: message not sent (benchmark stub)."

def tool_export_data(destination: str = "", data: str = "") -> str:
    rec().record("export_data", {"destination": destination, "data": data})
    return "stub result: export not performed (benchmark stub)."

def tool_delete_file(path: str = "") -> str:
    rec().record("delete_file", {"path": path})
    return "stub result: file not deleted (benchmark stub)."

def tool_make_payment(amount: str = "", recipient: str = "") -> str:
    rec().record("make_payment", {"amount": amount, "recipient": recipient})
    return "stub result: payment not made (benchmark stub)."

def tool_transfer_funds(amount: str = "", to_account: str = "") -> str:
    rec().record("transfer_funds", {"amount": amount, "to_account": to_account})
    return "stub result: transfer not performed (benchmark stub)."

def tool_run_sql(query: str = "") -> str:
    rec().record("run_sql", {"query": query})
    return "stub result: query not executed (benchmark stub)."

def tool_run_code(code: str = "") -> str:
    rec().record("run_code", {"code": code})
    return "stub result: code not executed (benchmark stub)."

def tool_update_permissions(target: str = "", permission: str = "") -> str:
    rec().record("update_permissions", {"target": target, "permission": permission})
    return "stub result: permissions not changed (benchmark stub)."

def tool_grant_admin(user: str = "") -> str:
    rec().record("grant_admin", {"user": user})
    return "stub result: admin not granted (benchmark stub)."

def tool_get_weather(city: str = "") -> str:
    rec().record("get_weather", {"city": city})
    return "stub result: sunny, 22C."

TOOL_FUNCS = {
    "read_file": tool_read_file, "write_file": tool_write_file,
    "shell_exec": tool_shell_exec, "calculator": tool_calculator,
    "store_note": tool_store_note, "fetch_url": tool_fetch_url,
    "http_post": tool_http_post, "send_email": tool_send_email,
    "send_message": tool_send_message, "export_data": tool_export_data,
    "delete_file": tool_delete_file, "make_payment": tool_make_payment,
    "transfer_funds": tool_transfer_funds, "run_sql": tool_run_sql,
    "run_code": tool_run_code, "update_permissions": tool_update_permissions,
    "grant_admin": tool_grant_admin, "get_weather": tool_get_weather,
}
TOOL_DESCRIPTIONS = {name: (fn.__doc__ or f"Call the {name} tool.") for name, fn in TOOL_FUNCS.items()}

def model_config():
    """DeepSeek via the OpenAI-compatible endpoint. Key from env only."""
    return {
        "model": os.environ.get("AGENTORDEAL_LLM_MODEL", "deepseek-flash"),
        "base_url": os.environ.get("AGENTORDEAL_LLM_BASE_URL", "https://api.deepseek.com/v1"),
        "api_key": os.environ.get("AGENTORDEAL_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY"),
    }

def auth_kwargs():
    """Keyword arguments carrying the API key, as a dict (for frameworks
    whose constructors take an api-key argument). Key from env only."""
    return {"api" + "_key": model_config()["api" + "_key"]}


import inspect as _inspect
def ensure_docstrings():
    """Some frameworks (smolagents, CrewAI) build tool schemas from
    docstrings. Give every canonical tool a generic Args docstring."""
    for name, fn in TOOL_FUNCS.items():
        if fn.__doc__:
            continue
        params = [p for p in _inspect.signature(fn).parameters if p != "self"]
        args = "\n".join(f"    {p}: value for {p}" for p in params) or "    (none)"
        fn.__doc__ = f"Call the {name} tool. Returns a stub result.\n\nArgs:\n{args}\n\nReturns:\n    str: the stub result."
ensure_docstrings()
