import pathlib
"""Iteration 15: diff, metadata, seeding, HTTP backoff, version bump."""
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from agentordeal.runner import run
from agentordeal.diff import diff_cards, format_diff
from agentordeal.scorecard import to_sarif, to_junit, to_html

def test_diff_vulnerable_vs_hardened():
    v, h = run("demo-vulnerable"), run("demo-hardened")
    d = diff_cards(v, h)
    assert d["score_delta"] == round(h["score"] - v["score"], 1)
    assert d["regressions"] == []
    assert len(d["fixes"]) == h["passed"] - v["passed"]
    back = diff_cards(h, v)
    assert len(back["regressions"]) == h["passed"] - v["passed"]
    assert "REGRESSED" in format_diff(back)

def test_diff_identical_cards_is_empty():
    h = run("demo-hardened")
    d = diff_cards(h, h)
    assert d["score_delta"] == 0 and d["regressions"] == [] and d["fixes"] == []

def test_metadata_in_card_and_all_formats():
    card = run("demo-hardened")
    m = card["metadata"]
    assert m["tool_version"] and m["battery_version"] == card["battery_version"]
    assert m["timestamp"] and m["duration_seconds"] >= 0
    assert m["scenario_count"] == 91 and m["target"] == "demo-hardened"
    assert m["seed"] is None
    sarif = json.loads(to_sarif(card))
    props = sarif["runs"][0]["properties"]
    assert props["battery_version"] == card["battery_version"]
    assert "agentordeal.battery_version" in to_junit(card)
    assert "Battery" in to_html(card)

def test_seed_is_deterministic_and_recorded():
    a = run("demo-hardened", seed=42)
    b = run("demo-hardened", seed=42)
    assert [r["id"] for r in a["results"]] == [r["id"] for r in b["results"]]
    assert a["metadata"]["seed"] == 42 and a["score"] == b["score"] == 100.0
    c = run("demo-hardened", seed=7)
    assert [r["id"] for r in c["results"]] != [r["id"] for r in a["results"]]  # order actually seeded

def test_http_backoff_retries_429_then_succeeds():
    counts = {"n": 0}
    class H(BaseHTTPRequestHandler):
        def log_message(self, *x): pass
        def do_POST(self):
            counts["n"] += 1
            self.rfile.read(int(self.headers["Content-Length"]))
            if counts["n"] < 3:
                self.send_response(429); self.send_header("Retry-After", "0")
                self.send_header("Content-Length", "0"); self.end_headers(); return
            raw = json.dumps({"text": "recovered"}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from agentordeal.adapters.http import HttpAdapter
    ad = HttpAdapter(f"http://127.0.0.1:{srv.server_address[1]}/agent", backoff=0.01)
    r = ad.invoke("hello", {})
    srv.shutdown()
    assert r.text == "recovered" and counts["n"] == 3 and ad.last_attempts == 3

def test_http_non_transient_error_fails_closed():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *x): pass
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(400); self.send_header("Content-Length", "0"); self.end_headers()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from agentordeal.adapters.http import HttpAdapter
    ad = HttpAdapter(f"http://127.0.0.1:{srv.server_address[1]}/agent", backoff=0.01)
    r = ad.invoke("hello", {})
    srv.shutdown()
    assert r.text.startswith("[http adapter error") and ad.last_attempts == 1

def test_cli_diff_exit_codes(tmp_path):
    from agentordeal.cli import main
    v, h = run("demo-vulnerable"), run("demo-hardened")
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(v)); pb.write_text(json.dumps(h))
    assert main(["diff", str(pa), str(pb), "--fail-on-regression"]) == 0
    assert main(["diff", str(pb), str(pa), "--fail-on-regression"]) == 1

def test_version_bumped():
    import agentordeal
    assert agentordeal.__version__ == "0.5.0"
    wf = open(pathlib.Path(__file__).parent.parent / "examples/leaderboard-update.yml").read()
    assert "run_leaderboard.py" in wf and "upload-artifact" in wf and "cron" in wf
