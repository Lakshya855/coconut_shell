# Agentic AI for Smart Payment Operations

A production-ready autonomous agent system that manages payment operations in real-time, demonstrating a complete **observe → reason → decide → act → learn** loop.

## 🎯 System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Payment Operations Agent                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ OBSERVE  │ → │  REASON  │ → │  DECIDE  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       ↓               ↓               ↓                      │
│  [Data Stream]  [Patterns]    [Actions]                     │
│       ↓               ↓               ↓                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   ACT    │ ← │  LEARN   │ ← │  Memory  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1. **Observation Layer** (`PaymentDataStream`)
- Ingests real-time payment transaction events
- Simulates realistic payment scenarios with configurable degradation
- Supports injection of failure scenarios (issuer outages, network issues, retry storms)
- Processes: transaction status, latency, payment methods, banks, issuers, error codes

### 2. **Memory System** (`AgentMemory`)
- Maintains sliding window of recent events (configurable, default: 1000 events)
- Stores action history and outcomes
- Tracks baseline performance metrics
- Enables learning from past interventions
- Implements efficient pattern lookup and retrieval

### 3. **Reasoning Engine** (`PatternDetector`)
- Detects multiple pattern types:
  - **Issuer Degradation**: Bank/issuer-specific failure rate spikes
  - **Latency Spikes**: Unusual transaction processing delays
  - **Retry Storms**: Excessive retry behavior indicating system stress
  - **Method Fatigue**: Payment method-specific failures
- Calculates severity scores (0-1) for each pattern
- Provides statistical evidence (sample sizes, confidence intervals)

### 4. **Decision Engine** (`DecisionEngine`)
- Context-aware decision making with multiple action types:
  - `ADJUST_RETRY`: Modify retry strategies (limits, backoff, timing)
  - `REROUTE`: Redirect traffic to alternative paths/gateways
  - `SUPPRESS_PATH`: Temporarily disable failing routes
  - `ENABLE_FALLBACK`: Activate backup payment methods
  - `ALERT_OPS`: Notify operations team for manual intervention
- Learns from historical action outcomes
- Implements safety constraints:
  - Auto-approval threshold for low-risk actions
  - Maximum simultaneous actions limit
  - Cooldown periods between actions
- Balances trade-offs: success rate vs. latency vs. cost vs. user friction

### 5. **Action Execution** (`ActionExecutor`)
- Executes approved actions with guardrails
- Tracks active interventions
- Evaluates action effectiveness by comparing pre/post metrics
- Automatic rollback for degrading performance
- Maintains rollback history for analysis

### 6. **Learning Loop**
- Continuously evaluates action outcomes
- Updates decision confidence based on historical success
- Adjusts baseline metrics as system state evolves
- Feeds learning back into decision engine for improved future actions

## 🚀 Key Features

### Safety & Governance
- **Tiered Approval System**: High-severity actions require human approval
- **Automatic Rollback**: Actions degrading performance are automatically reversed
- **Action Limits**: Prevents simultaneous execution of too many changes
- **Cooldown Periods**: Prevents rapid action oscillation
- **Explainable Decisions**: Every action includes confidence score and reasoning

### Intelligent Pattern Recognition
- **Multi-dimensional Analysis**: Analyzes by issuer, bank, method, merchant
- **Statistical Confidence**: Minimum sample sizes and thresholds prevent false positives
- **Severity Scoring**: Prioritizes critical issues over minor fluctuations
- **Temporal Awareness**: Tracks pattern evolution over time

### Adaptive Learning
- **Outcome Tracking**: Measures success rate, latency improvements
- **Historical Context**: Learns from past action effectiveness
- **Dynamic Thresholds**: Adjusts intervention strategies based on results
- **Baseline Adaptation**: Updates normal behavior expectations

## 📊 Example Output

```
🔥 SCENARIO INJECTED: issuer_down targeting HDFC_ISSUER

================================================================================
📊 CYCLE SUMMARY - Transactions: 150
================================================================================
✅ Success Rate: 68.50%
⚡ Avg Latency: 1847ms
🔍 Patterns Detected: 2
🎯 Actions Taken: 1

🔍 DETECTED PATTERNS:
   • issuer_degradation (severity: 0.72)
     Scope: {'issuer': 'HDFC_ISSUER'}
     Metrics: {'failure_rate': 0.36, 'avg_latency': 2641, 'sample_size': 14}
   
🎯 ACTIONS TAKEN:
   ✓ Executed: reroute_payment
     Target: HDFC_ISSUER
     Confidence: 87.30%
     Reasoning: Issuer HDFC_ISSUER showing 36.0% failure rate (severity: 0.72).
                Rerouting 80% traffic to fallback path.
```

## 🛡️ Safety Guardrails

### What the Agent Can Do Autonomously
- Adjust retry configurations (max retries, backoff timing)
- Enable fallback payment methods for high-latency paths
- Send alerts to operations team
- Make low-impact routing adjustments (<60% severity)

