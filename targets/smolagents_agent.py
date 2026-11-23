"""smolagents target harness: a ToolCallingAgent with the shared tool set
(@tool functions), backed by DeepSeek via OpenAIServerModel. The scenario
system prompt replaces the agent's system prompt template."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from agentordeal.adapters.base import AgentResponse

def _tools():
    from smolagents import tool
    made = []
    for name, fn in common.TOOL_FUNCS.items():
        t = tool(fn)
        t.name = name
        made.append(t)
    return made

class SmolagentsHarness:
    name = "smolagents-agent"
    def __init__(self):
        cfg = common.model_config()
        from smolagents import OpenAIServerModel
        self._model = OpenAIServerModel(model_id=cfg["model"], api_base=cfg["base_url"],
                                        tool_choice="auto",
                                        extra_body={"thinking": {"type": "disabled"}},
                                        **common.auth_kwargs())
        self._tools = _tools()
    def invoke(self, prompt, context=None):
        context = context or {}
        system = context.get("system") or "You are a helpful assistant."
        from smolagents import ToolCallingAgent
        agent = ToolCallingAgent(tools=self._tools, model=self._model, max_steps=4)
        recorder = common.begin()
        # smolagents 1.26 ToolCallingAgent has no system-prompt constructor
        # argument; the scenario's system content (canary + rules) is passed
        # as a leading operator-instructions block in the task. Documented
        # in targets/README.md as this harness's plumbing difference.
        task = f"Operator instructions (system): {system}\n\nUser request: {prompt}"
        out = agent.run(task)
        return AgentResponse(text=str(out or ""), tool_calls=recorder.tool_calls,
                             memory_writes=recorder.memory_writes)

def build():
    return SmolagentsHarness()
