import pytest
import subprocess
import os
import sys

# Add infra/scripts to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'infra', 'scripts'))

@pytest.mark.skipif(sys.platform == "win32", reason="Shell scripts require Unix")
def test_deploy_release_dry_run():
    """Test deploy_release.sh runs in dry-run mode."""
    result = subprocess.run(
        ["sh", "infra/scripts/deploy_release.sh", "--env", "staging", "--image", "test:latest", "--strategy", "rolling"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    
    output = result.stdout + result.stderr
    
    # Should contain the expected commands
    assert "register-task-definition" in output or "Deploy Release" in output
    assert "update-service" in output or "Rolling Deployment" in output

def test_wait_for_deployment_dry_run():
    """Test wait_for_deployment.py in dry-run mode."""
    os.environ["DRY_RUN"] = "true"
    
    from infra.scripts.wait_for_deployment import wait_for_deployment
    
    result = wait_for_deployment("test-cluster", "test-service", timeout=5)
    assert result is True

def test_smoke_test_structure():
    """Test smoke_test.sh exists and is valid shell."""
    path = "infra/scripts/smoke_test.sh"
    assert os.path.exists(path)
    
    with open(path) as f:
        content = f.read()
    assert "#!/bin/sh" in content
    assert "/health" in content

def test_rollback_script_structure():
    """Test rollback_release.sh contains expected commands."""
    path = "infra/scripts/rollback_release.sh"
    with open(path) as f:
        content = f.read()
    assert "list-task-definitions" in content
    assert "update-service" in content
