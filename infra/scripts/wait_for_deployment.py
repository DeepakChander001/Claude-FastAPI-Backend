"""
wait_for_deployment.py - Wait for ECS deployment to complete
Usage:
    python wait_for_deployment.py --cluster claude-proxy --service api-service
    DRY_RUN=true python wait_for_deployment.py --cluster test --service test
"""
import os
import sys
import time
import json

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"
TIMEOUT = int(os.environ.get("WAIT_TIMEOUT", "300"))

def get_service_status(cluster: str, service: str) -> dict:
    """Get ECS service deployment status."""
    if DRY_RUN:
        # Return fake success response
        return {
            "services": [{
                "serviceName": service,
                "runningCount": 2,
                "desiredCount": 2,
                "deployments": [{
                    "status": "PRIMARY",
                    "runningCount": 2,
                    "desiredCount": 2
                }]
            }]
        }
    
    # Real implementation would use boto3
    # import boto3
    # client = boto3.client("ecs")
    # return client.describe_services(cluster=cluster, services=[service])
    return {}

def wait_for_deployment(cluster: str, service: str, timeout: int = TIMEOUT) -> bool:
    """Wait for deployment to stabilize."""
    print(f"Waiting for {service} in {cluster} to stabilize...")
    
    start = time.time()
    while time.time() - start < timeout:
        status = get_service_status(cluster, service)
        
        if status.get("services"):
            svc = status["services"][0]
            running = svc.get("runningCount", 0)
            desired = svc.get("desiredCount", 0)
            
            print(f"  Running: {running}/{desired}")
            
            if running >= desired and desired > 0:
                print("Deployment complete!")
                return True
        
        time.sleep(10)
    
    print("Timeout waiting for deployment!")
    return False

if __name__ == "__main__":
    cluster = "claude-proxy"
    service = "api-service"
    
    # Parse args
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--cluster" and i + 1 < len(args):
            cluster = args[i + 1]
        elif arg == "--service" and i + 1 < len(args):
            service = args[i + 1]
    
    success = wait_for_deployment(cluster, service)
    sys.exit(0 if success else 1)
