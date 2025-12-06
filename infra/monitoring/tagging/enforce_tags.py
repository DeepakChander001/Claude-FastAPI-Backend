"""
enforce_tags.py - Validate resources have required tags
============================================================================
Required env: FAIL_ON_MISSING=true to exit non-zero on missing tags
Usage:
    python enforce_tags.py --path infra/terraform/
    python enforce_tags.py --plan-json tfplan.json
============================================================================
"""
import os
import sys
import json
import re

REQUIRED_TAGS = ["owner", "project", "env"]
FAIL_ON_MISSING = os.environ.get("FAIL_ON_MISSING", "false").lower() == "true"

def scan_tf_files(path: str) -> list:
    """Scan Terraform files for resources missing tags."""
    issues = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".tf") or file.endswith(".tf.example"):
                filepath = os.path.join(root, file)
                with open(filepath) as f:
                    content = f.read()
                
                # Find resource blocks
                resources = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', content)
                
                for resource_type, resource_name in resources:
                    # Check if tags block exists
                    if "tags" not in content:
                        issues.append({
                            "file": filepath,
                            "resource": f"{resource_type}.{resource_name}",
                            "missing": REQUIRED_TAGS
                        })
    
    return issues

def scan_plan_json(path: str) -> list:
    """Scan Terraform plan JSON for missing tags."""
    issues = []
    
    with open(path) as f:
        plan = json.load(f)
    
    for resource in plan.get("planned_values", {}).get("root_module", {}).get("resources", []):
        tags = resource.get("values", {}).get("tags", {})
        missing = [tag for tag in REQUIRED_TAGS if tag not in tags]
        
        if missing:
            issues.append({
                "resource": resource.get("address"),
                "missing": missing
            })
    
    return issues

def main():
    path = "infra/terraform/"
    plan_json = None
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--path" and i + 1 < len(args):
            path = args[i + 1]
        elif arg == "--plan-json" and i + 1 < len(args):
            plan_json = args[i + 1]
    
    if plan_json and os.path.exists(plan_json):
        issues = scan_plan_json(plan_json)
    else:
        issues = scan_tf_files(path)
    
    print(f"Scanned: {path or plan_json}")
    print(f"Required tags: {REQUIRED_TAGS}")
    print(f"Issues found: {len(issues)}")
    
    for issue in issues:
        print(f"  - {issue}")
    
    if issues and FAIL_ON_MISSING:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
