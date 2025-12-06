import pytest
import os
import json
import subprocess
import sys

def test_k6_smoke_test_has_target_placeholder():
    path = "infra/tests/load/k6/smoke_and_rps_test.js"
    with open(path) as f:
        content = f.read()
    assert "REPLACE_ME_TARGET_URL" in content
    assert "TARGET_URL" in content
    assert "thresholds" in content

def test_k6_soak_test_has_duration():
    path = "infra/tests/soak/soak_test_k6.js"
    with open(path) as f:
        content = f.read()
    assert "DURATION" in content
    assert "2h" in content

def test_locust_file_has_api_key():
    path = "infra/tests/load/locust/locustfile.py"
    with open(path) as f:
        content = f.read()
    assert "API_KEY" in content
    assert "HttpUser" in content

@pytest.mark.skipif(sys.platform == "win32", reason="Shell scripts require Unix")
def test_run_load_test_dry_run():
    result = subprocess.run(
        ["sh", "infra/scripts/run_load_test.sh", "--engine", "k6", "--target", "http://test"],
        capture_output=True,
        text=True
    )
    output = result.stdout + result.stderr
    assert "Load Test Runner" in output or "k6 run" in output

def test_slo_definitions_exist():
    path = "infra/slo/SLO_AND_ALERTS.md"
    with open(path) as f:
        content = f.read()
    assert "99.9%" in content
    assert "Error Budget" in content

def test_cutover_runbook_has_steps():
    path = "infra/runbooks/PRODUCTION_CUTOVER.md"
    with open(path) as f:
        content = f.read()
    assert "Pre-Cutover" in content
    assert "Rollback Triggers" in content
    assert "Post-Cutover" in content

def test_rollback_playbook_exists():
    path = "infra/runbooks/ROLLBACK_PLAYBOOK.md"
    with open(path) as f:
        content = f.read()
    assert "Quick Rollback" in content
    assert "update-service" in content
