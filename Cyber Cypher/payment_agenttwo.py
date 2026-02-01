"""
Agentic AI for Smart Payment Operations
A complete autonomous agent that manages payment operations in real-time
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import statistics
import pandas as pd
import os


class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    RETRYING = "retrying"


class PaymentMethod(Enum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class ActionType(Enum):
    ADJUST_RETRY = "adjust_retry_strategy"
    REROUTE = "reroute_payment"
    SUPPRESS_PATH = "suppress_failing_path"
    ALERT_OPS = "alert_operations"
    ENABLE_FALLBACK = "enable_fallback_method"
    NO_ACTION = "no_action"


@dataclass
class PaymentEvent:
    """Represents a single payment transaction event"""
    transaction_id: str
    timestamp: datetime
    merchant_id: str
    amount: float
    payment_method: PaymentMethod
    bank_code: str
    issuer: str
    status: PaymentStatus
    error_code: Optional[str]
    latency_ms: float
    retry_count: int
    routing_path: str
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['payment_method'] = self.payment_method.value
        data['status'] = self.status.value
        return data


@dataclass
class AgentAction:
    """Represents an action taken by the agent"""
    action_id: str
    timestamp: datetime
    action_type: ActionType
    target: str  # What's being modified (issuer, bank, method, etc.)
    parameters: Dict
    confidence: float
    reasoning: str
    requires_approval: bool
    approved: bool = False
    executed: bool = False
    outcome_metrics: Optional[Dict] = None
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['action_type'] = self.action_type.value
        return data


@dataclass
class Pattern:
    """Represents a detected pattern in payment behavior"""
    pattern_id: str
    pattern_type: str
    severity: float  # 0-1
    affected_scope: Dict  # e.g., {'issuer': 'HDFC', 'method': 'UPI'}
    metrics: Dict
    first_seen: datetime
    last_seen: datetime
    occurrences: int
    
    def to_dict(self):
        data = asdict(self)
        data['first_seen'] = self.first_seen.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        return data


class PaymentDataStream:
    """Simulates real-time payment data stream"""
    
    def __init__(self):
        self.banks = ['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK']
        self.issuers = ['HDFC_ISSUER', 'ICICI_ISSUER', 'SBI_ISSUER', 'VISA', 'MASTERCARD']
        self.merchants = [f'MERCHANT_{i:03d}' for i in range(1, 21)]
        self.routing_paths = ['primary', 'secondary', 'fallback']
        
        # Simulate degradation scenarios
        self.degradation_scenarios = {
            'normal': {'failure_rate': 0.02, 'latency_mean': 800, 'latency_std': 200},
            'issuer_down': {'failure_rate': 0.35, 'latency_mean': 2500, 'latency_std': 800},
            'network_slow': {'failure_rate': 0.08, 'latency_mean': 3000, 'latency_std': 1200},
            'retry_storm': {'failure_rate': 0.15, 'latency_mean': 1200, 'latency_std': 400}
        }
        
        self.current_scenario = 'normal'
        self.scenario_target = None  # Which issuer/bank is affected
        
    def generate_event(self, transaction_id: int) -> PaymentEvent:
        """Generate a single payment event"""
        method = random.choice(list(PaymentMethod))
        bank = random.choice(self.banks)
        issuer = random.choice(self.issuers)
        
        # Apply scenario-based degradation
        scenario = self.degradation_scenarios[self.current_scenario]
        
        # Check if this transaction is affected by current scenario
        is_affected = (self.scenario_target is None or 
                      self.scenario_target == issuer or 
                      self.scenario_target == bank)
        
        if is_affected:
            failure_rate = scenario['failure_rate']
            latency_params = (scenario['latency_mean'], scenario['latency_std'])
        else:
            normal = self.degradation_scenarios['normal']
            failure_rate = normal['failure_rate']
            latency_params = (normal['latency_mean'], normal['latency_std'])
        
        # Determine status
        if random.random() < failure_rate:
            status = PaymentStatus.FAILED
            error_code = random.choice(['ISSUER_DOWN', 'TIMEOUT', 'INSUFFICIENT_FUNDS', 
                                       'INVALID_CARD', 'NETWORK_ERROR'])
        else:
            status = PaymentStatus.SUCCESS
            error_code = None
        
        latency = max(100, random.gauss(*latency_params))
        
        return PaymentEvent(
            transaction_id=f"TXN_{transaction_id:08d}",
            timestamp=datetime.now(),
            merchant_id=random.choice(self.merchants),
            amount=random.uniform(100, 50000),
            payment_method=method,
            bank_code=bank,
            issuer=issuer,
            status=status,
            error_code=error_code,
            latency_ms=latency,
            retry_count=random.randint(0, 3) if status == PaymentStatus.FAILED else 0,
            routing_path=random.choice(self.routing_paths)
        )
    
    def inject_scenario(self, scenario: str, target: Optional[str] = None):
        """Inject a degradation scenario"""
        self.current_scenario = scenario
        self.scenario_target = target
        print(f"🔥 SCENARIO INJECTED: {scenario} targeting {target}")


class AgentMemory:
    """Agent's memory system for learning and decision-making"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.recent_events = deque(maxlen=window_size)
        self.actions_taken = []
        self.detected_patterns = {}
        self.action_outcomes = defaultdict(list)
        self.baseline_metrics = {}
        
    def add_event(self, event: PaymentEvent):
        """Add event to memory"""
        self.recent_events.append(event)
    
    def add_action(self, action: AgentAction):
        """Record an action taken"""
        self.actions_taken.append(action)
    
    def record_outcome(self, action_id: str, metrics: Dict):
        """Record the outcome of an action"""
        for action in self.actions_taken:
            if action.action_id == action_id:
                action.outcome_metrics = metrics
                self.action_outcomes[action.action_type].append({
                    'action': action,
                    'metrics': metrics
                })
                break
    
    def get_recent_events(self, n: int = None) -> List[PaymentEvent]:
        """Get recent events"""
        if n is None:
            return list(self.recent_events)
        return list(self.recent_events)[-n:]
    
    def calculate_baseline(self):
        """Calculate baseline metrics from recent history"""
        if len(self.recent_events) < 100:
            return
        
        events = list(self.recent_events)
        total = len(events)
        
        self.baseline_metrics = {
            'success_rate': sum(1 for e in events if e.status == PaymentStatus.SUCCESS) / total,
            'avg_latency': statistics.mean(e.latency_ms for e in events),
            'failure_rate': sum(1 for e in events if e.status == PaymentStatus.FAILED) / total,
        }


