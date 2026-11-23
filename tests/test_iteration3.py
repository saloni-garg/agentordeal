import json
from agentordeal.runner import run
from agentordeal.scorecard import to_badge_svg, badge_markdown
from agentordeal.cli import main

def test_badge_svg_content():
    svg=to_badge_svg(run("demo-hardened"))
    assert svg.startswith("<svg") and "A - 100.0/100" in svg and "#2da44e" in svg

def test_badge_color_f():
    assert "#cf222e" in to_badge_svg(run("demo-vulnerable"))

def test_badge_markdown():
    assert "AgentOrdeal: A" in badge_markdown(run("demo-hardened"))

def test_cli_badge_from_target(tmp_path):
    out=tmp_path/"badge.svg"
    assert main(["badge","--target","demo-hardened","--out",str(out)])==0
    assert "<svg" in out.read_text()

def test_cli_badge_from_scorecard(tmp_path):
    card=run("demo-vulnerable"); sc=tmp_path/"s.json"; sc.write_text(json.dumps(card))
    out=tmp_path/"b.svg"; assert main(["badge","--scorecard",str(sc),"--out",str(out)])==0
    assert "F - 12.3/100" in out.read_text()
