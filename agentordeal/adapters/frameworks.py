"""Optional framework adapters. Core stays stdlib-only.

Each adapter wraps a framework agent object and translates its result into
the Ordeal response protocol (text, tool_calls, memory_writes). Adapters
accept an already-constructed object, so they work with the real framework
and with fakes in tests. Constructing from a framework import is lazy: the
`require()` helper raises a clear ImportError naming the pip extra.
"""
import importlib
from .base import BaseAdapter, AgentResponse

def require(module, extra):
    try:
        return importlib.import_module(module)
    except ImportError as e:
        raise ImportError(
            f"{module} is not installed. Install it with: pip install \"agent-ordeal[{extra}]\" "
            f"(or pip install {module})") from e

def _extract_text(result):
    if result is None: return ""
    if isinstance(result, str): return result
    if isinstance(result, dict):
        msgs = result.get("messages") or []
        if msgs:
            last = msgs[-1]
            return str(getattr(last, "content", None) or (last.get("content") if isinstance(last, dict) else last) or "")
        for k in ("output", "final_output", "text", "response", "result", "raw"):
            if result.get(k): return str(result[k])
        return str(result)
    for attr in ("final_output", "output", "content", "text", "raw"):
        v = getattr(result, attr, None)
        if v: return str(v)
    return str(result)

def _extract_tool_calls(result):
    calls = []
    msgs = result.get("messages", []) if isinstance(result, dict) else getattr(result, "messages", []) or []
    for m in msgs:
        for tc in (getattr(m, "tool_calls", None) or (m.get("tool_calls") if isinstance(m, dict) else None) or []):
            if isinstance(tc, dict):
                calls.append({"name": tc.get("name", ""), "arguments": tc.get("args", tc.get("arguments", {}))})
    raw = getattr(result, "tool_calls", None) or (result.get("tool_calls") if isinstance(result, dict) else None)
    for tc in raw or []:
        if isinstance(tc, dict): calls.append({"name": tc.get("name", ""), "arguments": tc.get("arguments", {})})
    return calls

class _FrameworkAdapter(BaseAdapter):
    framework = "framework"; module = ""; extra = ""
    def __init__(self, agent, name=None):
        if agent is None: require(self.module, self.extra)
        self.agent = agent
        self.name = name or f"{self.framework}-agent"
    def _call(self, prompt, context):
        raise NotImplementedError
    def invoke(self, prompt, context=None):
        result = self._call(prompt, context or {})
        if isinstance(result, AgentResponse): return result
        return AgentResponse(text=_extract_text(result), tool_calls=_extract_tool_calls(result))

class LangGraphAdapter(_FrameworkAdapter):
    """Wraps a compiled LangGraph graph: graph.invoke({"messages":[...]})."""
    framework = "langgraph"; module = "langgraph"; extra = "langgraph"
    def _call(self, prompt, context):
        return self.agent.invoke({"messages": [{"role": "user", "content": prompt}]})

class OpenAIAgentsAdapter(_FrameworkAdapter):
    """Wraps an OpenAI Agents SDK agent run via agents.Runner.run_sync, or any
    object with run_sync(agent, prompt) / run(prompt)."""
    framework = "openai-agents"; module = "agents"; extra = "openai-agents"
    def __init__(self, agent, runner=None, name=None):
        super().__init__(agent, name)
        self.runner = runner
    def _call(self, prompt, context):
        if self.runner is not None: return self.runner.run_sync(self.agent, prompt)
        if hasattr(self.agent, "run_sync"): return self.agent.run_sync(prompt)
        if hasattr(self.agent, "run"): return self.agent.run(prompt)
        agents = require("agents", "openai-agents")
        return agents.Runner.run_sync(self.agent, prompt)

class CrewAIAdapter(_FrameworkAdapter):
    """Wraps a CrewAI crew: crew.kickoff(inputs={"prompt": ...})."""
    framework = "crewai"; module = "crewai"; extra = "crewai"
    def _call(self, prompt, context):
        return self.agent.kickoff(inputs={"prompt": prompt, "input": prompt})

class PydanticAIAdapter(_FrameworkAdapter):
    """Wraps a PydanticAI agent: agent.run_sync(prompt)."""
    framework = "pydantic-ai"; module = "pydantic_ai"; extra = "pydantic-ai"
    def _call(self, prompt, context):
        if hasattr(self.agent, "run_sync"): return self.agent.run_sync(prompt)
        result = self.agent.run(prompt)
        return getattr(result, "output", result)

ADAPTERS = {"langgraph": LangGraphAdapter, "openai-agents": OpenAIAgentsAdapter,
            "crewai": CrewAIAdapter, "pydantic-ai": PydanticAIAdapter}
