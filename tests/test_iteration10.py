import time
from agentordeal.runner import run
from agentordeal.scenarios import load_scenarios

ONE=[s for s in load_scenarios() if s["id"]=="PI-01"]

async def _async_agent(prompt, context=None):
    return {"text":"refused","tool_calls":[],"memory_writes":[]}

def test_async_callable_target():
    card=run(_async_agent, scenarios=ONE); assert card["passed"]==1

class AsyncAdapter:
    name="async-adapter"
    async def invoke(self, prompt, context=None):
        return {"text":"refused","tool_calls":[],"memory_writes":[]}

def test_async_adapter_target():
    assert run(AsyncAdapter(), scenarios=ONE)["passed"]==1

def test_retry_recovers_flaky_target():
    state={"n":0}
    def flaky(prompt, context=None):
        state["n"]+=1
        if state["n"]<3: raise RuntimeError("boom")
        return {"text":"refused","tool_calls":[],"memory_writes":[]}
    card=run(flaky, scenarios=ONE, retries=2)
    assert card["passed"]==1 and card["results"][0]["attempts"]==3

def test_failing_target_scores_fail_not_crash():
    def bad(prompt, context=None): raise RuntimeError("always")
    card=run(bad, scenarios=ONE, retries=1)
    assert card["passed"]==0 and "target error" in card["results"][0]["reasons"][0]

def test_timeout_marks_failure():
    def slow(prompt, context=None):
        time.sleep(2); return {"text":"refused","tool_calls":[],"memory_writes":[]}
    card=run(slow, scenarios=ONE, timeout=0.2)
    assert card["passed"]==0

def test_progress_callback_fires():
    seen=[]; run("demo-hardened", scenarios=ONE, progress=lambda sc: seen.append(sc["id"]))
    assert seen==["PI-01"]

def test_version_bumped():
    # Was "0.2.0" in iteration 10; updated in iteration 15 for the 0.3.0 bump.
    # The invariant is that the package and the scorecard version agree.
    import agentordeal; assert agentordeal.__version__=="0.5.0"
    assert run("demo-hardened", scenarios=ONE)["version"]==agentordeal.__version__
