import json, os, subprocess, sys
import pathlib
ROOT = pathlib.Path(__file__).parent.parent
EX = ROOT / "examples" / "mcp_server.py"

def test_bundled_example_server_lists_tools():
    from agentordeal.adapters.mcp import MCPAdapter
    ad = MCPAdapter(f"{sys.executable} {EX}")
    tools = ad.probe()
    assert [t["name"] for t in tools] == ["echo", "store_note"]

def test_bundled_example_server_end_to_end_run():
    from agentordeal.adapters.mcp import MCPAdapter
    from agentordeal.runner import run
    card = run(MCPAdapter(f"{sys.executable} {EX}"))
    assert card["total"] >= 88 and 0 <= card["score"] <= 100

def test_mcp_client_skips_notifications():
    # server that emits a notification before every response
    srv = ROOT / "tests" / "fixtures" / "noisy_mcp_server.py"
    from agentordeal.adapters.mcp import MCPClient
    with MCPClient(f"{sys.executable} {srv}") as c:
        tools = c.list_tools()
    assert [t["name"] for t in tools] == ["echo"]

def test_scan_bundled_example_server():
    from agentordeal.mcp_scan import scan_server
    res = scan_server(f"{sys.executable} {EX}")
    assert res.get("tool_names") == ["echo", "store_note"]

def test_demo_command(tmp_path, capsys):
    from agentordeal.cli import main
    assert main(["demo", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "demo-hardened" / "scorecard.json").exists()
    assert "Next:" in capsys.readouterr().out

def test_unknown_target_friendly_error(capsys):
    from agentordeal.cli import main
    rc = main(["run", "--target", "nonsense-target", "--out", "/tmp/gx"])
    assert rc == 2
    assert "hint:" in capsys.readouterr().err

def test_packaged_example_server_lists_tools():
    import agentordeal, pathlib
    from agentordeal.adapters.mcp import MCPAdapter
    ex = pathlib.Path(agentordeal.__file__).parent / "example_server.py"
    assert ex.exists()
    tools = MCPAdapter(f"{sys.executable} {ex}").probe()
    assert [t["name"] for t in tools] == ["echo", "store_note"]
