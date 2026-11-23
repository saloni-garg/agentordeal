"""Target protocol: a target takes (prompt, context) and returns a response.

context keys: secret/canary, system, tools (list of names), memory (list).
Response fields: text (str), tool_calls (list of {name, arguments}), memory_writes (list).
Any callable returning a dict / AgentResponse / object with those attrs works.
"""
from dataclasses import dataclass, field, asdict

@dataclass
class AgentResponse:
    text: str = ""
    tool_calls: list = field(default_factory=list)
    memory_writes: list = field(default_factory=list)
    def to_dict(self): return asdict(self)

def normalize_response(raw):
    if raw is None: return AgentResponse()
    if isinstance(raw, AgentResponse): return raw
    if isinstance(raw, dict):
        return AgentResponse(text=str(raw.get("text","")), tool_calls=list(raw.get("tool_calls") or []), memory_writes=list(raw.get("memory_writes") or []))
    return AgentResponse(text=str(getattr(raw,"text","")), tool_calls=list(getattr(raw,"tool_calls",[]) or []), memory_writes=list(getattr(raw,"memory_writes",[]) or []))

class BaseAdapter:
    name = "base"
    def invoke(self, prompt, context=None):
        raise NotImplementedError
    __call__ = invoke
