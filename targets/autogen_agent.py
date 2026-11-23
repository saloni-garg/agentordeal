"""AutoGen (autogen-agentchat) target harness: an AssistantAgent with the
shared tool set as FunctionTools, backed by DeepSeek via
OpenAIChatCompletionClient. Fresh agent per invocation so the scenario
system message applies. Tool calls recorded by common.py wrappers."""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from agentordeal.adapters.base import AgentResponse

class AutoGenHarness:
    name = "autogen-agent"
    def invoke(self, prompt, context=None):
        context = context or {}
        system = context.get("system") or "You are a helpful assistant."
        cfg = common.model_config()
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_core.tools import FunctionTool
        from autogen_core.models import ModelFamily
        client = OpenAIChatCompletionClient(
            model=cfg["model"], base_url=cfg["base_url"],
            model_info={"vision": False, "function_calling": True,
                        "json_output": True, "family": ModelFamily.UNKNOWN,
                        "structured_output": False, "multiple_system_messages": True},
            **common.auth_kwargs())
        tools = [FunctionTool(fn, description=f"Call the {name} tool. Returns a stub result.",
                              name=name)
                 for name, fn in common.TOOL_FUNCS.items()]
        agent = AssistantAgent("assistant", model_client=client, tools=tools,
                               system_message=system, reflect_on_tool_use=True,
                               max_tool_iterations=3)
        recorder = common.begin()
        result = asyncio.run(agent.run(task=prompt))
        text = ""
        if getattr(result, "messages", None):
            last = result.messages[-1]
            text = str(getattr(last, "content", "") or "")
        return AgentResponse(text=text, tool_calls=recorder.tool_calls,
                             memory_writes=recorder.memory_writes)

def build():
    return AutoGenHarness()
