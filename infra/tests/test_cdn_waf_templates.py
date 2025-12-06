import pytest
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'infra', 'scripts'))

def test_cloudfront_tf_is_valid():
    path = "infra/cdn/cloudfront.tf.example"
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "aws_cloudfront_distribution" in content
    assert "viewer_protocol_policy" in content

def test_waf_policy_is_valid_json():
    path = "infra/waf/wafv2_policy.json.example"
    with open(path) as f:
        data = json.load(f)
    assert "Name" in data
    assert "Rules" in data
    assert len(data["Rules"]) >= 1

def test_route53_tf_is_valid():
    path = "infra/dns/route53.tf.example"
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "aws_route53_record" in content

def test_s3_bucket_tf_is_valid():
    path = "infra/static/s3_bucket.tf.example"
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "aws_s3_bucket" in content

def test_waf_dryrun_report():
    from infra.scripts.waf_dryrun_report import load_policy, load_logs, simulate_rules
    
    policy = load_policy("infra/waf/wafv2_policy.json.example")
    logs = load_logs("nonexistent.json")  # Uses default sample
    
    results = simulate_rules(policy, logs)
    
    assert "total_requests" in results
    assert "rule_matches" in results
    assert "top_ips" in results

def test_cloudfront_invalidate_script_exists():
    path = "infra/scripts/cloudfront_invalidate.sh"
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "create-invalidation" in content

def test_create_dns_record_script_exists():
    path = "infra/scripts/create_dns_record.sh"
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "change-resource-record-sets" in content
