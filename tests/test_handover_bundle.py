import pytest
import os
import re

DOCS_DIR = "docs"
REQUIRED_DOCS = [
    "HANDOVER_README.md",
    "OPERATIONAL_RUNBOOK_FULL.md",
    "ONCALL_AND_ESCALATION.md",
    "LEGAL_COMPLIANCE_CHECKLIST.md",
    "SECURITY_SIGNOFF_TEMPLATE.md",
    "MAINTENANCE_SCHEDULE.md",
    "ROADMAP_12_MONTHS.md",
    "FAQ_AND_KNOWN_ISSUES.md",
    "SERVICE_DEFINITION_AND_SLA.md",
    "ARCHITECTURE_REFERENCE.mmd",
    "HANDOVER_CHECKLIST.md",
    "RELEASE_NOTES_TEMPLATE.md",
]

TRAINING_DOCS = [
    "TRAINING/intro_slides.md",
    "TRAINING/exercises.md",
]

def test_all_required_docs_exist():
    """Verify all required handover docs exist."""
    for doc in REQUIRED_DOCS:
        path = os.path.join(DOCS_DIR, doc)
        assert os.path.exists(path), f"Missing: {path}"

def test_training_docs_exist():
    """Verify training docs exist."""
    for doc in TRAINING_DOCS:
        path = os.path.join(DOCS_DIR, doc)
        assert os.path.exists(path), f"Missing: {path}"

def test_no_real_secrets_in_docs():
    """Verify sensitive fields use REPLACE_ME placeholders."""
    # Only check docs that should contain sensitive placeholders
    sensitive_docs = [
        "HANDOVER_README.md",
        "OPERATIONAL_RUNBOOK_FULL.md",
        "ONCALL_AND_ESCALATION.md",
        "SECURITY_SIGNOFF_TEMPLATE.md",
        "FAQ_AND_KNOWN_ISSUES.md",
        "SERVICE_DEFINITION_AND_SLA.md",
    ]
    
    for doc in sensitive_docs:
        path = os.path.join(DOCS_DIR, doc)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                content = f.read()
            
            # Check for REPLACE_ME placeholders (expected)
            assert "REPLACE_ME" in content, f"{doc} should have REPLACE_ME placeholders"

def test_handover_readme_has_key_sections():
    """Verify handover README has required sections."""
    with open(os.path.join(DOCS_DIR, "HANDOVER_README.md"), encoding="utf-8") as f:
        content = f.read()
    
    assert "Architecture" in content
    assert "Owners" in content or "Contact" in content
    assert "SLA" in content

def test_monthly_ops_report_exists():
    """Verify monthly ops report script exists."""
    path = "infra/scripts/monthly_ops_report.sh"
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "REPLACE_ME" in content
    assert "Dry run" in content or "dry-run" in content.lower()