class PatternDetector:
    """Detects patterns and anomalies in payment data"""
    
    def __init__(self):
        self.pattern_thresholds = {
            'issuer_degradation': {'min_failures': 5, 'failure_rate': 0.15},
            'latency_spike': {'min_events': 10, 'latency_threshold': 2000},
            'retry_storm': {'min_retries': 3, 'retry_rate': 0.3},
            'method_fatigue': {'min_failures': 8, 'failure_rate': 0.25}
        }
    
    def detect_patterns(self, events: List[PaymentEvent], memory: AgentMemory) -> List[Pattern]:
        """Detect patterns in recent events"""
        patterns = []
        
        # Group events by different dimensions
        by_issuer = defaultdict(list)
        by_method = defaultdict(list)
        by_bank = defaultdict(list)
        
        for event in events:
            by_issuer[event.issuer].append(event)
            by_method[event.payment_method].append(event)
            by_bank[event.bank_code].append(event)
        
        # Detect issuer degradation
        for issuer, issuer_events in by_issuer.items():
            if len(issuer_events) >= self.pattern_thresholds['issuer_degradation']['min_failures']:
                failure_rate = sum(1 for e in issuer_events if e.status == PaymentStatus.FAILED) / len(issuer_events)
                avg_latency = statistics.mean(e.latency_ms for e in issuer_events)
                
                # --- NEW CODE: Check Dynamic Latency Limit ---
                # 1. Get the limit we set in run_cycle (default to 800 if missing)
                latency_limit = getattr(memory, 'dynamic_latency_limit', 800.0)
                
                # 2. Check if current latency exceeds that limit
                if avg_latency > latency_limit:
                    patterns.append(Pattern(
                        pattern_id=f"latency_spike_{issuer}_{int(time.time())}",
                        pattern_type="latency_spike",
                        severity=min(1.0, (avg_latency - latency_limit) / 1000),
                        affected_scope={'issuer': issuer},
                        metrics={
                            'avg_latency': avg_latency,
                            'limit_used': latency_limit, # Proof we used the spreadsheet
                            'sample_size': len(issuer_events)
                        },
                        first_seen=min(e.timestamp for e in issuer_events),
                        last_seen=max(e.timestamp for e in issuer_events),
                        occurrences=len(issuer_events)
                    ))
                # ---------------------------------------------
                
                if failure_rate > self.pattern_thresholds['issuer_degradation']['failure_rate']:
                    patterns.append(Pattern(
                        pattern_id=f"issuer_deg_{issuer}_{int(time.time())}",
                        pattern_type="issuer_degradation",
                        severity=min(1.0, failure_rate * 2),
                        affected_scope={'issuer': issuer},
                        metrics={
                            'failure_rate': failure_rate,
                            'avg_latency': avg_latency,
                            'sample_size': len(issuer_events)
                        },
                        first_seen=min(e.timestamp for e in issuer_events),
                        last_seen=max(e.timestamp for e in issuer_events),
                        occurrences=len(issuer_events)
                    ))
        
        # Detect latency spikes
        for issuer, issuer_events in by_issuer.items():
            if len(issuer_events) >= self.pattern_thresholds['latency_spike']['min_events']:
                avg_latency = statistics.mean(e.latency_ms for e in issuer_events)
                
                if avg_latency > self.pattern_thresholds['latency_spike']['latency_threshold']:
                    baseline = memory.baseline_metrics.get('avg_latency', 1000)
                    severity = min(1.0, avg_latency / (baseline * 3))
                    
                    patterns.append(Pattern(
                        pattern_id=f"latency_spike_{issuer}_{int(time.time())}",
                        pattern_type="latency_spike",
                        severity=severity,
                        affected_scope={'issuer': issuer},
                        metrics={
                            'avg_latency': avg_latency,
                            'baseline_latency': baseline,
                            'sample_size': len(issuer_events)
                        },
                        first_seen=min(e.timestamp for e in issuer_events),
                        last_seen=max(e.timestamp for e in issuer_events),
                        occurrences=len(issuer_events)
                    ))
        
        # Detect retry storms
        high_retry_events = [e for e in events if e.retry_count >= 2]
        if len(high_retry_events) >= self.pattern_thresholds['retry_storm']['min_retries']:
            retry_rate = len(high_retry_events) / len(events)
            
            if retry_rate > self.pattern_thresholds['retry_storm']['retry_rate']:
                patterns.append(Pattern(
                    pattern_id=f"retry_storm_{int(time.time())}",
                    pattern_type="retry_storm",
                    severity=min(1.0, retry_rate * 2),
                    affected_scope={'global': True},
                    metrics={
                        'retry_rate': retry_rate,
                        'high_retry_count': len(high_retry_events),
                        'sample_size': len(events)
                    },
                    first_seen=min(e.timestamp for e in high_retry_events),
                    last_seen=max(e.timestamp for e in high_retry_events),
                    occurrences=len(high_retry_events)
                ))
        
        # Detect method-specific failures
        for method, method_events in by_method.items():
            if len(method_events) >= self.pattern_thresholds['method_fatigue']['min_failures']:
                failure_rate = sum(1 for e in method_events if e.status == PaymentStatus.FAILED) / len(method_events)
                
                if failure_rate > self.pattern_thresholds['method_fatigue']['failure_rate']:
                    patterns.append(Pattern(
                        pattern_id=f"method_fatigue_{method.value}_{int(time.time())}",
                        pattern_type="method_fatigue",
                        severity=min(1.0, failure_rate * 1.5),
                        affected_scope={'method': method.value},
                        metrics={
                            'failure_rate': failure_rate,
                            'sample_size': len(method_events)
                        },
                        first_seen=min(e.timestamp for e in method_events),
                        last_seen=max(e.timestamp for e in method_events),
                        occurrences=len(method_events)
                    ))
        
        return patterns


