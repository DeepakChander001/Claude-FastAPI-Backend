/**
 * k6 Smoke and RPS Load Test for Claude Proxy
 * ============================================================================
 * Usage:
 *   k6 run infra/tests/load/k6/smoke_and_rps_test.js
 *   k6 run --env TARGET_URL=http://localhost:8000 --env API_KEY=test-key infra/tests/load/k6/smoke_and_rps_test.js
 *
 * Environment Variables:
 *   TARGET_URL - Target API base URL (default: REPLACE_ME_TARGET_URL)
 *   API_KEY    - API key for authentication
 *   DURATION   - Test duration (default: 1m)
 *   RPS        - Requests per second for rps scenario (default: 50)
 * ============================================================================
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const enqueueDuration = new Trend('enqueue_duration');

// Configuration from environment
const TARGET_URL = __ENV.TARGET_URL || 'REPLACE_ME_TARGET_URL';
const API_KEY = __ENV.API_KEY || 'REPLACE_ME_API_KEY';
const DURATION = __ENV.DURATION || '1m';
const RPS = parseInt(__ENV.RPS || '50');

// Test options
export const options = {
    scenarios: {
        smoke: {
            executor: 'constant-vus',
            vus: 10,
            duration: DURATION,
            tags: { scenario: 'smoke' },
        },
        rps: {
            executor: 'constant-arrival-rate',
            rate: RPS,
            timeUnit: '1s',
            duration: DURATION,
            preAllocatedVUs: 50,
            maxVUs: 100,
            startTime: '1m',
            tags: { scenario: 'rps' },
        },
    },
    thresholds: {
        // SLO thresholds
        http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95th < 500ms, 99th < 1s
        http_req_failed: ['rate<0.01'],                  // Error rate < 1%
        errors: ['rate<0.05'],                           // Custom error rate < 5%
    },
};

// Headers
const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
};

// Test functions
export default function () {
    // Test 1: Health Check
    const healthRes = http.get(`${TARGET_URL}/health`);
    check(healthRes, {
        'health: status 200': (r) => r.status === 200,
        'health: has status field': (r) => r.json('status') !== undefined,
    });

    sleep(0.5);

    // Test 2: Enqueue Request
    const payload = JSON.stringify({
        prompt: 'Hello, this is a load test message.',
        max_tokens: 100,
    });

    const enqueueRes = http.post(`${TARGET_URL}/api/enqueue`, payload, { headers });

    const enqueueSuccess = check(enqueueRes, {
        'enqueue: status 200 or 202': (r) => r.status === 200 || r.status === 202,
        'enqueue: has request_id': (r) => {
            try {
                return r.json('request_id') !== undefined;
            } catch {
                return false;
            }
        },
    });

    errorRate.add(!enqueueSuccess);
    enqueueDuration.add(enqueueRes.timings.duration);

    sleep(1);
}

// Setup function
export function setup() {
    console.log(`Target URL: ${TARGET_URL}`);
    console.log(`Duration: ${DURATION}`);
    console.log(`RPS: ${RPS}`);
}

// Teardown function
export function teardown(data) {
    console.log('Load test completed.');
}
