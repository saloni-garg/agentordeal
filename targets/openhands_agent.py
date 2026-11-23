"""OpenHands target harness (software-agent-sdk, local conversation -- no
Docker): an Agent with the built-in TerminalTool and FileEditorTool,
workspace confined to the target sandbox, backed by DeepSeek via LiteLLM
(OpenAI-compatible). Tool calls are extracted from conversation events and
mapped to the canonical battery names: terminal -> shell_exec,
file_editor view -> read_file, create/str_replace/insert -> write_file.
There is no memory tool, so memory_writes is always empty. The scenario
system content is sent as a leading operator-instructions block in the
first message (the SDK Agent has no per-run system-prompt argument in
this harness's usage); see targets/README.md.
"""
import os, sys
os.environ.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from agentordeal.adapters.base import AgentResponse

WORKSPACE = os.path.join(common.SANDBOX, "openhands-workspace")
os.makedirs(WORKSPACE, exist_ok=True)

def _map_events(events):
    calls, text = [], ""
    for ev in events or []:
        kind = type(ev).__name__
        if kind == "ActionEvent":
            tool = getattr(ev, "tool_name", "") or ""
            action = getattr(ev, "action", None)
            args = {}
            if action is not None:
                try:
                    args = action.model_dump(exclude_none=True)
                except Exception:
                    args = {"repr": str(action)[:300]}
            if tool == "terminal":
                calls.append({"name": "shell_exec",
                              "arguments": {"command": args.get("command", str(args))}})
            elif tool == "str_replace_editor":
                cmd = args.get("command", "")
                name = {"view": "read_file", "create": "write_file",
                        "str_replace": "write_file", "insert": "write_file"}.get(cmd, "read_file")
                calls.append({"name": name, "arguments": args})
            else:
                calls.append({"name": tool, "arguments": args})
        elif kind == "MessageEvent":
            llm_msg = getattr(ev, "llm_message", None)
            role = getattr(llm_msg, "role", "") if llm_msg else ""
            if role == "assistant":
                content = getattr(llm_msg, "content", None) or []
                parts = [getattr(c, "text", "") for c in content if getattr(c, "text", "")]
                if parts:
                    text = "\n".join(parts)
    return calls, text

class OpenHandsHarness:
    name = "openhands-agent"
    def invoke(self, prompt, context=None):
        context = context or {}
        system = context.get("system") or "You are a helpful assistant."
        cfg = common.model_config()
        from openhands.sdk import Agent, Conversation, LLM, Tool
        from openhands.tools.terminal import TerminalTool
        from openhands.tools.file_editor import FileEditorTool
        llm = LLM(model=f"openai/{cfg['model']}", base_url=cfg["base_url"],
                  **common.auth_kwargs())
        agent = Agent(llm=llm, tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)])
        conv = Conversation(agent=agent, workspace=WORKSPACE)
        task = f"Operator instructions (system): {system}\n\nUser request: {prompt}"
        conv.send_message(task)
        conv.run()
        events = list(conv.state.events) if getattr(conv, "state", None) else []
        calls, text = _map_events(events)
        return AgentResponse(text=text, tool_calls=calls, memory_writes=[])

def build():
    return OpenHandsHarness()
