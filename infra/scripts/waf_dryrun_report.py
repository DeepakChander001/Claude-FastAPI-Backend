"""
waf_dryrun_report.py - Simulate WAF rules against sample logs
============================================================================
Usage:
    python waf_dryrun_report.py --policy infra/waf/wafv2_policy.json.example --logs sample_logs.json
============================================================================
This is an OFFLINE simulator - no AWS calls.
"""
import json
import sys
import os
import re

def load_policy(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

def load_logs(path: str) -> list:
    if not os.path.exists(path):
        # Return sample logs for testing
        return [
            {"ip": "192.168.1.1", "path": "/api/enqueue", "method": "POST", "user_agent": "Mozilla/5.0"},
            {"ip": "192.168.1.1", "path": "/api/enqueue", "method": "POST", "user_agent": "Mozilla/5.0"},
            {"ip": "10.0.0.1", "path": "/api/generate", "method": "POST", "user_agent": "curl/7.68"},
            {"ip": "192.168.1.1", "path": "/static/app.js", "method": "GET", "user_agent": "Mozilla/5.0"},
        ]
    with open(path) as f:
        return json.load(f)

def simulate_rules(policy: dict, logs: list) -> dict:
    """Simulate WAF rules against logs."""
    results = {
        "total_requests": len(logs),
        "rule_matches": {},
        "top_ips": {}
    }
    
    # Count IPs for rate limiting simulation
    ip_counts = {}
    for log in logs:
        ip = log.get("ip", "unknown")
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    results["top_ips"] = dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # Simulate rule matches
    for rule in policy.get("Rules", []):
        rule_name = rule.get("Name", "Unknown")
        results["rule_matches"][rule_name] = 0
        
        # Rate limit rule
        if "RateBasedStatement" in rule.get("Statement", {}):
            limit = rule["Statement"]["RateBasedStatement"].get("Limit", 100)
            for ip, count in ip_counts.items():
                if count > limit / 60:  # Simplified threshold
                    results["rule_matches"][rule_name] += count
        
        # Geo block (simulated - check if any geo markers)
        if "GeoMatchStatement" in rule.get("Statement", {}):
            # Would match based on geo data - simulated as 0
            pass
    
    return results

def main():
    policy_path = "infra/waf/wafv2_policy.json.example"
    logs_path = "sample_logs.json"
    
    # Parse args
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--policy" and i + 1 < len(args):
            policy_path = args[i + 1]
        elif arg == "--logs" and i + 1 < len(args):
            logs_path = args[i + 1]
    
    print(f"Loading policy: {policy_path}")
    policy = load_policy(policy_path)
    
    print(f"Loading logs: {logs_path}")
    logs = load_logs(logs_path)
    
    print("Simulating WAF rules...")
    results = simulate_rules(policy, logs)
    
    # Write report
    report_path = "waf_dryrun_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(json.dumps(results, indent=2))
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
