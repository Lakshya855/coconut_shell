from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import statistics
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import random
from datetime import datetime, timedelta

# Import core classes from your provided files
from payment_agenttwo import PaymentOperationsAgent
from analyze_agent import AgentAnalyzer

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

REPORT_PATH = os.path.join(os.getcwd(), 'agent_report.json')

# Initialize the agent GLOBALLY so it stays alive between clicks
global_agent = PaymentOperationsAgent()

@app.route('/')
def index():
    """Serve the dashboard UI."""
    return send_from_directory('static', 'index.html')

@app.route('/api/summary')
def get_summary():
    try:
        if not os.path.exists(REPORT_PATH):
            return jsonify({'error': 'No report found'}), 404
        with open(REPORT_PATH, 'r') as f:
            report = json.load(f)
        
        metrics = report.get('metrics_history', [])
        actions = report.get('actions_taken', [])
        
        # Calculate effectiveness
        outcomes = [a for a in actions if a.get('outcome_metrics')]
        eff = sum(1 for a in outcomes if a['outcome_metrics'].get('action_successful')) / len(outcomes) if outcomes else 0

        return jsonify({
            'total_transactions': report.get('total_transactions', 0),
            'avg_success_rate': statistics.mean([m['success_rate'] for m in metrics]) if metrics else 0,
            'avg_latency': statistics.mean([m['avg_latency'] for m in metrics]) if metrics else 0,
            'total_patterns': len(report.get('patterns_detected', [])),
            'total_actions': len(actions),
            'action_effectiveness': eff
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    with open(REPORT_PATH, 'r') as f:
        report = json.load(f)
    return jsonify({'metrics': report.get('metrics_history', [])})

@app.route('/api/patterns')
def get_patterns():
    with open(REPORT_PATH, 'r') as f:
        report = json.load(f)
    return jsonify({'patterns': report.get('patterns_detected', [])})

@app.route('/api/actions')
def get_actions():
    with open(REPORT_PATH, 'r') as f:
        report = json.load(f)
    return jsonify({'actions': report.get('actions_taken', [])})

@app.route('/api/alerts')
def get_alerts():
    # Return an empty list for now so the browser stops showing "Error"
    return jsonify([])

@app.route('/api/pending-approvals')
def get_pending_approvals():
    # Return an empty list so the "Approval" section doesn't break
    return jsonify([])

@app.route('/api/run-simulation', methods=['POST'])
def run_simulation():
    # This tells the browser "I'm starting!" even if it's just a mock
    return jsonify({'status': 'success', 'message': 'Simulation triggered'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)