"""
Locust Load Test for Claude Proxy
============================================================================
Usage:
    locust -f infra/tests/load/locust/locustfile.py --headless -u 10 -r 2 --run-time 1m --host http://localhost:8000

Environment Variables:
    LOCUST_TARGET  - Target API base URL
    LOCUST_API_KEY - API key for authentication
    USERS          - Number of concurrent users (default: 10)
    SPAWN_RATE     - Users spawned per second (default: 2)
============================================================================
"""
import os
import time
from locust import HttpUser, task, between, events

API_KEY = os.environ.get("LOCUST_API_KEY", "REPLACE_ME_API_KEY")

class APIUser(HttpUser):
    """Simulates a typical API user flow."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when user starts."""
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        }
    
    @task(3)
    def health_check(self):
        """Check health endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200 and "status" in response.text:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(5)
    def enqueue_request(self):
        """Submit an enqueue request and poll for result."""
        payload = {
            "prompt": "Load test prompt",
            "max_tokens": 50,
        }
        
        with self.client.post("/api/enqueue", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code in [200, 202]:
                response.success()
                try:
                    data = response.json()
                    request_id = data.get("request_id")
                    if request_id:
                        self.poll_status(request_id)
                except:
                    pass
            else:
                response.failure(f"Enqueue failed: {response.status_code}")
    
    def poll_status(self, request_id: str, max_attempts: int = 3):
        """Poll for request status."""
        for _ in range(max_attempts):
            with self.client.get(f"/api/request/{request_id}", headers=self.headers, catch_response=True, name="/api/request/[id]") as response:
                if response.status_code == 200:
                    response.success()
                    return
            time.sleep(1)


class StreamUser(HttpUser):
    """Tests streaming endpoints."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        }
    
    @task
    def test_streaming(self):
        """Test streaming endpoint (if available)."""
        payload = {
            "prompt": "Stream test",
            "stream": True,
        }
        
        # Note: Locust doesn't natively support SSE well
        # This is a basic check that the endpoint responds
        with self.client.post("/api/stream", json=payload, headers=self.headers, catch_response=True, timeout=30) as response:
            if response.status_code in [200, 404]:  # 404 is acceptable if streaming not implemented
                response.success()
            else:
                response.failure(f"Stream failed: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting load test against: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test completed.")
