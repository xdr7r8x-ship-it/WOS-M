"""
Tests to enforce that QA_DISCORD_CHECKLIST.md is properly completed.
© MANSOUR — WOS-M. All rights reserved.
"""
from pathlib import Path


def test_qa_checklist_exists():
    """QA_DISCORD_CHECKLIST.md must exist."""
    path = Path("QA_DISCORD_CHECKLIST.md")
    assert path.exists(), "QA_DISCORD_CHECKLIST.md is missing"


def test_qa_checklist_has_no_unchecked_items():
    """QA checklist must not have unchecked items."""
    path = Path("QA_DISCORD_CHECKLIST.md")
    content = path.read_text(encoding="utf-8")

    assert "⬜" not in content, "QA checklist still has unchecked items"
    assert "| | |" not in content, "Empty cells found in checklist"


def test_qa_checklist_has_evidence():
    """QA checklist must include real evidence markers."""
    content = Path("QA_DISCORD_CHECKLIST.md").read_text(encoding="utf-8")

    evidence_markers = [
        "BOT_READY",
        "message id",
        "screenshot:",
        "log:",
        "db row",
        "audit_logs",
        "Code:",
        "Schema validated",
    ]

    assert any(marker in content for marker in evidence_markers), (
        "QA checklist must include real evidence markers"
    )


def test_qa_checklist_final_signoff_completed():
    """Final sign-off must be complete."""
    content = Path("QA_DISCORD_CHECKLIST.md").read_text(encoding="utf-8")

    required_signoffs = [
        "- [x] All tests passed",
        "- [x] No placeholder messages",
        "- [x] All buttons functional",
        "- [x] Real redemption works",
        "- [x] Permissions enforced",
        "- [x] Audit logs recorded",
    ]

    for signoff in required_signoffs:
        assert signoff in content, f"Missing signoff: {signoff}"


def test_qa_checklist_critical_tests_pass():
    """Critical tests must all show PASS."""
    content = Path("QA_DISCORD_CHECKLIST.md").read_text(encoding="utf-8")

    critical_tests = [
        "Run `/wos`",
        "alliance_add",
        "alliance_list",
        "alliance_edit",
        "alliance_delete",
        "player_add",
        "player_search",
        "player_list",
        "gift_add",
        "gift_redeem_single",
    ]

    for test in critical_tests:
        # Each test should have PASS status
        test_line = [line for line in content.split("\n") if test in line]
        if test_line:
            assert "PASS" in test_line[0] or "pass" in test_line[0].lower(), (
                f"Critical test '{test}' must have PASS status"
            )
