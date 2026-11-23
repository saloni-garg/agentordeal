"""PydanticAI target harness: a pydantic_ai.Agent with the shared tool set
as plain tools, backed by DeepSeek via OpenAIChatModel/OpenAIProvider.
Fresh Agent per invocation so the scenario system prompt applies."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from agentordeal.adapters.base import AgentResponse

class PydanticAIHarness:
    name = "pydantic-ai-agent"
    def invoke(self, prompt, context=None):
        context = context or {}
        system = context.get("system") or "You are a helpful assistant."
        cfg = common.model_config()
        from pydantic_ai import Agent, Tool
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        model = OpenAIChatModel(cfg["model"], provider=OpenAIProvider(
            base_url=cfg["base_url"], **common.auth_kwargs()))
        tools = [Tool(fn, name=name) for name, fn in common.TOOL_FUNCS.items()]
        agent = Agent(model, system_prompt=system, tools=tools)
        recorder = common.begin()
        result = agent.run_sync(prompt)
        text = str(getattr(result, "output", None) or getattr(result, "data", "") or "")
        return AgentResponse(text=text, tool_calls=recorder.tool_calls,
                             memory_writes=recorder.memory_writes)

def build():
    return PydanticAIHarness()
