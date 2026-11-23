# Framework target harnesses (Phase 2)

Canonical, minimal agents for each major open agent framework, all sharing
one stub tool set, so the AgentOrdeal battery measures the framework +
model combination rather than bespoke agent code. Every harness lives in
this directory (`targets/` in the runner repo) and is run with:

    python targets/run_battery.py <harness_module> <leaderboard-slug>

`run_battery.py` drives the full battery (91 scenarios, battery 1.2.0)
through the runner's callable-target path and writes the scorecard
(json/html/sarif/junit/badge + trace.jsonl) to
`leaderboard/results/<slug>/`. Scores from these runs are merged into
`leaderboard/leaderboard.json` and exported to the leaderboard repo's
`scores.json` (see leaderboard/README.md).

## Shared tool set (common.py)

18 tools with the canonical battery names: read_file, write_file,
shell_exec, calculator, store_note, fetch_url, http_post, send_email,
send_message, export_data, delete_file, make_payment, transfer_funds,
run_sql, run_code, update_permissions, grant_admin, get_weather.

Safety: only read_file/write_file touch disk, and only inside the target
sandbox (`~/.cache/agentordeal-target-sandbox`, overridable with
AGENTORDEAL_TARGET_SANDBOX). Everything else records the call and returns
a stub string -- shell commands are never executed, mail is never sent,
payments never happen, URLs are never fetched. A contextvar-based
recorder keeps parallel scenario jobs' tool calls separate.

## Model

All framework harnesses run against the live model via the registered
DeepSeek connector, exactly as the iteration-18 LLM reference run: the
credential surrogate is fetched in memory by a launcher
(`python3 ~/.cache/ds_run.py <venv-python> targets/run_battery.py ...`)
and passed through environment variables only. No credential is printed
or written to any file. Model: deepseek-flash (DeepSeek-V4.1-Flash),
OpenAI-compatible endpoint https://api.deepseek.com/v1.

## Harnesses and plumbing differences

| Harness | Framework | Shape | Notes |
|---|---|---|---|
| langgraph_agent.py | langgraph 1.2.24 (+ langchain-openai 1.8.5) | `langgraph.prebuilt.create_react_agent` + ChatOpenAI | Tools built as StructuredTool with explicit descriptions (docstring parsing alone gives empty schemas). Fresh graph per scenario. |
| pydantic_ai_agent.py | pydantic-ai 2.71.0 | `Agent` + OpenAIChatModel/OpenAIProvider | Fresh Agent per scenario; tools via `@agent.tool_plain` with generated Args docstrings. |
| smolagents_agent.py | smolagents 1.26.0 | `ToolCallingAgent` + OpenAIServerModel | ToolCallingAgent has no system-prompt argument in 1.26, so scenario system content is sent as a leading "Operator instructions (system):" block in the task. Model needs tool_choice="auto" and thinking disabled (DeepSeek thinking mode rejects a forced tool_choice). max_steps=4. |
| autogen_agent.py | autogen-agentchat 0.7.5 | `AssistantAgent` + FunctionTool, reflect_on_tool_use | max_tool_iterations=3; each invoke runs its own event loop. |
| crewai_agent.py | crewai 1.15.44 | One Agent + one Task, `Crew.kickoff` | max_iter=3, telemetry disabled. CrewAI pins protobuf 7.x while autogen-core wants ~=5.29.3; both still run in the shared venv (pip warns; observed working). |
| openhands_agent.py | openhands-sdk + openhands-tools 1.63.1 | SDK `Agent` + `Conversation` (local, no Docker), TerminalTool + FileEditorTool | Runs in its own venv (`~/.cache/ohvenv`) because of its heavy dependency tree. Unlike the stub harnesses, its terminal and file-editor tools REALLY execute, confined to the workspace directory inside the target sandbox. Tool calls are mapped from conversation events: terminal -> shell_exec, file editor view -> read_file, create/str_replace/insert -> write_file. No memory tool, so memory_writes is always empty. Scenario system content is sent as a leading operator-instructions block (no per-run system-prompt argument used). |

Frameworks were installed into `~/.cache/fwvenv` (langgraph, crewai,
autogen-agentchat, pydantic-ai, smolagents) and OpenHands into
`~/.cache/ohvenv`. Venvs live under ~/.cache because /tmp is a small
tmpfs in this VM.

## Results (battery 1.2.0, 2026-11-23)

See `leaderboard/leaderboard.json` for the authoritative entries with
citations. MCP reference servers are not framework harnesses; they are
scored through the stdio MCP adapter (`agentordeal run --target
"mcp:<command>"`) and statically with `agentordeal scan-mcp`.
