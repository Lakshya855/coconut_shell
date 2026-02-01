"""
Interactive Demo for Payment Operations Agent
Allows real-time control and observation of agent behavior
"""

import sys
import time
from payment_agent import (
    PaymentOperationsAgent,
    PaymentStatus,
    ActionType
)


class InteractiveDemo:
    """Interactive demonstration of the agent"""
    
    def __init__(self):
        self.agent = PaymentOperationsAgent()
        self.running = False
    
    def print_menu(self):
        """Print interactive menu"""
        print("\n" + "="*80)
        print("🎮 INTERACTIVE PAYMENT AGENT DEMO")
        print("="*80)
        print("\nOptions:")
        print("  1. Run automatic demo (12 cycles with scenarios)")
        print("  2. Run single cycle")
        print("  3. Inject issuer downtime scenario")
        print("  4. Inject network slowdown scenario")
        print("  5. Inject retry storm scenario")
        print("  6. Reset to normal operation")
        print("  7. View current status")
        print("  8. View agent memory")
        print("  9. Approve pending actions")
        print("  0. Exit")
        print("="*80)
    
    def run_auto_demo(self):
        """Run automatic demonstratio2
        n"""
        print("\n🚀 Starting automatic demo...")
        print("   This will run 12 cycles with automatic scenario injection")
        print("   Press Ctrl+C to stop\n")
        
        time.sleep(2)
        self.agent.run(cycles=12, inject_scenarios=True)
    
    def run_single_cycle(self):
        """Run a single agent cycle"""
        print("\n⚡ Running single cycle...")
        
        cycle_result = self.agent.run_cycle()
        self.agent.print_status(cycle_result)
        
        return cycle_result
    
    def inject_scenario(self, scenario_type: str, target: str = None):
        """Inject a specific scenario"""
        self.agent.data_stream.inject_scenario(scenario_type, target)
        print(f"\n✅ Scenario injected: {scenario_type}")
        if target:
            print(f"   Target: {target}")
    
    def view_status(self):
        """View current agent status"""
        print("\n" + "="*80)
        print("📊 CURRENT AGENT STATUS")
        print("="*80)
        
        # Recent metrics
        if self.agent.metrics_history:
            latest = self.agent.metrics_history[-1]
            print(f"\n  Total Transactions: {latest['total_transactions']:,}")
            print(f"  Success Rate: {latest['success_rate']:.2%}")
            print(f"  Avg Latency: {latest['avg_latency']:.0f}ms")
            print(f"  Patterns Detected: {latest['patterns_detected']}")
            print(f"  Actions Taken: {latest['actions_taken']}")
        else:
            print("\n  No cycles run yet. Run a cycle to see status.")
        
        # Active scenario
        print(f"\n  Current Scenario: {self.agent.data_stream.current_scenario}")
        if self.agent.data_stream.scenario_target:
            print(f"  Target: {self.agent.data_stream.scenario_target}")
        
        # Baseline metrics
        if self.agent.memory.baseline_metrics:
            print("\n  Baseline Metrics:")
            for key, value in self.agent.memory.baseline_metrics.items():
                if isinstance(value, float):
                    if 'rate' in key:
                        print(f"    {key}: {value:.2%}")
                    else:
                        print(f"    {key}: {value:.2f}")
    
    def view_memory(self):
        """View agent memory contents"""
        print("\n" + "="*80)
        print("🧠 AGENT MEMORY")
        print("="*80)
        
        # Recent events summary
        recent = self.agent.memory.get_recent_events(100)
        if recent:
            success_count = sum(1 for e in recent if e.status == PaymentStatus.SUCCESS)
            print(f"\n  Recent Events Window: {len(self.agent.memory.recent_events)}/{self.agent.memory.window_size}")
            print(f"  Last 100 Events:")
            print(f"    Success: {success_count}")
            print(f"    Failed: {100 - success_count}")
            
            # Group by issuer
            from collections import defaultdict
            by_issuer = defaultdict(int)
            for e in recent:
                by_issuer[e.issuer] += 1
            
            print(f"\n  Distribution by Issuer:")
            for issuer, count in sorted(by_issuer.items(), key=lambda x: x[1], reverse=True):
                print(f"    {issuer}: {count}")
        
        # Actions in memory
        print(f"\n  Total Actions Recorded: {len(self.agent.memory.actions_taken)}")
        
        if self.agent.memory.actions_taken:
            print(f"\n  Recent Actions (last 5):")
            for action in self.agent.memory.actions_taken[-5:]:
                status = "✓ Executed" if action.executed else "⏳ Pending"
                print(f"    {status}: {action.action_type.value} on {action.target}")
                print(f"      Confidence: {action.confidence:.2%}")
                if action.outcome_metrics:
                    improvement = action.outcome_metrics.get('success_rate_improvement', 0)
                    print(f"      Outcome: {improvement:+.2%} success rate")
        
        # Detected patterns
        print(f"\n  Active Patterns: {len(self.agent.memory.detected_patterns)}")
        
        if self.agent.memory.detected_patterns:
            print(f"\n  Top Patterns by Severity:")
            sorted_patterns = sorted(
                self.agent.memory.detected_patterns.values(),
                key=lambda p: p.severity,
                reverse=True
            )[:5]
            
            for pattern in sorted_patterns:
                print(f"    • {pattern.pattern_type}")
                print(f"      Severity: {pattern.severity:.2f}")
                print(f"      Scope: {pattern.affected_scope}")
    
    def approve_pending_actions(self):
        """Approve pending actions"""
        pending = [a for a in self.agent.memory.actions_taken 
                  if a.requires_approval and not a.approved and not a.executed]
        
        if not pending:
            print("\n✅ No pending actions requiring approval")
            return
        
        print("\n" + "="*80)
        print("⚠️  PENDING ACTIONS REQUIRING APPROVAL")
        print("="*80)
        
        for i, action in enumerate(pending, 1):
            print(f"\n  {i}. {action.action_type.value} on {action.target}")
            print(f"     Confidence: {action.confidence:.2%}")
            print(f"     Reasoning: {action.reasoning}")
            print(f"     Parameters: {action.parameters}")
        
        print("\n  Options:")
        print("    a - Approve all")
        print("    [number] - Approve specific action")
        print("    n - Cancel")
        
        choice = input("\n  Your choice: ").strip().lower()
        
        if choice == 'a':
            for action in pending:
                action.approved = True
                self.agent.action_executor.execute(action)
            print(f"\n✅ Approved and executed {len(pending)} actions")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(pending):
                pending[idx].approved = True
                self.agent.action_executor.execute(pending[idx])
                print(f"\n✅ Approved and executed action {choice}")
            else:
                print("\n❌ Invalid action number")
        else:
            print("\n❌ Cancelled")
    
    def run(self):
        """Run interactive demo"""
        print("\n🎯 Welcome to the Payment Operations Agent Demo!")
        print("   This is an autonomous AI agent for managing payment operations")
        
        while True:
            self.print_menu()
            
            try:
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    self.run_auto_demo()
                elif choice == '2':
                    self.run_single_cycle()
                elif choice == '3':
                    target = input("  Enter issuer code (or press Enter for HDFC_ISSUER): ").strip()
                    self.inject_scenario('issuer_down', target or 'HDFC_ISSUER')
                elif choice == '4':
                    target = input("  Enter issuer code (or press Enter for ICICI_ISSUER): ").strip()
                    self.inject_scenario('network_slow', target or 'ICICI_ISSUER')
                elif choice == '5':
                    self.inject_scenario('retry_storm')
                elif choice == '6':
                    self.inject_scenario('normal')
                elif choice == '7':
                    self.view_status()
                elif choice == '8':
                    self.view_memory()
                elif choice == '9':
                    self.approve_pending_actions()
                elif choice == '0':
                    print("\n👋 Exiting demo. Goodbye!")
                    break
                else:
                    print("\n❌ Invalid choice. Please try again.")
                
                # Small pause for readability
                if choice != '1':  # Auto demo has its own pauses
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Returning to menu...")
                time.sleep(1)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    demo = InteractiveDemo()
    demo.run()


if __name__ == "__main__":
    main()
