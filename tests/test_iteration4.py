import pytest
from agentordeal.runner import run
from agentordeal.adapters.frameworks import (LangGraphAdapter, OpenAIAgentsAdapter,
    CrewAIAdapter, PydanticAIAdapter, require)

class FakeMsg:
    def __init__(self, content, tool_calls=None): self.content=content; self.tool_calls=tool_calls or []
class FakeGraph:
    def invoke(self, state): return {"messages":[FakeMsg("done", [{"name":"search","args":{"q":"x"}}])]}
class FakeRunner:
    def run_sync(self, agent, prompt): return {"final_output":"ran: "+prompt}
class FakeCrew:
    def kickoff(self, inputs): return {"raw":"crew did it"}
class FakePydanticAgent:
    def run_sync(self, prompt):
        class R: output="pydantic answer"
        return R()

def test_langgraph_adapter_with_fake():
    card=run(LangGraphAdapter(FakeGraph()))
    assert card["total"]==91 and card["target"]=="langgraph-agent"

def test_openai_adapter_with_fake_runner():
    a=OpenAIAgentsAdapter(object(), runner=FakeRunner()); assert a.invoke("hi").text=="ran: hi"

def test_crewai_adapter_with_fake():
    assert CrewAIAdapter(FakeCrew()).invoke("hi").text=="crew did it"

def test_pydantic_adapter_with_fake():
    assert PydanticAIAdapter(FakePydanticAgent()).invoke("hi").text=="pydantic answer"

def test_tool_calls_extracted():
    resp=LangGraphAdapter(FakeGraph()).invoke("x")
    assert resp.tool_calls==[{"name":"search","arguments":{"q":"x"}}]

def test_missing_framework_errors_cleanly():
    with pytest.raises(ImportError) as e: LangGraphAdapter(None)
    assert "agent-ordeal[langgraph]" in str(e.value)
    with pytest.raises(ImportError): require("definitely_not_installed_xyz", "langgraph")
