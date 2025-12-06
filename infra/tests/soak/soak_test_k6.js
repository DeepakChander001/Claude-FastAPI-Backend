/**
 * k6 Soak Test for Claude Proxy
 * ============================================================================
 * Long-duration test to identify memory leaks, connection exhaustion, etc.
 *
 * Usage:
 *   k6 run --env TARGET_URL=http://localhost:8000 --env DURATION=2h infra/tests/soak/soak_test_k6.js
 *   k6 run --summary-export=soak_results.json infra/tests/soak/soak_test_k6.js
 *
 * Environment Variables:
 *   TARGET_URL - Target API base URL
 *   API_KEY    - API key for authentication
 *   DURATION   - Test duration (default: 2h)
 *   RPS        - Steady-state RPS (default: 50)
 * ============================================================================
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Counter } from 'k6/metrics';

const TARGET_URL = __ENV.TARGET_URL || 'REPLACE_ME_TARGET_URL';
const API_KEY = __ENV.API_KEY || 'REPLACE_ME_API_KEY';
const DURATION = __ENV.DURATION || '2h';
const RPS = parseInt(__ENV.RPS || '50');

const errors = new Rate('errors');
const requests = new Counter('total_requests');

export const options = {
    scenarios: {
        soak: {
            executor: 'constant-arrival-rate',
            rate: RPS,
            timeUnit: '1s',
            duration: DURATION,
            preAllocatedVUs: 100,
            maxVUs: 200,
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<1000'],  // Relaxed for soak
        http_req_failed: ['rate<0.02'],     // 2% error threshold
        errors: ['rate<0.05'],
    },
};

const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
};

export default function () {
    requests.add(1);

    // Health check (lightweight)
    const healthRes = http.get(`${TARGET_URL}/health`);
    const healthOk = check(healthRes, {
        'health ok': (r) => r.status === 200,
    });
    errors.add(!healthOk);

    sleep(0.1);

    // Enqueue request
    const payload = JSON.stringify({
        prompt: `Soak test request at ${Date.now()}`,
        max_tokens: 50,
    });

    const enqueueRes = http.post(`${TARGET_URL}/api/enqueue`, payload, { headers });
    const enqueueOk = check(enqueueRes, {
        'enqueue ok': (r) => r.status === 200 || r.status === 202,
    });
    errors.add(!enqueueOk);

    sleep(0.5);
}

export function setup() {
    console.log('=== SOAK TEST STARTING ===');
    console.log(`Target: ${TARGET_URL}`);
    console.log(`Duration: ${DURATION}`);
    console.log(`RPS: ${RPS}`);
}

export function teardown(data) {
    console.log('=== SOAK TEST COMPLETE ===');
}