class DecisionEngine:
    """Makes decisions about what actions to take based on patterns"""
    
    def __init__(self):
        self.action_policies = {
            'issuer_degradation': self._handle_issuer_degradation,
            'latency_spike': self._handle_latency_spike,
            'retry_storm': self._handle_retry_storm,
            'method_fatigue': self._handle_method_fatigue
        }
        
        # Safety constraints
        self.auto_approval_threshold = 0.6  # Severity below this can be auto-approved
        self.max_simultaneous_actions = 3
        self.cooldown_period = timedelta(minutes=5)
        self.last_action_time = defaultdict(lambda: datetime.min)
    
    def decide(self, patterns: List[Pattern], memory: AgentMemory) -> List[AgentAction]:
        """Decide what actions to take based on detected patterns"""
        actions = []
        
        # Check active actions count
        active_actions = [a for a in memory.actions_taken 
                         if a.executed and not a.outcome_metrics]
        
        if len(active_actions) >= self.max_simultaneous_actions:
            return []  # Too many active actions
        
        # Sort patterns by severity
        patterns.sort(key=lambda p: p.severity, reverse=True)
        
        for pattern in patterns:
            # Check cooldown
            pattern_key = f"{pattern.pattern_type}_{pattern.affected_scope}"
            if datetime.now() - self.last_action_time[pattern_key] < self.cooldown_period:
                continue
            
            # Get appropriate handler
            handler = self.action_policies.get(pattern.pattern_type)
            if handler:
                action = handler(pattern, memory)
                if action:
                    actions.append(action)
                    self.last_action_time[pattern_key] = datetime.now()
                    
                    if len(actions) >= self.max_simultaneous_actions:
                        break
        
        return actions
    
    def _handle_issuer_degradation(self, pattern: Pattern, memory: AgentMemory) -> Optional[AgentAction]:
        """Handle issuer degradation pattern"""
        issuer = pattern.affected_scope['issuer']
        severity = pattern.severity
        failure_rate = pattern.metrics['failure_rate']
        
        # Learn from past actions
        past_outcomes = memory.action_outcomes.get(ActionType.REROUTE, [])
        avg_success_improvement = 0.0
        if past_outcomes:
            improvements = [o['metrics'].get('success_rate_improvement', 0) 
                          for o in past_outcomes]
            avg_success_improvement = statistics.mean(improvements)
        
        # Calculate confidence based on severity and past learnings
        confidence = min(0.95, severity + (avg_success_improvement * 0.3))
        
        if failure_rate > 0.3:
            # Severe degradation - reroute traffic
            return AgentAction(
                action_id=f"action_{int(time.time())}_{random.randint(1000, 9999)}",
                timestamp=datetime.now(),
                action_type=ActionType.REROUTE,
                target=issuer,
                parameters={
                    'from_issuer': issuer,
                    'to_routing': 'fallback',
                    'percentage': 80,
                    'duration_minutes': 15
                },
                confidence=confidence,
                reasoning=f"Issuer {issuer} showing {failure_rate:.1%} failure rate (severity: {severity:.2f}). "
                         f"Rerouting 80% traffic to fallback path. Past reroutes improved success by {avg_success_improvement:.1%}.",
                requires_approval=severity > self.auto_approval_threshold
            )
        elif failure_rate > 0.15:
            # Moderate degradation - adjust retry strategy
            return AgentAction(
                action_id=f"action_{int(time.time())}_{random.randint(1000, 9999)}",
                timestamp=datetime.now(),
                action_type=ActionType.ADJUST_RETRY,
                target=issuer,
                parameters={
                    'issuer': issuer,
                    'max_retries': 2,
                    'retry_delay_ms': 2000,
                    'exponential_backoff': True
                },
                confidence=confidence,
                reasoning=f"Issuer {issuer} showing {failure_rate:.1%} failure rate. "
                         f"Adjusting retry strategy to reduce load and improve success.",
                requires_approval=False
            )
        
        return None
    
    def _handle_latency_spike(self, pattern: Pattern, memory: AgentMemory) -> Optional[AgentAction]:
        """Handle latency spike pattern"""
        issuer = pattern.affected_scope['issuer']
        avg_latency = pattern.metrics['avg_latency']
        baseline = pattern.metrics.get('baseline_latency', 1000)
        
        if avg_latency > baseline * 2.5:
            return AgentAction(
                action_id=f"action_{int(time.time())}_{random.randint(1000, 9999)}",
                timestamp=datetime.now(),
                action_type=ActionType.ENABLE_FALLBACK,
                target=issuer,
                parameters={
                    'issuer': issuer,
                    'latency_threshold_ms': baseline * 2,
                    'fallback_method': 'alternative_gateway'
                },
                confidence=min(0.9, pattern.severity),
                reasoning=f"Latency spike detected for {issuer}: {avg_latency:.0f}ms "
                         f"(baseline: {baseline:.0f}ms). Enabling fallback for slow transactions.",
                requires_approval=pattern.severity > self.auto_approval_threshold
            )
        
        return None
    
    def _handle_retry_storm(self, pattern: Pattern, memory: AgentMemory) -> Optional[AgentAction]:
        """Handle retry storm pattern"""
        retry_rate = pattern.metrics['retry_rate']
        
        return AgentAction(
            action_id=f"action_{int(time.time())}_{random.randint(1000, 9999)}",
            timestamp=datetime.now(),
            action_type=ActionType.ADJUST_RETRY,
            target='global',
            parameters={
                'global_max_retries': 2,
                'retry_backoff_multiplier': 2.0,
                'circuit_breaker_threshold': 5
            },
            confidence=0.85,
            reasoning=f"Retry storm detected: {retry_rate:.1%} of transactions have high retry counts. "
                     f"Implementing global retry limits to prevent cascade failures.",
            requires_approval=pattern.severity > 0.7
        )
    
    def _handle_method_fatigue(self, pattern: Pattern, memory: AgentMemory) -> Optional[AgentAction]:
        """Handle payment method fatigue"""
        method = pattern.affected_scope['method']
        failure_rate = pattern.metrics['failure_rate']
        
        return AgentAction(
            action_id=f"action_{int(time.time())}_{random.randint(1000, 9999)}",
            timestamp=datetime.now(),
            action_type=ActionType.ALERT_OPS,
            target=method,
            parameters={
                'method': method,
                'failure_rate': failure_rate,
                'alert_level': 'high' if failure_rate > 0.3 else 'medium',
                'recommended_action': 'investigate_method_specific_issues'
            },
            confidence=0.75,
            reasoning=f"Payment method {method} showing {failure_rate:.1%} failure rate. "
                     f"Alerting ops team for investigation.",
            requires_approval=False
        )


