"""
Tests to enforce that Final Quality Gate is STRICT and has no bypasses.
© MANSOUR — WOS-M. All rights reserved.
"""
import re
from pathlib import Path


CI_PATH = Path(".github/workflows/ci.yml")


def test_no_true_bypass_in_quality_gates():
    """No '|| true' or '|| echo' bypasses allowed in quality gates."""
    ci = CI_PATH.read_text(encoding="utf-8")

    forbidden = [
        "flake8 core modules integrations views tests main.py || true",
        "mypy core modules integrations views main.py || true",
        "pip_audit -r requirements.txt || true",
        "discord_runtime_smoke.py || echo",
        "Runtime QA skipped",
    ]

    for item in forbidden:
        assert item not in ci, f"Forbidden CI bypass found: {item}"


def test_discord_runtime_qa_requires_real_secret():
    """Discord Runtime QA must require real Discord bot token from secrets."""
    ci = CI_PATH.read_text(encoding="utf-8")

    assert "discord-runtime-qa:" in ci, "discord-runtime-qa job must exist"
    assert "Discord Runtime QA Live" in ci, "Job must be named Discord Runtime QA Live"
    assert "secrets.DISCORD_BOT_TOKEN" in ci, "Must use secrets.DISCORD_BOT_TOKEN"

    # Find the discord-runtime-qa section
    runtime_section = ci.split("discord-runtime-qa:", 1)[1]
    # Get just the job definition (until next job or end)
    if "jobs:" in runtime_section:
        runtime_section = runtime_section.split("jobs:")[0]

    assert "test_token_for_ci" not in runtime_section, "test_token_for_ci must not be used"
    assert "|| echo" not in runtime_section, "|| echo bypass not allowed"
    assert "Runtime QA skipped" not in runtime_section, "Runtime QA skipped not allowed"
    assert "run: python scripts/discord_runtime_smoke.py" in runtime_section, "Must run smoke test"


def test_runtime_smoke_does_not_accept_test_token():
    """Runtime smoke test must reject test_token_for_ci with exit code 1."""
    smoke = Path("scripts/discord_runtime_smoke.py").read_text(encoding="utf-8")

    # Must contain rejection logic
    assert "test_token_for_ci" in smoke, "Script must mention test_token_for_ci"
    assert re.search(r"test_token_for_ci.*sys\.exit\(1\)", smoke, re.DOTALL), (
        "test_token_for_ci must fail with sys.exit(1)"
    )

    # Must NOT contain bypass logic
    assert "Environment check PASSED (test mode)" not in smoke, "Test mode bypass not allowed"
    assert "skipping actual connection" not in smoke, "Skip bypass not allowed"
    assert "Runtime QA skipped" not in smoke, "Skip message not allowed"


def test_dependency_audit_is_strict():
    """pip-audit must run without '|| true' bypass."""
    ci = CI_PATH.read_text(encoding="utf-8")
    assert "python -m pip_audit -r requirements.txt" in ci, "pip-audit must be present"
    assert "python -m pip_audit -r requirements.txt || true" not in ci, "|| true bypass not allowed"


def test_lint_is_strict():
    """flake8 must run without '|| true' bypass."""
    ci = CI_PATH.read_text(encoding="utf-8")
    lint_line = "python -m flake8 core modules integrations views tests main.py"
    assert lint_line in ci, "flake8 must be present"
    assert lint_line + " || true" not in ci, "|| true bypass not allowed"


def test_typecheck_is_strict():
    """mypy must run without '|| true' bypass."""
    ci = CI_PATH.read_text(encoding="utf-8")
    typecheck_line = "python -m mypy core modules integrations views main.py"
    assert typecheck_line in ci, "mypy must be present"
    assert typecheck_line + " || true" not in ci, "|| true bypass not allowed"