### What Requires Human Approval
- Large-scale traffic rerouting (>60% severity)
- Suppressing entire payment paths
- Actions affecting multiple issuers simultaneously
- Any action with confidence < 70%

### Automatic Rollback Triggers
- Success rate drops >10% after action execution
- Latency increases >50% after action execution
- Failure rate increases after supposed fix
- Evaluation period: 100 transactions post-action

## 🎮 Usage

### Basic Usage

```python
from payment_agent import PaymentOperationsAgent

# Initialize agent
agent = PaymentOperationsAgent()

# Run with automatic scenario injection
agent.run(cycles=12, inject_scenarios=True)
```

### Custom Configuration

```python
agent = PaymentOperationsAgent()

# Customize observation window
agent.observation_window = 100  # events per cycle

# Customize decision thresholds
agent.decision_engine.auto_approval_threshold = 0.7  # Higher = more cautious

# Inject specific scenario
agent.data_stream.inject_scenario('issuer_down', 'HDFC_ISSUER')

# Run specific number of cycles
agent.run(cycles=20, inject_scenarios=False)
```

### Accessing Results

```python
# Get current metrics
metrics = agent.metrics_history[-1]
print(f"Current success rate: {metrics['success_rate']:.2%}")

# Review actions taken
for action in agent.memory.actions_taken:
    print(f"{action.action_type.value}: {action.reasoning}")
    if action.outcome_metrics:
        print(f"  Result: {action.outcome_metrics['success_rate_improvement']:.2%}")

# Access detected patterns
for pattern_id, pattern in agent.memory.detected_patterns.items():
    print(f"{pattern.pattern_type}: severity {pattern.severity:.2f}")
```

## 📈 Performance Metrics

The agent tracks:
- **Success Rate**: Percentage of successful transactions
- **Average Latency**: Mean transaction processing time
- **Pattern Detection Rate**: Issues identified per cycle
- **Action Effectiveness**: Success rate of interventions
- **Cycle Time**: Agent processing overhead

All metrics are logged to `agent_report.json` for analysis.

## 🧪 Testing Scenarios

The system includes built-in test scenarios:

1. **Normal Operations** (2% failure rate)
   - Baseline behavior, minimal interventions

2. **Issuer Downtime** (35% failure rate)
   - Triggers aggressive rerouting
   - Tests fallback mechanisms

3. **Network Slowdown** (8% failure, high latency)
   - Activates latency-based fallbacks
   - Adjusts timeout configurations

4. **Retry Storm** (15% failure, high retry rate)
   - Implements circuit breakers
   - Reduces retry limits globally

## 🔬 Architecture Decisions

### Why Not a Rules Engine?
- **Context-Aware**: Decisions consider current system state, historical performance, and confidence levels
- **Learning**: Improves from experience, not static if-then rules
- **Explainable**: Provides reasoning and confidence for each decision
- **Adaptive Thresholds**: Adjusts to changing baseline performance

### Why This Memory Design?
- **Sliding Window**: Balances recency with statistical significance
- **Action Tracking**: Essential for learning and rollback
- **Pattern History**: Prevents duplicate detections and actions
- **Baseline Calculation**: Enables anomaly detection relative to normal

### Trade-off Balancing
The agent considers multiple objectives:
- **Success Rate**: Primary goal, but not at any cost
- **Latency**: Important for UX, but success takes priority
- **Cost**: Alternative routes may be more expensive
- **Risk**: Conservative on high-severity changes

## 🔮 Future Enhancements

Potential extensions:
- Integration with actual payment gateway APIs
- Real-time dashboard for monitoring agent decisions
- A/B testing framework for action strategies
- Multi-agent coordination for distributed systems
- Advanced ML models for pattern prediction
- Cost optimization algorithms
- Merchant-specific SLA handling

## 📝 Output Files

- `agent_report.json`: Comprehensive performance report
  - All transactions processed
  - Actions taken with outcomes
  - Patterns detected
  - Metrics timeline

## 🎯 Success Criteria

The agent successfully demonstrates:
1. ✅ **Complete OODA Loop**: Observe → Reason → Decide → Act → Learn
2. ✅ **Real Agent Logic**: State management, memory, decision policies
3. ✅ **Pattern Detection**: Multiple failure modes identified
4. ✅ **Contextual Decisions**: Not rules-based, considers full context
5. ✅ **Safety Guardrails**: Approval requirements, rollback mechanisms
6. ✅ **Learning**: Improves decisions based on historical outcomes
7. ✅ **Explainability**: Clear reasoning for every action

## 🏃 Quick Start

```bash
# Run the agent
python payment_agent.py

# View results
cat agent_report.json
```

The agent will run 12 cycles, automatically inject failure scenarios, and demonstrate autonomous decision-making with safety guardrails.
