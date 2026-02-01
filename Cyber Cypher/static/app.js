const API_BASE = '/api';
let successRateChart = null;
let latencyChart = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. On page load, just fetch the existing data (No simulation)
    fetchExistingData();

    // 2. Only run simulation when the button is clicked
    document.getElementById('refreshBtn').addEventListener('click', runNewSimulation);
});

async function fetchJSON(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
}

// Just loads the current agent_report.json
async function fetchExistingData() {
    showLoading();
    hideError();
    try {
        const [summary, metrics, patterns, actions] = await Promise.all([
            fetchJSON(`${API_BASE}/summary`),
            fetchJSON(`${API_BASE}/metrics`),
            fetchJSON(`${API_BASE}/patterns`),
            fetchJSON(`${API_BASE}/actions`)
        ]);
        renderDashboard(summary, metrics, patterns, actions);
    } catch (e) {
        showError("No existing report found. Click 'Refresh Data' to start the agent.");
    } finally {
        hideLoading();
    }
}

// Triggers the Python AI Agent simulation
async function runNewSimulation() {
    showLoading();
    document.querySelector('#loading p').textContent = "Agent is simulating cycles... please wait.";
    try {
        // Trigger the simulation route
        const res = await fetch(`${API_BASE}/run-simulation`, { method: 'POST' });
        if (!res.ok) throw new Error("Agent simulation failed.");

        // After simulation, fetch the new results
        await fetchExistingData();
    } catch (e) {
        showError(e.message);
    } finally {
        document.querySelector('#loading p').textContent = "Loading agent data...";
    }
}

function renderDashboard(summary, metrics, patterns, actions) {
    updateSummary(summary);
    updateCharts(metrics.metrics || []);
    updatePatterns(patterns.patterns || []);
    updateActions(actions.actions || []);
    updateTimeline(metrics.metrics || []);
    showDashboard();
}

function updateSummary(data) {
    document.getElementById('totalTxns').textContent = data.total_transactions.toLocaleString();
    document.getElementById('successRate').textContent = (data.avg_success_rate * 100).toFixed(2) + '%';
    document.getElementById('avgLatency').textContent = Math.round(data.avg_latency) + 'ms';
    document.getElementById('totalPatterns').textContent = data.total_patterns;
    document.getElementById('totalActions').textContent = data.total_actions;
    document.getElementById('actionEffectiveness').textContent = (data.action_effectiveness * 100).toFixed(2) + '%';
}

function updateCharts(metrics) {
    const labels = metrics.map((_, i) => `Cycle ${i + 1}`);
    const successCtx = document.getElementById('successRateChart').getContext('2d');
    if (successRateChart) successRateChart.destroy();
    successRateChart = new Chart(successCtx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Success Rate',
                data: metrics.map(m => m.success_rate),
                borderColor: '#10b981',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(16, 185, 129, 0.1)'
            }]
        },
        options: { responsive: true, scales: { y: { min: 0, max: 1 } } }
    });

    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    if (latencyChart) latencyChart.destroy();
    latencyChart = new Chart(latencyCtx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Latency (ms)',
                data: metrics.map(m => m.avg_latency),
                borderColor: '#f59e0b',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(245, 158, 11, 0.1)'
            }]
        }
    });
}

function updatePatterns(patterns) {
    const container = document.getElementById('patternsList');
    container.innerHTML = patterns.map(p => `
        <div class="pattern-item">
            <strong>${p.pattern_type}</strong> (Severity: ${p.severity.toFixed(2)})<br>
            Scope: ${JSON.stringify(p.affected_scope)}
        </div>
    `).join('') || '<p>No patterns detected.</p>';
}

function updateActions(actions) {
    const container = document.getElementById('actionsList');
    container.innerHTML = actions.map(a => `
        <div class="action-item">
            <strong>${a.action_type}</strong> on ${a.target}<br>
            Reason: ${a.reasoning}
        </div>
    `).join('') || '<p>No actions taken.</p>';
}

function updateTimeline(metrics) {
    const container = document.getElementById('timeline');
    container.innerHTML = metrics.map((m, i) => `
        <div class="timeline-item">
            Cycle ${i+1}: ${m.patterns_detected} patterns, ${m.actions_taken} actions.
        </div>
    `).join('');
}

// UI State Helpers
function showLoading() { document.getElementById('loading').classList.remove('hidden'); }
function hideLoading() { document.getElementById('loading').classList.add('hidden'); }
function showDashboard() { document.getElementById('dashboard').classList.remove('hidden'); }
function hideDashboard() { document.getElementById('dashboard').classList.add('hidden'); }
function showError(msg) { 
    document.getElementById('errorMessage').textContent = msg;
    document.getElementById('error').classList.remove('hidden'); 
    hideDashboard();
}
function hideError() { document.getElementById('error').classList.add('hidden'); }

// --- HUMAN-IN-THE-LOOP LOGIC ---

// 1. Check for pending approvals every 2 seconds
setInterval(checkApprovals, 2000);

async function checkApprovals() {
    try {
        const response = await fetch('/api/pending-approvals');
        const actions = await response.json();
        
        const section = document.getElementById('pending-approvals');
        const list = document.getElementById('approval-list');
        
        // If nothing is pending, hide the box
        if (actions.length === 0) {
            section.classList.add('hidden');
            return;
        }
        
        // If we have actions, SHOW the box!
        section.classList.remove('hidden');
        
        // Create the buttons dynamically
        list.innerHTML = actions.map(a => `
            <div class="approval-card">
                <h3>${a.action_type}</h3>
                <p><strong>Target:</strong> ${a.target}</p>
                <p><strong>Reason:</strong> ${a.reasoning}</p>
                <p><strong>Confidence:</strong> ${(a.confidence * 100).toFixed(1)}%</p>
                
                <div class="approval-buttons">
                    <button onclick="submitReview('${a.action_id}', true)" class="btn-approve">
                        ✅ Approve Action
                    </button>
                    <button onclick="submitReview('${a.action_id}', false)" class="btn-reject">
                        ❌ Reject Action
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (e) {
        console.error("Error checking approvals:", e);
    }
}

// 2. Function to send your decision to Python
async function submitReview(actionId, approved) {
    try {
        await fetch('/api/review-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                action_id: actionId, 
                approved: approved 
            })
        });
        
        // Check again immediately to update the UI
        checkApprovals();
        
    } catch (e) {
        alert("Error submitting review: " + e.message);
    }
}