"""CrewAI target harness: a one-agent Crew (Agent + Task) with the shared
tool set, backed by DeepSeek via crewai.LLM (OpenAI-compatible). Fresh crew
per invocation; the scenario system prompt becomes the agent backstory.
Tool calls recorded by common.py wrappers."""
import os, sys
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from agentordeal.adapters.base import AgentResponse

def _tools():
    from crewai.tools import tool
    made = []
    for name, fn in common.TOOL_FUNCS.items():
        made.append(tool(name)(fn))
    return made

class CrewAIHarness:
    name = "crewai-agent"
    def __init__(self):
        cfg = common.model_config()
        from crewai import LLM
        self._llm = LLM(model=f"openai/{cfg['model']}", base_url=cfg["base_url"],
                        temperature=0, **common.auth_kwargs())
        self._tools = _tools()
    def invoke(self, prompt, context=None):
        context = context or {}
        system = context.get("system") or "You are a helpful assistant."
        from crewai import Agent, Task, Crew
        agent = Agent(role="Assistant",
                      goal="Complete the user's request, using the tools when needed.",
                      backstory=system, tools=self._tools, llm=self._llm,
                      verbose=False, max_iter=3)
        task = Task(description=prompt, expected_output="A helpful final answer.",
                    agent=agent)
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        recorder = common.begin()
        result = crew.kickoff()
        return AgentResponse(text=str(getattr(result, "raw", result) or ""),
                             tool_calls=recorder.tool_calls,
                             memory_writes=recorder.memory_writes)

def build():
    return CrewAIHarness()
