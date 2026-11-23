#!/usr/bin/env python3
"""A real, minimal MCP server over stdio (newline-delimited JSON-RPC 2.0).

Implements initialize, ping, tools/list and tools/call with two tools:
  - echo: returns its `text` argument unchanged
  - store_note: records a note in memory and confirms (a stand-in for a
    memory-writing tool, so memory-poisoning scenarios have something
    real to call)

Run it through Ordeal:
  agentordeal mcp --command "python examples/mcp_server.py"
  agentordeal scan-mcp --command "python examples/mcp_server.py"

Stdlib only, like the rest of the project.
"""
import json, sys

TOOLS = [
    {"name": "echo",
     "description": "Echo back the provided text.",
     "inputSchema": {"type": "object",
                     "properties": {"text": {"type": "string"}},
                     "required": ["text"]}},
    {"name": "store_note",
     "description": "Store a note in long-term memory.",
     "inputSchema": {"type": "object",
                     "properties": {"note": {"type": "string"}},
                     "required": ["note"]}},
]
_notes = []

def handle(req):
    method = req.get("method", "")
    rid = req.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "agentordeal-example-mcp", "version": "1.0.0"}}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name", "")
        args = params.get("arguments") or {}
        if name == "echo":
            text = str(args.get("text", args.get("prompt", args.get("input", ""))))
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": text}], "isError": False}}
        if name == "store_note":
            note = str(args.get("note", args.get("prompt", args.get("input", ""))))
            _notes.append(note)
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": f"stored: {note}"}], "isError": False}}
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "content": [{"type": "text", "text": f"unknown tool: {name}"}], "isError": True}}
    if rid is not None:
        return {"jsonrpc": "2.0", "id": rid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None  # notification: no response

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
