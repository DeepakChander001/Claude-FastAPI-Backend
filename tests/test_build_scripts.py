import pytest
import os
from infra.ci.verify_pinned_base import verify_pinned_base
from infra.ci.check_image_size import check_image_size

def test_verify_pinned_base_success(tmp_path):
    d = tmp_path / "Dockerfile"
    d.write_text("FROM python:3.11-slim@sha256:1234567890abcdef\nCMD python")
    
    # Should not raise exception
    verify_pinned_base(str(d))

def test_verify_pinned_base_failure(tmp_path):
    d = tmp_path / "Dockerfile"
    d.write_text("FROM python:3.11-slim\nCMD python")
    
    # Should exit with 1
    with pytest.raises(SystemExit) as e:
        verify_pinned_base(str(d))
    assert e.value.code == 1

def test_check_image_size_success():
    # Default mock size is 150, limit is 200
    check_image_size()

def test_check_image_size_failure():
    os.environ["MAX_IMAGE_SIZE_MB"] = "100"
    try:
        with pytest.raises(SystemExit) as e:
            check_image_size()
        assert e.value.code == 1
    finally:
        del os.environ["MAX_IMAGE_SIZE_MB"]