class ActionExecutor:
    """Executes actions with safety guardrails (Upgraded for HITL)"""
    
    def __init__(self):
        self.executed_actions = {}
        self.rollback_history = []
        self.pending_approvals = {} # <--- NEW: The "Holding Bay"
    
    def execute(self, action: AgentAction) -> bool:
        """Execute an action with safety checks"""
        
        # --- MODIFIED SAFETY CHECK ---
        if action.requires_approval and not action.approved:
            # Save it so the Human (You) can approve it later
            self.pending_approvals[action.action_id] = action 
            
            print(f"✋ ACTION PAUSED: {action.action_type.value} on {action.target}")
            print(f"   (Saved to pending queue. Waiting for human...)")
            return False
        # -----------------------------
        
        print(f"\n🤖 EXECUTING ACTION: {action.action_type.value}")
        print(f"   Target: {action.target}")
        print(f"   Parameters: {json.dumps(action.parameters, indent=2)}")
        print(f"   Confidence: {action.confidence:.2%}")
        print(f"   Reasoning: {action.reasoning}")
        
        # Simulate execution
        action.executed = True
        self.executed_actions[action.action_id] = action
        
        return True
    
    def rollback(self, action_id: str) -> bool:
        """Rollback an action if it's not performing well"""
        if action_id in self.executed_actions:
            action = self.executed_actions[action_id]
            print(f"\n🔄 ROLLING BACK ACTION: {action.action_type.value} on {action.target}")
            
            self.rollback_history.append({
                'action': action,
                'rollback_time': datetime.now(),
                'reason': 'Performance degradation detected'
            })
            
            del self.executed_actions[action_id]
            return True
        return False
    
    def evaluate_action(self, action_id: str, events_before: List[PaymentEvent], 
                        events_after: List[PaymentEvent]) -> Dict:
        """Evaluate the impact of an action"""
        if not events_before or not events_after:
            return {}
        
        # Calculate metrics before and after
        success_rate_before = sum(1 for e in events_before if e.status == PaymentStatus.SUCCESS) / len(events_before)
        success_rate_after = sum(1 for e in events_after if e.status == PaymentStatus.SUCCESS) / len(events_after)
        
        latency_before = statistics.mean(e.latency_ms for e in events_before)
        latency_after = statistics.mean(e.latency_ms for e in events_after)
        
        metrics = {
            'success_rate_before': success_rate_before,
            'success_rate_after': success_rate_after,
            'success_rate_improvement': success_rate_after - success_rate_before,
            'latency_before': latency_before,
            'latency_after': latency_after,
            'latency_improvement': latency_before - latency_after,
            'sample_size_before': len(events_before),
            'sample_size_after': len(events_after)
        }
        
        # Decide if action was successful
        metrics['action_successful'] = (
            metrics['success_rate_improvement'] > 0.05 or 
            metrics['latency_improvement'] > 200
        )
        
        return metrics


