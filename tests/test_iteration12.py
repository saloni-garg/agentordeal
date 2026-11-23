"""Iteration 12: packaging and distribution readiness (static checks;
the wheel build + clean-venv install is verified in the iteration log)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _read(p):
    with open(os.path.join(ROOT, p)) as f: return f.read()

def test_dockerfile_present_and_valid_shape():
    d = _read("Dockerfile")
    assert d.startswith("FROM python:3.12")
    assert "pip install" in d and 'ENTRYPOINT ["agentordeal"]' in d
    assert os.path.exists(os.path.join(ROOT, ".dockerignore"))

def test_action_branding_and_outputs():
    a = _read("action.yml")
    assert "branding:" in a and 'icon: "shield"' in a
    for out in ("score:", "grade:", "scorecard-path:"):
        assert out in a
    assert "GITHUB_OUTPUT" in a
    assert "formats:" in a  # documented input

def test_contributor_and_security_surface():
    for p in ("CONTRIBUTING.md", "SECURITY.md", "MANIFEST.in", ".pre-commit-config.yaml",
              ".github/ISSUE_TEMPLATE/bug_report.md",
              ".github/ISSUE_TEMPLATE/feature_request.md",
              ".github/ISSUE_TEMPLATE/scenario_proposal.md"):
        assert os.path.exists(os.path.join(ROOT, p)), p
    assert "standard-library only" in _read("CONTRIBUTING.md")
    assert "14-day" in _read("SECURITY.md")

def test_manifest_covers_docs_and_leaderboard():
    m = _read("MANIFEST.in")
    assert "docs" in m and "leaderboard" in m and "action.yml" in m

def test_version_consistency():
    import agentordeal
    assert f'version = "{agentordeal.__version__}"' in _read("pyproject.toml")
