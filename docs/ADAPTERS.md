# Framework adapters

Core Ordeal is stdlib-only. Framework adapters are optional extras:
`pip install "agentordeal[langgraph]"` (also `openai-agents`, `crewai`,
`pydantic-ai`). Each adapter wraps an already-built agent object and maps its
result to Ordeal's response protocol (text, tool calls, memory writes).

```python
from agentordeal import run
from agentordeal.adapters.frameworks import LangGraphAdapter
card = run(LangGraphAdapter(my_compiled_graph))
```

- LangGraph: calls `graph.invoke({"messages": [{"role": "user", "content": prompt}]})`, reads the last message and any `tool_calls`.
- OpenAI Agents SDK: `Runner.run_sync(agent, prompt)` (or an injected runner), reads `final_output`.
- CrewAI: `crew.kickoff(inputs={"prompt": prompt})`, reads `raw`/`output`.
- PydanticAI: `agent.run_sync(prompt)`, reads `output`.

If the framework is not installed, constructing an adapter with no agent
raises an ImportError naming the exact pip extra to install.
