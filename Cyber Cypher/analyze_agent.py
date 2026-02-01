"""
Visualization and Analysis for Payment Operations Agent
Analyzes agent performance, action effectiveness, and learning progress
"""

import json
import statistics
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


class AgentAnalyzer:
    """Analyzes agent performance from saved reports"""
    
    def __init__(self, report_path: str = None):
        import os
        if report_path is None:
            # Default to current directory, same as payment_agent.py saves it
            report_path = os.path.join(os.getcwd(), 'agent_report.json')
        with open(report_path, 'r') as f:
            self.report = json.load(f)
    
    def analyze_performance(self):
        """Analyze overall agent performance"""
        print("="*80)
        print("📊 AGENT PERFORMANCE ANALYSIS")
        print("="*80)
        
        metrics = self.report['metrics_history']
        
        # Success rate over time
        success_rates = [m['success_rate'] for m in metrics]
        latencies = [m['avg_latency'] for m in metrics]
        
        print(f"\n{'SUCCESS RATE ANALYSIS':^80}")
        print("-"*80)
        print(f"  Minimum: {min(success_rates):.2%}")
        print(f"  Maximum: {max(success_rates):.2%}")
        print(f"  Average: {statistics.mean(success_rates):.2%}")
        print(f"  Std Dev: {statistics.stdev(success_rates):.2%}")
        
        # Trend analysis
        first_quarter = success_rates[:len(success_rates)//4]
        last_quarter = success_rates[-len(success_rates)//4:]
        
        if first_quarter and last_quarter:
            improvement = statistics.mean(last_quarter) - statistics.mean(first_quarter)
            print(f"  Trend: {improvement:+.2%} (first vs last quarter)")
        
        print(f"\n{'LATENCY ANALYSIS':^80}")
        print("-"*80)
        print(f"  Minimum: {min(latencies):.0f}ms")
        print(f"  Maximum: {max(latencies):.0f}ms")
        print(f"  Average: {statistics.mean(latencies):.0f}ms")
        print(f"  Std Dev: {statistics.stdev(latencies):.0f}ms")
    
    def analyze_patterns(self):
        """Analyze detected patterns"""
        print(f"\n{'PATTERN DETECTION ANALYSIS':^80}")
        print("-"*80)
        
        patterns = self.report['patterns_detected']
        
        # Group by type
        by_type = defaultdict(list)
        for pattern in patterns:
            by_type[pattern['pattern_type']].append(pattern)
        
        print(f"\n  Total Patterns Detected: {len(patterns)}")
        print(f"\n  Breakdown by Type:")
        
        for ptype, plist in sorted(by_type.items()):
            avg_severity = statistics.mean(p['severity'] for p in plist)
            print(f"    • {ptype}: {len(plist)} occurrences (avg severity: {avg_severity:.2f})")
        
        # Most severe patterns
        if patterns:
            print(f"\n  Top 5 Most Severe Patterns:")
            sorted_patterns = sorted(patterns, key=lambda p: p['severity'], reverse=True)[:5]
            
            for i, pattern in enumerate(sorted_patterns, 1):
                print(f"    {i}. {pattern['pattern_type']}")
                print(f"       Severity: {pattern['severity']:.2f}")
                print(f"       Scope: {pattern['affected_scope']}")
                print(f"       Metrics: {pattern['metrics']}")
    
    def analyze_actions(self):
        """Analyze agent actions and their effectiveness"""
        print(f"\n{'ACTION EFFECTIVENESS ANALYSIS':^80}")
        print("-"*80)
        
        actions = self.report['actions_taken']
        
        # Group by type
        by_type = defaultdict(list)
        for action in actions:
            by_type[action['action_type']].append(action)
        
        print(f"\n  Total Actions Taken: {len(actions)}")
        print(f"\n  Breakdown by Type:")
        
        for atype, alist in sorted(by_type.items()):
            executed = sum(1 for a in alist if a['executed'])
            approved = sum(1 for a in alist if a['approved'])
            print(f"    • {atype}:")
            print(f"      Total: {len(alist)} | Executed: {executed} | Approved: {approved}")
        
        # Evaluate outcomes
        actions_with_outcomes = [a for a in actions if a['outcome_metrics']]
        
        if actions_with_outcomes:
            print(f"\n  Action Outcomes ({len(actions_with_outcomes)} evaluated):")
            print("-"*80)
            
            successful = 0
            total_success_improvement = 0
            total_latency_improvement = 0
            
            for action in actions_with_outcomes:
                metrics = action['outcome_metrics']
                
                if metrics.get('action_successful', False):
                    successful += 1
                    success_imp = metrics.get('success_rate_improvement', 0)
                    latency_imp = metrics.get('latency_improvement', 0)
                    
                    total_success_improvement += success_imp
                    total_latency_improvement += latency_imp
                    
                    print(f"\n    ✅ {action['action_type']} on {action['target']}")
                    print(f"       Success Rate: {success_imp:+.2%}")
                    print(f"       Latency: {latency_imp:+.0f}ms")
                    print(f"       Confidence: {action['confidence']:.2%}")
                else:
                    print(f"\n    ❌ {action['action_type']} on {action['target']}")
                    print(f"       Success Rate: {metrics.get('success_rate_improvement', 0):+.2%}")
                    print(f"       Status: Rolled back")
            
            effectiveness = successful / len(actions_with_outcomes) * 100
            avg_success_imp = total_success_improvement / len(actions_with_outcomes)
            avg_latency_imp = total_latency_improvement / len(actions_with_outcomes)
            
            print(f"\n  {'OVERALL EFFECTIVENESS':^80}")
            print(f"  Action Success Rate: {effectiveness:.1f}%")
            print(f"  Avg Success Rate Improvement: {avg_success_imp:+.2%}")
            print(f"  Avg Latency Improvement: {avg_latency_imp:+.0f}ms")
    
    def analyze_learning(self):
        """Analyze agent's learning progress"""
        print(f"\n{'LEARNING PROGRESS ANALYSIS':^80}")
        print("-"*80)
        
        actions = self.report['actions_taken']
        
        # Track confidence over time
        if actions:
            print("\n  Confidence Evolution:")
            
            first_half = actions[:len(actions)//2]
            second_half = actions[len(actions)//2:]
            
            if first_half:
                avg_conf_first = statistics.mean(a['confidence'] for a in first_half)
                print(f"    First Half Avg Confidence: {avg_conf_first:.2%}")
            
            if second_half:
                avg_conf_second = statistics.mean(a['confidence'] for a in second_half)
                print(f"    Second Half Avg Confidence: {avg_conf_second:.2%}")
            
            if first_half and second_half:
                improvement = avg_conf_second - avg_conf_first
                print(f"    Confidence Growth: {improvement:+.2%}")
        
        # Analyze response time to patterns
        metrics = self.report['metrics_history']
        
        cycles_with_patterns = [m for m in metrics if m['patterns_detected'] > 0]
        cycles_with_actions = [m for m in metrics if m['actions_taken'] > 0]
        
        print(f"\n  Response Efficiency:")
        print(f"    Cycles with Patterns: {len(cycles_with_patterns)}")
        print(f"    Cycles with Actions: {len(cycles_with_actions)}")
        
        if cycles_with_patterns:
            action_rate = len(cycles_with_actions) / len(cycles_with_patterns) * 100
            print(f"    Action Rate: {action_rate:.1f}% (actions per pattern detection)")
    
    def generate_timeline(self):
        """Generate a timeline of key events"""
        print(f"\n{'EVENT TIMELINE':^80}")
        print("-"*80)
        
        metrics = self.report['metrics_history']
        actions = self.report['actions_taken']
        
        print("\n  Key Events in Agent's Operation:")
        
        for i, m in enumerate(metrics):
            timestamp = datetime.fromisoformat(m['timestamp'])
            
            # Check for significant changes
            events = []
            
            if m['patterns_detected'] > 0:
                events.append(f"{m['patterns_detected']} patterns detected")
            
            if m['actions_taken'] > 0:
                events.append(f"{m['actions_taken']} actions taken")
            
            # Check for significant metric changes
            if i > 0:
                prev = metrics[i-1]
                success_change = m['success_rate'] - prev['success_rate']
                
                if abs(success_change) > 0.1:
                    direction = "↑" if success_change > 0 else "↓"
                    events.append(f"Success rate {direction} {abs(success_change):.1%}")
            
            if events:
                print(f"\n    Cycle {i+1} ({timestamp.strftime('%H:%M:%S')})")
                for event in events:
                    print(f"      • {event}")
    
    def generate_summary(self):
        """Generate executive summary"""
        print("\n" + "="*80)
        print(f"{'🎯 EXECUTIVE SUMMARY':^80}")
        print("="*80)
        
        metrics = self.report['metrics_history']
        actions = self.report['actions_taken']
        patterns = self.report['patterns_detected']
        
        # Overall stats
        total_txns = self.report['total_transactions']
        avg_success = statistics.mean(m['success_rate'] for m in metrics)
        
        print(f"\n  Transactions Processed: {total_txns:,}")
        print(f"  Average Success Rate: {avg_success:.2%}")
        print(f"  Total Patterns Detected: {len(patterns)}")
        print(f"  Total Actions Taken: {len(actions)}")
        
        # Action effectiveness
        actions_with_outcomes = [a for a in actions if a['outcome_metrics']]
        if actions_with_outcomes:
            successful = sum(1 for a in actions_with_outcomes 
                           if a['outcome_metrics'].get('action_successful', False))
            effectiveness = successful / len(actions_with_outcomes) * 100
            print(f"  Action Success Rate: {effectiveness:.1f}%")
        
        # Performance improvement
        first_quarter = metrics[:len(metrics)//4]
        last_quarter = metrics[-len(metrics)//4:]
        
        if first_quarter and last_quarter:
            improvement = (statistics.mean(m['success_rate'] for m in last_quarter) - 
                         statistics.mean(m['success_rate'] for m in first_quarter))
            print(f"  Overall Performance Improvement: {improvement:+.2%}")
        
        print("\n" + "="*80)
    
    def run_full_analysis(self):
        """Run complete analysis"""
        self.generate_summary()
        self.analyze_performance()
        self.analyze_patterns()
        self.analyze_actions()
        self.analyze_learning()
        self.generate_timeline()
        
        print("\n" + "="*80)
        print("Analysis complete! 🎉")
        print("="*80 + "\n")


def main():
    """Run analysis on agent report"""
    import os
    
    # Look for report in current directory (where payment_agent.py saves it)
    report_path = os.path.join(os.getcwd(), 'agent_report.json')
    
    if not os.path.exists(report_path):
        print("❌ No agent report found!")
        print(f"   Looking for: {report_path}")
        print("   Please run payment_agent.py first to generate the report.")
        return
    
    analyzer = AgentAnalyzer(report_path)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
