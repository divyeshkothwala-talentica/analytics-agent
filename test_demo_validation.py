#!/usr/bin/env python3
"""
Comprehensive validation test script for the demo interface
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.main import AnalyticsCLI
from src.demo.use_cases import UseCaseHandler
from src.demo.demo_script import DemoScript
from src.demo.monitor import PerformanceMonitor
from src.demo.data_generator import DemoDataGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemoValidator:
    """Comprehensive validation for all demo components"""
    
    def __init__(self):
        """Initialize the validator"""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        
        self.use_case_handler = UseCaseHandler()
        self.monitor = PerformanceMonitor()
        self.data_generator = DemoDataGenerator()
        
        logger.info("Demo validator initialized")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        print("🧪 RUNNING COMPREHENSIVE DEMO VALIDATION")
        print("=" * 60)
        
        test_methods = [
            ('use_cases', self.test_use_cases),
            ('sample_queries', self.test_sample_queries),
            ('data_generation', self.test_data_generation),
            ('demo_script', self.test_demo_script),
            ('performance_monitor', self.test_performance_monitor),
            ('cli_interface', self.test_cli_interface),
            ('web_interface', self.test_web_interface)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n🔍 Testing: {test_name.replace('_', ' ').title()}")
            print("-" * 40)
            
            try:
                start_time = time.time()
                result = test_method()
                duration = time.time() - start_time
                
                result['duration'] = duration
                result['status'] = 'passed' if result.get('success', False) else 'failed'
                
                self.results['tests'][test_name] = result
                
                if result['status'] == 'passed':
                    print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
                else:
                    print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                    if 'error' in result:
                        print(f"   Error: {result['error']}")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results['tests'][test_name] = {
                    'status': 'error',
                    'error': str(e),
                    'duration': duration
                }
                print(f"💥 {test_name} - ERROR ({duration:.2f}s): {e}")
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def test_use_cases(self) -> Dict[str, Any]:
        """Test all use case implementations"""
        results = {'success': True, 'details': {}}
        
        use_cases = [
            ('analyze_city_delays', {'city': 'Mumbai', 'date': 'yesterday'}),
            ('analyze_client_failures', {'client_id': 'Client_ABC', 'days': 7}),
            ('analyze_warehouse_failures', {'warehouse_id': 'Warehouse_B', 'period': 'August'}),
            ('compare_city_failures', {'city1': 'Mumbai', 'city2': 'Delhi', 'period': 'last month'}),
            ('analyze_seasonal_patterns', {'season': 'festival period'}),
            ('analyze_capacity_impact', {'client_name': 'Client_Y', 'extra_orders': 20000})
        ]
        
        for use_case_name, args in use_cases:
            try:
                method = getattr(self.use_case_handler, use_case_name)
                result = method(**args)
                
                # Validate result structure
                validation = self.use_case_handler.validate_use_case_results(
                    use_case_name.replace('analyze_', '').replace('compare_', ''),
                    result
                )
                
                results['details'][use_case_name] = {
                    'success': result.get('success', False),
                    'validation_score': validation.get('score', 0),
                    'has_insights': len(result.get('insights', [])) > 0,
                    'has_recommendations': len(result.get('recommendations', [])) > 0
                }
                
                if not result.get('success') or validation.get('score', 0) < 75:
                    results['success'] = False
                
            except Exception as e:
                results['success'] = False
                results['details'][use_case_name] = {'error': str(e)}
        
        return results
    
    def test_sample_queries(self) -> Dict[str, Any]:
        """Test sample query generation and suggestions"""
        results = {'success': True, 'details': {}}
        
        try:
            # Test sample queries
            sample_queries = self.use_case_handler.get_sample_queries()
            
            results['details']['total_categories'] = len(sample_queries)
            results['details']['total_queries'] = sum(len(queries) for queries in sample_queries.values())
            
            # Test query suggestions
            test_inputs = ['delay', 'client', 'warehouse', 'compare', 'seasonal']
            suggestion_results = {}
            
            for test_input in test_inputs:
                suggestions = self.use_case_handler.get_query_suggestions(test_input)
                suggestion_results[test_input] = len(suggestions)
            
            results['details']['suggestion_tests'] = suggestion_results
            
            # Validate minimum requirements
            if results['details']['total_categories'] < 6:
                results['success'] = False
                results['error'] = "Insufficient query categories"
            
            if results['details']['total_queries'] < 30:
                results['success'] = False
                results['error'] = "Insufficient sample queries"
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def test_data_generation(self) -> Dict[str, Any]:
        """Test demo data generation"""
        results = {'success': True, 'details': {}}
        
        try:
            # Test basic data generation
            orders = self.data_generator.generate_orders(count=100, date_range_days=7)
            fleet_logs = self.data_generator.generate_fleet_logs(count=150, date_range_days=7)
            warehouse_logs = self.data_generator.generate_warehouse_logs(count=100, date_range_days=7)
            external_factors = self.data_generator.generate_external_factors(date_range_days=7)
            feedback = self.data_generator.generate_feedback_data(order_count=80)
            
            results['details']['orders_generated'] = len(orders)
            results['details']['fleet_logs_generated'] = len(fleet_logs)
            results['details']['warehouse_logs_generated'] = len(warehouse_logs)
            results['details']['external_factors_generated'] = len(external_factors)
            results['details']['feedback_generated'] = len(feedback)
            
            # Test scenario data generation
            scenario_data = self.data_generator.create_scenario_data('mumbai_delays')
            results['details']['scenario_collections'] = list(scenario_data.keys())
            
            # Validate data quality
            if len(orders) != 100:
                results['success'] = False
                results['error'] = "Orders generation count mismatch"
            
            # Check for required fields in orders
            if orders and not all(hasattr(order, 'order_id') for order in orders):
                results['success'] = False
                results['error'] = "Missing required fields in generated orders"
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def test_demo_script(self) -> Dict[str, Any]:
        """Test demo script functionality"""
        results = {'success': True, 'details': {}}
        
        try:
            demo_script = DemoScript(interactive=False, verbose=False)
            
            # Test scenario listing
            scenarios = demo_script.list_scenarios()
            results['details']['available_scenarios'] = len(scenarios)
            
            # Test single scenario (without full system initialization)
            if scenarios:
                scenario_name = scenarios[0]
                results['details']['test_scenario'] = scenario_name
                
                # Test scenario configuration
                scenario_config = next(
                    (s for s in demo_script.demo_scenarios if s['name'] == scenario_name), 
                    None
                )
                
                if scenario_config:
                    results['details']['scenario_has_query'] = bool(scenario_config.get('query'))
                    results['details']['scenario_has_method'] = bool(scenario_config.get('use_case_method'))
                    results['details']['scenario_has_args'] = bool(scenario_config.get('use_case_args'))
                else:
                    results['success'] = False
                    results['error'] = "Scenario configuration not found"
            
            # Validate minimum scenarios
            if len(scenarios) < 6:
                results['success'] = False
                results['error'] = "Insufficient demo scenarios"
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def test_performance_monitor(self) -> Dict[str, Any]:
        """Test performance monitoring functionality"""
        results = {'success': True, 'details': {}}
        
        try:
            # Test monitor initialization
            monitor = PerformanceMonitor()
            
            # Test query monitoring
            test_query = "Test query for monitoring"
            monitor.start_query(test_query)
            time.sleep(0.1)  # Simulate processing time
            monitor.end_query(True, 0.1, 5)
            
            # Test statistics
            session_stats = monitor.get_session_stats()
            performance_summary = monitor.get_performance_summary()
            real_time_stats = monitor.get_real_time_stats()
            
            results['details']['session_stats_keys'] = list(session_stats.keys())
            results['details']['performance_summary_keys'] = list(performance_summary.keys())
            results['details']['real_time_stats_keys'] = list(real_time_stats.keys())
            results['details']['total_queries_tracked'] = session_stats.get('total_queries', 0)
            
            # Test OpenAI usage tracking
            monitor.record_openai_usage(100, 0.01)
            updated_stats = monitor.get_session_stats()
            results['details']['openai_tracking_works'] = updated_stats.get('openai_tokens_used', 0) > 0
            
            # Validate essential functionality
            if session_stats.get('total_queries', 0) == 0:
                results['success'] = False
                results['error'] = "Query tracking not working"
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def test_cli_interface(self) -> Dict[str, Any]:
        """Test CLI interface components"""
        results = {'success': True, 'details': {}}
        
        try:
            # Test CLI initialization (without actually running it)
            from src.cli.main import AnalyticsCLI
            
            # Test command handling
            results['details']['cli_class_exists'] = True
            
            # Test sample queries integration
            sample_queries = self.use_case_handler.get_sample_queries()
            results['details']['has_sample_queries'] = len(sample_queries) > 0
            
            # Test use case handler integration
            results['details']['use_case_handler_available'] = True
            
        except ImportError as e:
            results['success'] = False
            results['error'] = f"CLI import error: {e}"
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def test_web_interface(self) -> Dict[str, Any]:
        """Test web interface components"""
        results = {'success': True, 'details': {}}
        
        try:
            # Test Flask app import
            from src.web.app import app
            
            results['details']['flask_app_exists'] = True
            
            # Test route registration
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            expected_routes = ['/', '/query', '/examples', '/history', '/stats', '/demo', '/about']
            
            results['details']['registered_routes'] = len(routes)
            results['details']['expected_routes_present'] = all(
                any(expected in route for route in routes) for expected in expected_routes
            )
            
            # Test template files exist
            template_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'templates')
            if os.path.exists(template_dir):
                templates = os.listdir(template_dir)
                results['details']['template_files'] = len(templates)
                results['details']['has_base_template'] = 'base.html' in templates
            else:
                results['success'] = False
                results['error'] = "Template directory not found"
            
        except ImportError as e:
            results['success'] = False
            results['error'] = f"Web interface import error: {e}"
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for test in self.results['tests'].values() if test['status'] == 'passed')
        failed_tests = sum(1 for test in self.results['tests'].values() if test['status'] == 'failed')
        error_tests = sum(1 for test in self.results['tests'].values() if test['status'] == 'error')
        
        total_duration = sum(test.get('duration', 0) for test in self.results['tests'].values())
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'overall_status': 'PASSED' if failed_tests == 0 and error_tests == 0 else 'FAILED'
        }
    
    def print_summary(self):
        """Print test summary"""
        summary = self.results['summary']
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Errors: {summary['error_tests']} 💥")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Overall Status: {summary['overall_status']}")
        
        if summary['overall_status'] == 'PASSED':
            print("\n🎉 ALL TESTS PASSED! Demo interface is ready for use.")
        else:
            print("\n⚠️ Some tests failed. Check the details above for issues to resolve.")
        
        # Print failed test details
        failed_tests = [name for name, result in self.results['tests'].items() 
                       if result['status'] in ['failed', 'error']]
        
        if failed_tests:
            print(f"\n❌ Failed Tests: {', '.join(failed_tests)}")
    
    def export_results(self, filepath: str):
        """Export validation results to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n📄 Results exported to {filepath}")
        except Exception as e:
            print(f"\n❌ Failed to export results: {e}")


def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate demo interface components')
    parser.add_argument('--export', type=str, help='Export results to JSON file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        validator = DemoValidator()
        results = validator.run_all_tests()
        validator.print_summary()
        
        if args.export:
            validator.export_results(args.export)
        
        # Exit with appropriate code
        overall_status = results['summary']['overall_status']
        sys.exit(0 if overall_status == 'PASSED' else 1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
