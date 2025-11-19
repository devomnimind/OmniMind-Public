// k6 Load Test Script for OmniMind API
// Run with: k6 run tests/load_tests/api_load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const taskDuration = new Trend('task_duration');

// Test configuration
export const options = {
    // Stages define different load levels over time
    stages: [
        { duration: '30s', target: 10 },  // Ramp up to 10 users
        { duration: '1m', target: 50 },   // Ramp up to 50 users
        { duration: '2m', target: 50 },   // Stay at 50 users
        { duration: '30s', target: 100 }, // Spike to 100 users
        { duration: '1m', target: 100 },  // Stay at 100 users
        { duration: '30s', target: 0 },   // Ramp down to 0 users
    ],
    
    // Thresholds define SLAs
    thresholds: {
        'http_req_duration': ['p(95)<500'],  // 95% of requests must complete under 500ms
        'http_req_failed': ['rate<0.1'],     // Less than 10% of requests can fail
        'errors': ['rate<0.1'],              // Error rate must be below 10%
    },
};

// Base URL
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test credentials (from environment or defaults)
const USERNAME = __ENV.USERNAME || 'test_user';
const PASSWORD = __ENV.PASSWORD || 'test_pass';

// Encode credentials for Basic Auth
const credentials = `${USERNAME}:${PASSWORD}`;
const encodedCredentials = encoding.b64encode(credentials);

const headers = {
    'Authorization': `Basic ${encodedCredentials}`,
    'Content-Type': 'application/json',
};

export default function () {
    // Test 1: Health Check (no auth required)
    let healthResponse = http.get(`${BASE_URL}/health`);
    check(healthResponse, {
        'health check status is 200': (r) => r.status === 200,
        'health check has status field': (r) => JSON.parse(r.body).status !== undefined,
    });
    errorRate.add(healthResponse.status !== 200);
    
    sleep(1);
    
    // Test 2: Get Metrics (requires auth)
    let metricsResponse = http.get(`${BASE_URL}/metrics`, { headers: headers });
    check(metricsResponse, {
        'metrics status is 200': (r) => r.status === 200,
        'metrics has backend field': (r) => JSON.parse(r.body).backend !== undefined,
    });
    errorRate.add(metricsResponse.status !== 200);
    
    sleep(1);
    
    // Test 3: Get Status (requires auth)
    let statusResponse = http.get(`${BASE_URL}/status`, { headers: headers });
    check(statusResponse, {
        'status check is 200': (r) => r.status === 200,
        'status has plan field': (r) => JSON.parse(r.body).plan !== undefined,
    });
    errorRate.add(statusResponse.status !== 200);
    
    sleep(1);
    
    // Test 4: Task Orchestration (requires auth, more intensive)
    const taskPayload = JSON.stringify({
        task: `Load test task ${__VU}-${__ITER}`,
        max_iterations: 1,
    });
    
    const startTime = new Date().getTime();
    let taskResponse = http.post(
        `${BASE_URL}/tasks/orchestrate`,
        taskPayload,
        { headers: headers, timeout: '30s' }
    );
    const endTime = new Date().getTime();
    const duration = endTime - startTime;
    
    check(taskResponse, {
        'task orchestration status is 200': (r) => r.status === 200,
        'task orchestration has success field': (r) => {
            try {
                return JSON.parse(r.body).success !== undefined;
            } catch (e) {
                return false;
            }
        },
        'task orchestration completes in <30s': () => duration < 30000,
    });
    errorRate.add(taskResponse.status !== 200);
    taskDuration.add(duration);
    
    sleep(2);
    
    // Test 5: WebSocket Stats (requires auth)
    let wsStatsResponse = http.get(`${BASE_URL}/ws/stats`, { headers: headers });
    check(wsStatsResponse, {
        'websocket stats status is 200': (r) => r.status === 200,
    });
    errorRate.add(wsStatsResponse.status !== 200);
    
    sleep(1);
}

// Setup function (runs once)
export function setup() {
    console.log(`Starting load test against ${BASE_URL}`);
    
    // Verify server is accessible
    let healthCheck = http.get(`${BASE_URL}/health`);
    if (healthCheck.status !== 200) {
        throw new Error(`Server not accessible at ${BASE_URL}`);
    }
    
    return { baseUrl: BASE_URL };
}

// Teardown function (runs once at end)
export function teardown(data) {
    console.log('Load test complete');
    console.log(`Tested against: ${data.baseUrl}`);
}

// Handle summary for custom reporting
export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'logs/load_test_summary.json': JSON.stringify(data),
        'logs/load_test_report.html': htmlReport(data),
    };
}

// Simple text summary
function textSummary(data, options) {
    const indent = options.indent || '';
    const enableColors = options.enableColors || false;
    
    let summary = '\n=== Load Test Summary ===\n\n';
    
    // Request metrics
    summary += `${indent}HTTP Requests:\n`;
    summary += `${indent}  Total: ${data.metrics.http_reqs.values.count}\n`;
    summary += `${indent}  Failed: ${data.metrics.http_req_failed.values.rate * 100}%\n`;
    summary += `${indent}  Duration (avg): ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
    summary += `${indent}  Duration (p95): ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
    
    // Custom metrics
    if (data.metrics.errors) {
        summary += `\n${indent}Errors:\n`;
        summary += `${indent}  Rate: ${data.metrics.errors.values.rate * 100}%\n`;
    }
    
    if (data.metrics.task_duration) {
        summary += `\n${indent}Task Orchestration:\n`;
        summary += `${indent}  Avg Duration: ${data.metrics.task_duration.values.avg.toFixed(2)}ms\n`;
        summary += `${indent}  p95 Duration: ${data.metrics.task_duration.values['p(95)'].toFixed(2)}ms\n`;
    }
    
    return summary;
}

// Simple HTML report
function htmlReport(data) {
    return `<!DOCTYPE html>
<html>
<head>
    <title>OmniMind Load Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .pass { color: green; }
        .fail { color: red; }
    </style>
</head>
<body>
    <h1>OmniMind Load Test Report</h1>
    <p>Generated: ${new Date().toISOString()}</p>
    
    <h2>Summary</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total Requests</td><td>${data.metrics.http_reqs.values.count}</td></tr>
        <tr><td>Failed Requests</td><td class="${data.metrics.http_req_failed.values.rate < 0.1 ? 'pass' : 'fail'}">${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%</td></tr>
        <tr><td>Avg Response Time</td><td>${data.metrics.http_req_duration.values.avg.toFixed(2)}ms</td></tr>
        <tr><td>p95 Response Time</td><td class="${data.metrics.http_req_duration.values['p(95)'] < 500 ? 'pass' : 'fail'}">${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms</td></tr>
    </table>
    
    <h2>Thresholds</h2>
    <table>
        <tr><th>Threshold</th><th>Status</th></tr>
        ${Object.entries(data.root_group.checks || {}).map(([name, check]) => `
            <tr>
                <td>${name}</td>
                <td class="${check.passes === check.fails + check.passes ? 'pass' : 'fail'}">
                    ${check.passes}/${check.fails + check.passes} passed
                </td>
            </tr>
        `).join('')}
    </table>
</body>
</html>`;
}