class PaymentOperationsAgent:
    """Main agent orchestrating the observe-reason-decide-act-learn loop"""
    
    def __init__(self):
        self.data_stream = PaymentDataStream()
        self.memory = AgentMemory()
    
        # Load the spreadsheet we generated in Step 1
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'indian_payment_calendar.csv')
        try:
            self.calendar_df = pd.read_csv(csv_path)
            print("✅ Brain Loaded: indian_payment_calendar.csv")
        except:
            print("❌ Error: CSV not found. Using defaults.")
            self.calendar_df = pd.DataFrame()
        # --------------------------------
        
        self.pattern_detector = PatternDetector()
        self.decision_engine = DecisionEngine()
        self.action_executor = ActionExecutor()
        
        self.observation_window = 50  # Events to analyze at once
        self.evaluation_window = 100  # Events to use for action evaluation
        self.transaction_counter = 0
        
        self.metrics_history = []
        self.running = False
    
    def observe(self) -> List[PaymentEvent]:
        """Observe incoming payment events"""
        events = []
        for _ in range(self.observation_window):
            self.transaction_counter += 1
            event = self.data_stream.generate_event(self.transaction_counter)
            events.append(event)
            self.memory.add_event(event)
        
        return events
    
    def reason(self, events: List[PaymentEvent]) -> List[Pattern]:
        """Reason about patterns in the observed data"""
        patterns = self.pattern_detector.detect_patterns(events, self.memory)
        
        # Store detected patterns in memory
        for pattern in patterns:
            self.memory.detected_patterns[pattern.pattern_id] = pattern
        
        return patterns
    
    def decide(self, patterns: List[Pattern]) -> List[AgentAction]:
        """Decide what actions to take"""
        actions = self.decision_engine.decide(patterns, self.memory)
        return actions
    
    def act(self, actions: List[AgentAction]) -> List[AgentAction]:
        """Execute decided actions"""
        executed_actions = []
        
        for action in actions:
            # Auto-approve low-severity actions
            if not action.requires_approval:
                action.approved = True
            
            if self.action_executor.execute(action):
                self.memory.add_action(action)
                executed_actions.append(action)
        
        return executed_actions
    
    def learn(self):
        """Learn from past actions and update decision-making"""
        # Evaluate recent actions
        for action in self.memory.actions_taken[-5:]:  # Last 5 actions
            if action.executed and action.outcome_metrics is None:
                # Get events before and after action
                action_time = action.timestamp
                
                events_before = [e for e in self.memory.recent_events 
                               if e.timestamp < action_time][-self.evaluation_window:]
                events_after = [e for e in self.memory.recent_events 
                              if e.timestamp >= action_time][:self.evaluation_window]
                
                if len(events_after) >= self.evaluation_window:
                    metrics = self.action_executor.evaluate_action(
                        action.action_id, events_before, events_after
                    )
                    
                    self.memory.record_outcome(action.action_id, metrics)
                    
                    # Rollback if action is making things worse
                    if not metrics.get('action_successful', True):
                        if metrics['success_rate_improvement'] < -0.1:
                            print(f"\n❌ ACTION DEGRADED PERFORMANCE - Rolling back")
                            self.action_executor.rollback(action.action_id)
        
        # Update baseline metrics
        self.memory.calculate_baseline()
    
    def run_cycle(self) -> Dict:
        """Run one complete observe-reason-decide-act-learn cycle"""
        cycle_start = time.time()
        # --- NEW CODE START: READ SPREADSHEET ---
        # 1. Simulate a specific date (e.g., Republic Day) to test the logic
        # Use the ACTUAL current date from your computer clock
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 2. Default Limit (Normal Day)
        current_limit = 800.0

        # 3. Check the Spreadsheet
        if hasattr(self, 'calendar_df') and not self.calendar_df.empty:
            # Find the row for today
            row = self.calendar_df[self.calendar_df['Date'] == today_str]
            if not row.empty:
                current_limit = float(row.iloc[0]['Max_Latency'])
                print(f"\n📅 AGENT CONTEXT: {row.iloc[0]['Context']}")
                print(f"   Setting Latency Limit to: {current_limit}ms")
        
        # 4. Save this limit into memory so the Detector can see it
        self.memory.dynamic_latency_limit = current_limit
        # --- NEW CODE END -----------------------
        # 1. OBSERVE
        events = self.observe()
        
        # 2. REASON
        patterns = self.reason(events)
        
        # 3. DECIDE
        actions = self.decide(patterns)
        
        # 4. ACT
        executed_actions = self.act(actions)
        
        # 5. LEARN
        self.learn()
        
        # Calculate current metrics
        recent = self.memory.get_recent_events(200)
        current_metrics = {
            'timestamp': datetime.now(),
            'success_rate': sum(1 for e in recent if e.status == PaymentStatus.SUCCESS) / len(recent) if recent else 0,
            'avg_latency': statistics.mean(e.latency_ms for e in recent) if recent else 0,
            'patterns_detected': len(patterns),
            'actions_taken': len(executed_actions),
            'total_transactions': self.transaction_counter,
            'cycle_time_ms': (time.time() - cycle_start) * 1000
        }
        
        self.metrics_history.append(current_metrics)
        
        return {
            'events_observed': len(events),
            'patterns_detected': patterns,
            'actions_taken': executed_actions,
            'current_metrics': current_metrics
        }
    
    def print_status(self, cycle_result: Dict):
        """Print current status"""
        metrics = cycle_result['current_metrics']
        patterns = cycle_result['patterns_detected']
        actions = cycle_result['actions_taken']
        
        print(f"\n" + "="*80)
        print(f"📊 CYCLE SUMMARY - Transactions: {metrics['total_transactions']}")
        print(f"="*80)
        print(f"✅ Success Rate: {metrics['success_rate']:.2%}")
        print(f"⚡ Avg Latency: {metrics['avg_latency']:.0f}ms")
        print(f"🔍 Patterns Detected: {metrics['patterns_detected']}")
        print(f"🎯 Actions Taken: {metrics['actions_taken']}")
        
        if patterns:
            print(f"\n🔍 DETECTED PATTERNS:")
            for pattern in patterns:
                print(f"   • {pattern.pattern_type} (severity: {pattern.severity:.2f})")
                print(f"     Scope: {pattern.affected_scope}")
                print(f"     Metrics: {pattern.metrics}")
        
        if actions:
            print(f"\n🎯 ACTIONS TAKEN:")
            for action in actions:
                status = "✓ Executed" if action.executed else "⏳ Pending Approval"
                print(f"   {status}: {action.action_type.value}")
                print(f"     Target: {action.target}")
                print(f"     Confidence: {action.confidence:.2%}")
        
        print(f"\n⏱️  Cycle Time: {metrics['cycle_time_ms']:.1f}ms")
        print("="*80)
    
    def run(self, cycles: int = 10, inject_scenarios: bool = True):
        """Run the agent for specified number of cycles"""
        self.running = True
        print("🚀 Payment Operations Agent Starting...")
        print(f"   Will run {cycles} cycles")
        print(f"   Observation window: {self.observation_window} events/cycle")
        
        for cycle in range(cycles):
            print(f"\n\n{'🔄 CYCLE ' + str(cycle + 1):^80}")
            
            # Inject scenarios at specific cycles for demonstration
            if inject_scenarios:
                if cycle == 3:
                    self.data_stream.inject_scenario('issuer_down', 'HDFC_ISSUER')
                elif cycle == 6:
                    self.data_stream.inject_scenario('network_slow', 'ICICI_ISSUER')
                elif cycle == 9:
                    self.data_stream.inject_scenario('normal')
            
            cycle_result = self.run_cycle()
            self.print_status(cycle_result)
            
            time.sleep(0.5)  # Brief pause between cycles
        
        self.running = False
        self.print_final_report()
    
    def print_final_report(self):
        """Print final performance report"""
        print(f"\n\n{'='*80}")
        print(f"{'📈 FINAL PERFORMANCE REPORT':^80}")
        print(f"{'='*80}\n")
        
        if not self.metrics_history:
            return
        
        # Overall statistics
        avg_success = statistics.mean(m['success_rate'] for m in self.metrics_history)
        avg_latency = statistics.mean(m['avg_latency'] for m in self.metrics_history)
        total_patterns = sum(m['patterns_detected'] for m in self.metrics_history)
        total_actions = sum(m['actions_taken'] for m in self.metrics_history)
        
        print(f"Total Transactions Processed: {self.transaction_counter:,}")
        print(f"Average Success Rate: {avg_success:.2%}")
        print(f"Average Latency: {avg_latency:.0f}ms")
        print(f"Total Patterns Detected: {total_patterns}")
        print(f"Total Actions Taken: {total_actions}")
        
        # Action effectiveness
        print(f"\n{'ACTION EFFECTIVENESS':^80}")
        print("-" * 80)
        
        successful_actions = 0
        failed_actions = 0
        
        for action in self.memory.actions_taken:
            if action.outcome_metrics:
                if action.outcome_metrics.get('action_successful', False):
                    successful_actions += 1
                    improvement = action.outcome_metrics['success_rate_improvement']
                    print(f"✅ {action.action_type.value} on {action.target}: "
                          f"+{improvement:.2%} success rate")
                else:
                    failed_actions += 1
                    degradation = action.outcome_metrics['success_rate_improvement']
                    print(f"❌ {action.action_type.value} on {action.target}: "
                          f"{degradation:.2%} success rate (rolled back)")
        
        if successful_actions + failed_actions > 0:
            effectiveness = successful_actions / (successful_actions + failed_actions)
            print(f"\nOverall Action Effectiveness: {effectiveness:.2%}")
        
        # Performance over time
        print(f"\n{'PERFORMANCE TREND':^80}")
        print("-" * 80)
        
        first_half = self.metrics_history[:len(self.metrics_history)//2]
        second_half = self.metrics_history[len(self.metrics_history)//2:]
        
        if first_half and second_half:
            first_success = statistics.mean(m['success_rate'] for m in first_half)
            second_success = statistics.mean(m['success_rate'] for m in second_half)
            improvement = second_success - first_success
            
            print(f"First Half Avg Success Rate: {first_success:.2%}")
            print(f"Second Half Avg Success Rate: {second_success:.2%}")
            print(f"Overall Improvement: {improvement:+.2%}")
        
        print(f"\n{'='*80}\n")
    # --- HITL: APPROVAL FUNCTIONS ---
    def get_pending_approvals(self):
        """Returns the list of actions waiting for your permission"""
        return list(self.action_executor.pending_approvals.values())

    def review_action(self, action_id: str, approved: bool):
        """Call this to Approve (True) or Reject (False) an action"""
        executor = self.action_executor
        
        if action_id in executor.pending_approvals:
            action = executor.pending_approvals.pop(action_id)
            
            if approved:
                print(f"✅ HUMAN APPROVED: {action.action_type.value}")
                action.approved = True
                executor.execute(action) # Run it now!
            else:
                print(f"❌ HUMAN REJECTED: {action.action_type.value}")
    # --------------------------------


def main():
    """Main entry point"""
    agent = PaymentOperationsAgent()
    
    # Run the agent
    agent.run(cycles=12, inject_scenarios=True)
    
    # Export final state for analysis
    report = {
        'total_transactions': agent.transaction_counter,
        'actions_taken': [a.to_dict() for a in agent.memory.actions_taken],
        'patterns_detected': [p.to_dict() for p in agent.memory.detected_patterns.values()],
        'metrics_history': [{
            'timestamp': m['timestamp'].isoformat(),
            'success_rate': m['success_rate'],
            'avg_latency': m['avg_latency'],
            'patterns_detected': m['patterns_detected'],
            'actions_taken': m['actions_taken']
        } for m in agent.metrics_history],
        'baseline_metrics': agent.memory.baseline_metrics
    }
    
    with open('agent_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("📊 Full report saved to agent_report.json")


if __name__ == "__main__":
    main()
