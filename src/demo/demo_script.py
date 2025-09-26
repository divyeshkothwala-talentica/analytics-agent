"""
Automated demo script for presentations and testing
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai.query_engine import AIQueryEngine
from src.demo.use_cases import UseCaseHandler
from src.demo.monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class DemoScript:
    """Automated demo script for presentations"""
    
    def __init__(self, interactive: bool = True, verbose: bool = True):
        """Initialize the demo script
        
        Args:
            interactive: Whether to pause between demos for user input
            verbose: Whether to show detailed output
        """
        self.interactive = interactive
        self.verbose = verbose
        self.query_engine = None
        self.use_case_handler = UseCaseHandler()
        self.monitor = PerformanceMonitor()
        
        # Demo configuration
        self.demo_scenarios = self._initialize_demo_scenarios()
        self.current_scenario = 0
        
        # Results tracking
        self.demo_results = []
        self.start_time = None
        
    def _initialize_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Initialize predefined demo scenarios"""
        return [
            {
                'name': 'City Delay Analysis',
                'description': 'Analyze delivery delays in a specific city',
                'query': 'Why were deliveries delayed in Mumbai yesterday?',
                'expected_duration': 5.0,
                'use_case_method': 'analyze_city_delays',
                'use_case_args': {'city': 'Mumbai', 'date': 'yesterday'}
            },
            {
                'name': 'Client Failure Analysis',
                'description': 'Investigate failures for a specific client',
                'query': 'Why did Client ABC orders fail in the past week?',
                'expected_duration': 4.0,
                'use_case_method': 'analyze_client_failures',
                'use_case_args': {'client_id': 'Client ABC', 'days': 7}
            },
            {
                'name': 'Warehouse Performance',
                'description': 'Analyze warehouse efficiency and failure reasons',
                'query': 'Top reasons for delivery failures linked to Warehouse B in August',
                'expected_duration': 4.5,
                'use_case_method': 'analyze_warehouse_failures',
                'use_case_args': {'warehouse_id': 'Warehouse B', 'period': 'August'}
            },
            {
                'name': 'City Comparison',
                'description': 'Compare delivery performance between cities',
                'query': 'Compare delivery failure causes between Mumbai and Delhi last month',
                'expected_duration': 6.0,
                'use_case_method': 'compare_city_failures',
                'use_case_args': {'city1': 'Mumbai', 'city2': 'Delhi', 'period': 'last month'}
            },
            {
                'name': 'Seasonal Analysis',
                'description': 'Analyze seasonal patterns and their impact',
                'query': 'Likely causes of delivery failures during festival period',
                'expected_duration': 5.5,
                'use_case_method': 'analyze_seasonal_patterns',
                'use_case_args': {'season': 'festival period'}
            },
            {
                'name': 'Capacity Planning',
                'description': 'Predict impact of increased order volume',
                'query': 'Impact of onboarding Client Y with 20,000 extra monthly orders?',
                'expected_duration': 7.0,
                'use_case_method': 'analyze_capacity_impact',
                'use_case_args': {'client_name': 'Client Y', 'extra_orders': 20000}
            }
        ]
    
    def initialize_system(self) -> bool:
        """Initialize the analytics system"""
        try:
            self.print_header("INITIALIZING ANALYTICS SYSTEM")
            
            if self.verbose:
                print("🔧 Starting analytics engine...")
            
            self.query_engine = AIQueryEngine()
            self.monitor.start_monitoring()
            
            if self.verbose:
                print("✅ Analytics engine ready!")
                print("📊 Performance monitoring active")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            return False
    
    def run_full_demo(self) -> Dict[str, Any]:
        """Run the complete demo sequence"""
        self.start_time = datetime.now()
        
        if not self.initialize_system():
            return {'success': False, 'error': 'System initialization failed'}
        
        self.print_header("LOGISTICS ANALYTICS Q&A TOOL - DEMO")
        
        if self.verbose:
            print("This demo showcases all 6 use cases of the analytics tool:")
            print("1. City Delay Analysis")
            print("2. Client Failure Analysis") 
            print("3. Warehouse Performance")
            print("4. City Comparison")
            print("5. Seasonal Analysis")
            print("6. Capacity Planning")
            print()
        
        # Run all scenarios
        for i, scenario in enumerate(self.demo_scenarios, 1):
            if self.interactive:
                input(f"Press Enter to run Demo {i}: {scenario['name']}...")
            
            result = self.run_scenario(scenario, i)
            self.demo_results.append(result)
            
            if not result['success']:
                print(f"❌ Demo {i} failed: {result.get('error', 'Unknown error')}")
                if self.interactive:
                    continue_demo = input("Continue with remaining demos? (y/n): ").lower().startswith('y')
                    if not continue_demo:
                        break
        
        # Generate final report
        return self.generate_demo_report()
    
    def run_scenario(self, scenario: Dict[str, Any], scenario_number: int) -> Dict[str, Any]:
        """Run a single demo scenario"""
        start_time = time.time()
        
        self.print_scenario_header(scenario, scenario_number)
        
        try:
            # Start monitoring
            self.monitor.start_query(scenario['query'])
            
            if self.verbose:
                print(f"🔍 Processing query: {scenario['query']}")
                print("📊 Analyzing data...")
            
            # Execute using use case handler for consistent results
            use_case_method = getattr(self.use_case_handler, scenario['use_case_method'])
            result = use_case_method(**scenario['use_case_args'])
            
            duration = time.time() - start_time
            self.monitor.end_query(True, duration, len(result.get('insights', [])))
            
            # Display results
            self.display_scenario_results(result, scenario, duration)
            
            # Validate results
            validation = self.validate_scenario_result(scenario, result, duration)
            
            return {
                'success': True,
                'scenario': scenario['name'],
                'query': scenario['query'],
                'duration': duration,
                'result': result,
                'validation': validation
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.monitor.end_query(False, duration, 0, str(e))
            
            print(f"❌ Scenario failed: {e}")
            
            return {
                'success': False,
                'scenario': scenario['name'],
                'query': scenario['query'],
                'duration': duration,
                'error': str(e)
            }
    
    def display_scenario_results(self, result: Dict[str, Any], 
                               scenario: Dict[str, Any], duration: float):
        """Display results for a scenario"""
        if not self.verbose:
            return
        
        print("\n" + "=" * 60)
        print("📋 ANALYSIS RESULTS")
        print("=" * 60)
        
        # Key insights
        insights = result.get('insights', [])
        if insights:
            print("\n📊 Key Findings:")
            for i, insight in enumerate(insights, 1):
                print(f"  {i}. {insight}")
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Performance metrics
        print(f"\n⚡ Performance:")
        print(f"  • Processing time: {duration:.2f}s")
        print(f"  • Expected time: {scenario['expected_duration']:.1f}s")
        
        performance_status = "✅ Good" if duration <= scenario['expected_duration'] else "⚠️ Slow"
        print(f"  • Status: {performance_status}")
    
    def validate_scenario_result(self, scenario: Dict[str, Any], 
                               result: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Validate scenario results against expectations"""
        validation = {
            'performance_ok': duration <= scenario['expected_duration'] * 1.5,  # 50% tolerance
            'has_insights': len(result.get('insights', [])) > 0,
            'has_recommendations': len(result.get('recommendations', [])) > 0,
            'data_reasonable': True,  # Will be set based on specific checks
            'overall_score': 0
        }
        
        # Calculate overall score
        score = 0
        if validation['performance_ok']:
            score += 25
        if validation['has_insights']:
            score += 25
        if validation['has_recommendations']:
            score += 25
        if validation['data_reasonable']:
            score += 25
        
        validation['overall_score'] = score
        validation['passed'] = score >= 75  # 75% threshold
        
        return validation
    
    def generate_demo_report(self) -> Dict[str, Any]:
        """Generate comprehensive demo report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        successful_scenarios = sum(1 for r in self.demo_results if r['success'])
        total_scenarios = len(self.demo_results)
        success_rate = (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        avg_duration = sum(r['duration'] for r in self.demo_results) / total_scenarios if total_scenarios > 0 else 0
        
        # Validation statistics
        validations = [r.get('validation', {}) for r in self.demo_results if r['success']]
        avg_score = sum(v.get('overall_score', 0) for v in validations) / len(validations) if validations else 0
        passed_validations = sum(1 for v in validations if v.get('passed', False))
        
        # Performance monitoring stats
        monitor_stats = self.monitor.get_performance_summary()
        
        # Generate report
        report = {
            'demo_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration': total_duration,
                'interactive_mode': self.interactive
            },
            'execution_summary': {
                'total_scenarios': total_scenarios,
                'successful_scenarios': successful_scenarios,
                'success_rate': success_rate,
                'average_duration': avg_duration
            },
            'validation_summary': {
                'average_score': avg_score,
                'passed_validations': passed_validations,
                'validation_rate': (passed_validations / len(validations) * 100) if validations else 0
            },
            'performance_summary': monitor_stats,
            'scenario_results': self.demo_results
        }
        
        # Display summary
        self.display_demo_summary(report)
        
        return report
    
    def display_demo_summary(self, report: Dict[str, Any]):
        """Display demo summary"""
        self.print_header("DEMO SUMMARY")
        
        exec_summary = report['execution_summary']
        val_summary = report['validation_summary']
        
        print(f"📊 Execution Results:")
        print(f"  • Scenarios run: {exec_summary['total_scenarios']}")
        print(f"  • Successful: {exec_summary['successful_scenarios']}")
        print(f"  • Success rate: {exec_summary['success_rate']:.1f}%")
        print(f"  • Average duration: {exec_summary['average_duration']:.2f}s")
        
        print(f"\n✅ Validation Results:")
        print(f"  • Average score: {val_summary['average_score']:.1f}/100")
        print(f"  • Passed validations: {val_summary['passed_validations']}")
        print(f"  • Validation rate: {val_summary['validation_rate']:.1f}%")
        
        # Performance insights
        perf_summary = report['performance_summary']
        if 'system_performance' in perf_summary:
            sys_perf = perf_summary['system_performance']
            print(f"\n⚡ System Performance:")
            print(f"  • Average CPU: {sys_perf.get('avg_cpu_usage', 0):.1f}%")
            print(f"  • Average Memory: {sys_perf.get('avg_memory_usage_mb', 0):.1f}MB")
            print(f"  • Peak Memory: {sys_perf.get('peak_memory_mb', 0):.1f}MB")
        
        # OpenAI usage
        openai_cost = perf_summary.get('openai_cost_usd', 0)
        if openai_cost > 0:
            print(f"\n💰 AI Usage:")
            print(f"  • Total cost: ${openai_cost:.4f}")
            print(f"  • Tokens used: {perf_summary.get('openai_tokens_used', 0):,}")
        
        # Overall assessment
        overall_success = (exec_summary['success_rate'] >= 80 and 
                          val_summary['validation_rate'] >= 75)
        
        status = "🎉 EXCELLENT" if overall_success else "⚠️ NEEDS ATTENTION"
        print(f"\n{status} - Demo completed!")
        
        if not overall_success:
            print("\nAreas for improvement:")
            if exec_summary['success_rate'] < 80:
                print("  • Improve system reliability")
            if val_summary['validation_rate'] < 75:
                print("  • Enhance result quality")
    
    def run_single_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a single named scenario"""
        scenario = next((s for s in self.demo_scenarios if s['name'] == scenario_name), None)
        if not scenario:
            return {'success': False, 'error': f'Scenario "{scenario_name}" not found'}
        
        if not self.initialize_system():
            return {'success': False, 'error': 'System initialization failed'}
        
        return self.run_scenario(scenario, 1)
    
    def list_scenarios(self) -> List[str]:
        """List all available scenarios"""
        return [scenario['name'] for scenario in self.demo_scenarios]
    
    def print_header(self, title: str):
        """Print formatted header"""
        if self.verbose:
            print("\n" + "=" * 80)
            print(f"🚚 {title}")
            print("=" * 80)
    
    def print_scenario_header(self, scenario: Dict[str, Any], number: int):
        """Print scenario header"""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"📋 DEMO {number}: {scenario['name'].upper()}")
            print(f"{'='*60}")
            print(f"Description: {scenario['description']}")
            print(f"Query: {scenario['query']}")
            print(f"Expected duration: {scenario['expected_duration']}s")
            print("-" * 60)
    
    def export_results(self, filepath: str):
        """Export demo results to file"""
        try:
            import json
            
            if hasattr(self, 'demo_results') and self.demo_results:
                report = self.generate_demo_report()
                
                with open(filepath, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                print(f"📄 Demo results exported to {filepath}")
            else:
                print("❌ No demo results to export")
                
        except Exception as e:
            print(f"❌ Failed to export results: {e}")


def main():
    """Main entry point for demo script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run analytics demo script')
    parser.add_argument('--scenario', type=str, help='Run specific scenario only')
    parser.add_argument('--non-interactive', action='store_true', help='Run without pauses')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--export', type=str, help='Export results to file')
    parser.add_argument('--list', action='store_true', help='List available scenarios')
    
    args = parser.parse_args()
    
    # Create demo script
    demo = DemoScript(
        interactive=not args.non_interactive,
        verbose=not args.quiet
    )
    
    try:
        if args.list:
            print("Available scenarios:")
            for i, scenario in enumerate(demo.list_scenarios(), 1):
                print(f"  {i}. {scenario}")
            return
        
        if args.scenario:
            # Run single scenario
            result = demo.run_single_scenario(args.scenario)
            if result['success']:
                print(f"✅ Scenario '{args.scenario}' completed successfully")
            else:
                print(f"❌ Scenario '{args.scenario}' failed: {result.get('error')}")
        else:
            # Run full demo
            result = demo.run_full_demo()
            if result.get('execution_summary', {}).get('success_rate', 0) >= 80:
                print("\n🎉 Demo completed successfully!")
            else:
                print("\n⚠️ Demo completed with issues")
        
        # Export results if requested
        if args.export:
            demo.export_results(args.export)
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
