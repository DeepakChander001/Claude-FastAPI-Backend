import pytest
import os
import json
import yaml
import sys

def test_otel_config_is_valid_yaml():
    path = "infra/monitoring/otel/otel-collector-config.yaml"
    with open(path) as f:
        config = yaml.safe_load(f)
    assert "receivers" in config
    assert "exporters" in config
    assert "service" in config

def test_prometheus_config_is_valid_yaml():
    path = "infra/monitoring/prometheus/prometheus.yml.example"
    with open(path) as f:
        config = yaml.safe_load(f)
    assert "scrape_configs" in config
    assert "global" in config

def test_grafana_dashboards_are_valid_json():
    for dashboard in ["api_overview.json", "worker_overview.json"]:
        path = f"infra/monitoring/grafana/dashboards/{dashboard}"
        with open(path) as f:
            data = json.load(f)
        assert "title" in data
        assert "panels" in data

def test_cloudwatch_alarms_tf_has_resources():
    path = "infra/monitoring/alerts/cloudwatch_alarms.tf.example"
    with open(path) as f:
        content = f.read()
    assert "aws_cloudwatch_metric_alarm" in content
    assert "alarm_actions" in content

def test_alertmanager_rules_are_valid_yaml():
    path = "infra/monitoring/alerts/alertmanager/alert_rules.yml.example"
    with open(path) as f:
        config = yaml.safe_load(f)
    assert "groups" in config

def test_enforce_tags_runs():
    sys.path.insert(0, "infra/monitoring/tagging")
    from enforce_tags import scan_tf_files
    
    issues = scan_tf_files("infra/terraform/")
    assert isinstance(issues, list)

def test_autoscaling_tf_has_policies():
    path = "infra/monitoring/autoscaling/ecs_scaling.tf.example"
    with open(path) as f:
        content = f.read()
    assert "aws_appautoscaling_target" in content
    assert "aws_appautoscaling_policy" in content
