"""LangGraph target harness: a canonical create_react_agent-style agent
(langgraph.prebuilt.create_react_agent) with the shared tool set, backed by
DeepSeek (OpenAI-compatible). One fresh graph per invocation so the
scenario's system prompt (with its planted canary) is the agent's system
prompt. Tool calls are recorded by the shared wrappers in common.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from agentordeal.adapters.base import AgentResponse

def _tools():
    from langchain_core.tools import StructuredTool
    made = []
    for name, fn in common.TOOL_FUNCS.items():
        made.append(StructuredTool.from_function(
            func=fn, name=name,
            description=f"Call the {name} tool. Returns a stub result."))
    return made

class LangGraphHarness:
    name = "langgraph-agent"
    def __init__(self):
        cfg = common.model_config()
        from langchain_openai import ChatOpenAI
        self._model = ChatOpenAI(model=cfg["model"], base_url=cfg["base_url"],
                                 **common.auth_kwargs(), temperature=0)
        self._tools = _tools()
    def invoke(self, prompt, context=None):
        context = context or {}
        system = context.get("system") or "You are a helpful assistant."
        from langgraph.prebuilt import create_react_agent
        graph = create_react_agent(self._model, self._tools, prompt=system)
        recorder = common.begin()
        result = graph.invoke({"messages": [{"role": "user", "content": prompt}]})
        msgs = result.get("messages") or []
        text = ""
        if msgs:
            last = msgs[-1]
            text = str(getattr(last, "content", "") or "")
        return AgentResponse(text=text, tool_calls=recorder.tool_calls,
                             memory_writes=recorder.memory_writes)

def build():
    return LangGraphHarness()
