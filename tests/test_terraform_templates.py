import pytest
import json
import os
import subprocess

def test_task_definition_template_is_valid_json():
    path = "infra/terraform/modules/ecs_service/task_definition_template.json"
    with open(path, "r") as f:
        data = json.load(f)
    assert "family" in data
    assert "containerDefinitions" in data

def test_variables_have_descriptions():
    path = "infra/terraform/variables.tf"
    with open(path, "r") as f:
        content = f.read()
    assert "description" in content
    assert "aws_region" in content

def test_render_taskdef_offline():
    # Simulate rendering by replacing placeholders
    template_path = "infra/terraform/modules/ecs_service/task_definition_template.json"
    
    with open(template_path, "r") as f:
        template = f.read()
    
    rendered = template.replace("REPLACE_ME_IMAGE", "test-image")
    rendered = rendered.replace("REPLACE_ME_REGION", "us-east-1")
    
    # Should still be valid JSON
    data = json.loads(rendered)
    assert data["containerDefinitions"][0]["image"] == "test-image"

def test_main_tf_includes_modules():
    path = "infra/terraform/main.tf"
    with open(path, "r") as f:
        content = f.read()
    assert "module \"ecs_cluster\"" in content
    assert "module \"alb\"" in content
    assert "module \"sqs\"" in content
