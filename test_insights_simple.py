#!/usr/bin/env python3
"""
Simple test script for insight generation functionality
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_sample_data() -> List[Dict[str, Any]]:
    """Generate sample data for testing"""
    sample_data = []
    
    # Generate sample delivery data
    statuses = ['completed', 'failed', 'delayed', 'cancelled']
    failure_reasons = ['traffic_congestion', 'address_issues', 'weather_delay', 'vehicle_breakdown', 'stock_unavailable']
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
    
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(100):  # Smaller dataset for simple test
        # Create realistic sample data
        timestamp = base_time + timedelta(hours=i * 6)
        status = statuses[i % len(statuses)]
        
        record = {
            'order_id': f'ORD{1000 + i}',
            'timestamp': timestamp.isoformat(),
            'status': status,
            'city': cities[i % len(cities)],
            'amount': 1000 + (i * 50) % 5000,
            'processing_time_minutes': 15 + (i * 3) % 120,
            'client_id': f'CLIENT_{(i % 10) + 1}',
            'warehouse_id': f'WH_{(i % 5) + 1}',
            'driver_id': f'DRV_{(i % 15) + 1}'
        }
        
        # Add delay information for delayed/failed orders
        if status in ['delayed', 'failed']:
            record['delay_minutes'] = 30 + (i * 5) % 180
            record['failure_reason'] = failure_reasons[i % len(failure_reasons)]
        
        # Add hour for pattern analysis
        record['hour'] = timestamp.hour
        
        sample_data.append(record)
    
    logger.info(f"Generated {len(sample_data)} sample records")
    return sample_data


def test_processor():
    """Test the ResultProcessor functionality"""
    logger.info("Testing ResultProcessor...")
    
    try:
        # Import directly to avoid package-level import issues
        import sys
        import importlib.util
        
        # Load processor module directly
        spec = importlib.util.spec_from_file_location(
            "processor", 
            os.path.join(os.path.dirname(__file__), 'src', 'insights', 'processor.py')
        )
        processor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(processor_module)
        ResultProcessor = processor_module.ResultProcessor
        
        processor = ResultProcessor()
        sample_data = generate_sample_data()
        
        # Test statistical analysis
        stats = processor.calculate_statistics(sample_data, 'amount')
        if stats:
            logger.info(f"✅ Statistics: mean={stats.mean:.2f}, std_dev={stats.std_dev:.2f}")
        
        # Test pattern detection
        patterns = processor.detect_patterns(sample_data, 'status', 'amount')
        logger.info(f"✅ Patterns: {patterns['total_groups']} status patterns detected")
        
        # Test anomaly detection
        anomalies = processor.detect_anomalies(sample_data, 'amount')
        logger.info(f"✅ Anomalies: {anomalies.total_anomalies} anomalies detected")
        
        # Test trend analysis
        trends = processor.analyze_trends(sample_data, 'timestamp', 'amount')
        logger.info(f"✅ Trends: {trends.direction} trend with {trends.change_percentage:.1f}% change")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ResultProcessor test failed: {e}")
        return False


def test_templates():
    """Test the InsightTemplates functionality"""
    logger.info("Testing InsightTemplates...")
    
    try:
        # Import directly to avoid package-level import issues
        import importlib.util
        
        # Load templates module directly
        spec = importlib.util.spec_from_file_location(
            "templates", 
            os.path.join(os.path.dirname(__file__), 'src', 'insights', 'templates.py')
        )
        templates_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(templates_module)
        InsightTemplates = templates_module.InsightTemplates
        Recommendation = templates_module.Recommendation
        
        templates = InsightTemplates()
        
        # Sample analysis results
        analysis_results = {
            'total_delayed': 25,
            'avg_delay': 45.5,
            'delay_rate': 25.0,
            'top_delay_cause': 'traffic_congestion'
        }
        
        # Sample recommendations
        recommendations = [
            Recommendation(
                category="operational",
                action="Implement dynamic routing",
                expected_impact="Reduce delays by 30%",
                implementation_effort="medium",
                timeline="2-3 weeks",
                priority="high"
            )
        ]
        
        # Test delay analysis template
        delay_template = templates.delay_analysis_template(analysis_results, recommendations)
        logger.info(f"✅ Delay template created with type: {delay_template['analysis_type']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ InsightTemplates test failed: {e}")
        return False


def test_visualizer():
    """Test the VisualizationDataPrep functionality"""
    logger.info("Testing VisualizationDataPrep...")
    
    try:
        # Import directly to avoid package-level import issues
        import importlib.util
        
        # Load visualizer module directly
        spec = importlib.util.spec_from_file_location(
            "visualizer", 
            os.path.join(os.path.dirname(__file__), 'src', 'insights', 'visualizer.py')
        )
        visualizer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(visualizer_module)
        VisualizationDataPrep = visualizer_module.VisualizationDataPrep
        
        visualizer = VisualizationDataPrep()
        sample_data = generate_sample_data()
        
        # Test time series data preparation
        time_series = visualizer.prepare_time_series_data(
            sample_data, 'timestamp', 'amount', 'sum', 'daily'
        )
        logger.info(f"✅ Time series: {len(time_series['labels'])} data points")
        
        # Test pie chart data preparation
        pie_data = visualizer.prepare_pie_chart_data(sample_data, 'status')
        logger.info(f"✅ Pie chart: {len(pie_data['labels'])} categories")
        
        # Test bar chart data preparation
        bar_data = visualizer.prepare_bar_chart_data(
            sample_data, 'city', 'amount', 'sum', 'value', 5
        )
        logger.info(f"✅ Bar chart: {len(bar_data['labels'])} bars")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ VisualizationDataPrep test failed: {e}")
        return False


def test_recommender():
    """Test the RecommendationEngine functionality"""
    logger.info("Testing RecommendationEngine...")
    
    try:
        # Import directly to avoid package-level import issues
        import importlib.util
        
        # Load templates module first for Recommendation class
        templates_spec = importlib.util.spec_from_file_location(
            "templates", 
            os.path.join(os.path.dirname(__file__), 'src', 'insights', 'templates.py')
        )
        templates_module = importlib.util.module_from_spec(templates_spec)
        templates_spec.loader.exec_module(templates_module)
        
        # Load recommender module directly
        spec = importlib.util.spec_from_file_location(
            "recommender", 
            os.path.join(os.path.dirname(__file__), 'src', 'insights', 'recommender.py')
        )
        recommender_module = importlib.util.module_from_spec(spec)
        
        # Inject the Recommendation class into the recommender module
        recommender_module.Recommendation = templates_module.Recommendation
        
        spec.loader.exec_module(recommender_module)
        RecommendationEngine = recommender_module.RecommendationEngine
        
        recommender = RecommendationEngine()
        sample_data = generate_sample_data()
        
        query_context = {
            'analysis_type': 'delay_analysis',
            'time_field': 'timestamp',
            'value_field': 'amount'
        }
        
        # Test operational recommendations
        operational_recs = recommender.generate_operational_recommendations(
            sample_data, query_context, 'delay_analysis'
        )
        logger.info(f"✅ Generated {len(operational_recs)} operational recommendations")
        
        # Test executive recommendations
        executive_recs = recommender.generate_executive_recommendations(sample_data, query_context)
        logger.info(f"✅ Generated {len(executive_recs)} executive recommendations")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RecommendationEngine test failed: {e}")
        return False


def test_formatters():
    """Test the OutputFormatters functionality"""
    logger.info("Testing OutputFormatters...")
    
    try:
        # Import directly to avoid package-level import issues
        import importlib.util
        
        # Load formatters module directly
        spec = importlib.util.spec_from_file_location(
            "formatters", 
            os.path.join(os.path.dirname(__file__), 'src', 'insights', 'formatters.py')
        )
        formatters_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(formatters_module)
        OutputFormatters = formatters_module.OutputFormatters
        
        formatters = OutputFormatters()
        
        # Sample report data
        sample_report = {
            'report_type': 'operational_report',
            'analysis_type': 'delay_analysis',
            'generated_at': datetime.now().isoformat(),
            'executive_summary': 'Analysis of 100 orders shows delay patterns requiring attention.',
            'key_performance_indicators': {
                'total_orders': 100,
                'success_rate': 75.0,
                'average_delay_minutes': 45.5
            },
            'recommendations': [
                {
                    'category': 'operational',
                    'action': 'Implement dynamic routing',
                    'expected_impact': 'Reduce delays by 30%',
                    'priority': 'high'
                }
            ]
        }
        
        # Test all formatters
        success_count = 0
        for format_type in formatters.get_available_formats():
            try:
                formatted_output = formatters.format(sample_report, format_type)
                content_type = formatters.get_content_type(format_type)
                logger.info(f"✅ {format_type.upper()}: {len(formatted_output)} chars, {content_type}")
                
                # Save sample output
                filename = f"test_output.{format_type}"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(formatted_output)
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ {format_type.upper()} format failed: {e}")
        
        return success_count == len(formatters.get_available_formats())
        
    except Exception as e:
        logger.error(f"❌ OutputFormatters test failed: {e}")
        return False


def main():
    """Main test function"""
    print("Starting Simple Insight Generation Tests...")
    print("="*50)
    
    test_results = []
    
    # Run individual component tests
    test_results.append(("ResultProcessor", test_processor()))
    test_results.append(("InsightTemplates", test_templates()))
    test_results.append(("VisualizationDataPrep", test_visualizer()))
    test_results.append(("RecommendationEngine", test_recommender()))
    test_results.append(("OutputFormatters", test_formatters()))
    
    # Print results
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"Tests Passed: {passed}/{len(test_results)}")
    
    if passed == len(test_results):
        print("\n🎉 All core insight generation components are working!")
        print("\nGenerated test files:")
        print("- test_output.json")
        print("- test_output.markdown")
        print("- test_output.html")
        print("- test_output.text")
    else:
        print(f"\n⚠️  {len(test_results) - passed} tests failed. Check logs above.")
    
    return passed == len(test_results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
