#!/usr/bin/env python3
"""
Test script for insight generation functionality
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from insights.processor import ResultProcessor
from insights.templates import InsightTemplates, Recommendation
from insights.visualizer import VisualizationDataPrep
from insights.recommender import RecommendationEngine
from insights.formatters import OutputFormatters

# Import narrator and reporter conditionally to handle OpenAI dependency
try:
    from insights.narrator import NarrativeGenerator
    NARRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"NarrativeGenerator not available: {e}")
    NARRATOR_AVAILABLE = False

try:
    from insights.reporter import ReportGenerator
    REPORTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ReportGenerator not available: {e}")
    REPORTER_AVAILABLE = False

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
    
    for i in range(500):
        # Create realistic sample data
        timestamp = base_time + timedelta(hours=i * 1.5)
        status = statuses[i % len(statuses)]
        
        record = {
            'order_id': f'ORD{1000 + i}',
            'timestamp': timestamp.isoformat(),
            'status': status,
            'city': cities[i % len(cities)],
            'amount': 1000 + (i * 50) % 5000,
            'processing_time_minutes': 15 + (i * 3) % 120,
            'client_id': f'CLIENT_{(i % 50) + 1}',
            'warehouse_id': f'WH_{(i % 10) + 1}',
            'driver_id': f'DRV_{(i % 25) + 1}'
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


def test_result_processor():
    """Test the ResultProcessor functionality"""
    logger.info("Testing ResultProcessor...")
    
    processor = ResultProcessor()
    sample_data = generate_sample_data()
    
    # Test statistical analysis
    stats = processor.calculate_statistics(sample_data, 'amount')
    if stats:
        logger.info(f"Statistics for 'amount': mean={stats.mean:.2f}, std_dev={stats.std_dev:.2f}")
    
    # Test pattern detection
    patterns = processor.detect_patterns(sample_data, 'status', 'amount')
    logger.info(f"Detected {patterns['total_groups']} status patterns")
    
    # Test anomaly detection
    anomalies = processor.detect_anomalies(sample_data, 'amount')
    logger.info(f"Detected {anomalies.total_anomalies} anomalies using {anomalies.threshold_method}")
    
    # Test trend analysis
    trends = processor.analyze_trends(sample_data, 'timestamp', 'amount')
    logger.info(f"Trend analysis: {trends.direction} trend with {trends.change_percentage:.1f}% change")
    
    # Test ranking
    rankings = processor.rank_items(sample_data, 'city', 'amount', limit=5)
    logger.info(f"Top 5 cities by amount: {[r['item'] for r in rankings]}")
    
    logger.info("✅ ResultProcessor tests completed")
    return processor, sample_data


def test_templates():
    """Test the InsightTemplates functionality"""
    logger.info("Testing InsightTemplates...")
    
    templates = InsightTemplates()
    
    # Sample analysis results
    analysis_results = {
        'total_delayed': 125,
        'avg_delay': 45.5,
        'delay_rate': 25.0,
        'top_delay_cause': 'traffic_congestion',
        'delay_causes': {
            'traffic_congestion': {'percentage': 40.0, 'avg_delay': 60.0, 'count': 50},
            'weather_delay': {'percentage': 30.0, 'avg_delay': 35.0, 'count': 37},
            'address_issues': {'percentage': 20.0, 'avg_delay': 25.0, 'count': 25}
        },
        'trend_analysis': {
            'direction': 'increasing',
            'change_percentage': 15.5,
            'confidence': 0.85
        }
    }
    
    # Sample recommendations
    recommendations = [
        Recommendation(
            category="operational",
            action="Implement dynamic routing based on real-time traffic",
            expected_impact="Reduce delays by 30-40%",
            implementation_effort="medium",
            timeline="2-3 weeks",
            priority="high"
        ),
        Recommendation(
            category="process",
            action="Improve address verification before dispatch",
            expected_impact="Reduce address-related failures by 80%",
            implementation_effort="low",
            timeline="1-2 weeks",
            priority="medium"
        )
    ]
    
    # Test delay analysis template
    delay_template = templates.delay_analysis_template(analysis_results, recommendations)
    logger.info(f"Delay analysis template created with {len(delay_template['key_findings'])} findings")
    
    # Test client analysis template
    client_results = {
        'client_name': 'ABC Corp',
        'success_rate': 87.5,
        'total_orders': 150,
        'failure_analysis': {
            'stockout': {'count': 12},
            'address_issues': {'count': 8},
            'weather_delays': {'count': 5}
        }
    }
    
    client_template = templates.client_analysis_template(client_results, recommendations)
    logger.info(f"Client analysis template created for {client_template['client_overview']}")
    
    logger.info("✅ InsightTemplates tests completed")
    return templates


def test_visualizer():
    """Test the VisualizationDataPrep functionality"""
    logger.info("Testing VisualizationDataPrep...")
    
    visualizer = VisualizationDataPrep()
    sample_data = generate_sample_data()
    
    # Test time series data preparation
    time_series = visualizer.prepare_time_series_data(
        sample_data, 'timestamp', 'amount', 'sum', 'daily'
    )
    logger.info(f"Time series data: {len(time_series['labels'])} data points")
    
    # Test pie chart data preparation
    pie_data = visualizer.prepare_pie_chart_data(sample_data, 'status')
    logger.info(f"Pie chart data: {len(pie_data['labels'])} categories")
    
    # Test bar chart data preparation
    bar_data = visualizer.prepare_bar_chart_data(
        sample_data, 'city', 'amount', 'sum', 'value', 5
    )
    logger.info(f"Bar chart data: {len(bar_data['labels'])} bars")
    
    # Test scatter plot data preparation
    scatter_data = visualizer.prepare_scatter_plot_data(
        sample_data, 'processing_time_minutes', 'amount'
    )
    logger.info(f"Scatter plot data: {len(scatter_data['points'])} points")
    
    logger.info("✅ VisualizationDataPrep tests completed")
    return visualizer


def test_recommender():
    """Test the RecommendationEngine functionality"""
    logger.info("Testing RecommendationEngine...")
    
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
    logger.info(f"Generated {len(operational_recs)} operational recommendations")
    
    # Test executive recommendations
    executive_recs = recommender.generate_executive_recommendations(sample_data, query_context)
    logger.info(f"Generated {len(executive_recs)} executive recommendations")
    
    # Test comparative recommendations
    comparison_analysis = {
        'performance_changes': {
            'success_rate': {'change_percentage': -15.5},
            'delay_rate': {'change_percentage': 25.0}
        },
        'better_areas': ['Mumbai', 'Delhi'],
        'worse_areas': ['Bangalore', 'Chennai']
    }
    
    comparative_recs = recommender.generate_comparative_recommendations(
        comparison_analysis, query_context
    )
    logger.info(f"Generated {len(comparative_recs)} comparative recommendations")
    
    logger.info("✅ RecommendationEngine tests completed")
    return recommender


def test_formatters():
    """Test the OutputFormatters functionality"""
    logger.info("Testing OutputFormatters...")
    
    formatters = OutputFormatters()
    
    # Sample report data
    sample_report = {
        'report_type': 'operational_report',
        'analysis_type': 'delay_analysis',
        'generated_at': datetime.now().isoformat(),
        'executive_summary': 'Analysis of 500 orders shows significant delay patterns requiring immediate attention.',
        'key_performance_indicators': {
            'total_orders': 500,
            'success_rate': 75.0,
            'average_delay_minutes': 45.5,
            'on_time_percentage': 68.2
        },
        'key_findings': [
            {
                'finding': 'Traffic congestion caused 40% of delays',
                'impact': 'Average delay: 60 minutes',
                'affected_orders': 50
            },
            {
                'finding': 'Weather delays increased by 25% this month',
                'impact': 'Average delay: 35 minutes',
                'affected_orders': 37
            }
        ],
        'recommendations': [
            {
                'category': 'operational',
                'action': 'Implement dynamic routing based on real-time traffic',
                'expected_impact': 'Reduce delays by 30-40%',
                'implementation_effort': 'medium',
                'timeline': '2-3 weeks',
                'priority': 'high'
            }
        ]
    }
    
    # Test all formatters
    for format_type in formatters.get_available_formats():
        try:
            formatted_output = formatters.format(sample_report, format_type)
            content_type = formatters.get_content_type(format_type)
            logger.info(f"✅ {format_type.upper()} format: {len(formatted_output)} characters, content-type: {content_type}")
            
            # Save sample outputs
            filename = f"sample_report.{format_type}"
            if format_type == 'html':
                filename = f"sample_report.html"
            elif format_type == 'text':
                filename = f"sample_report.txt"
            elif format_type == 'markdown':
                filename = f"sample_report.md"
            else:
                filename = f"sample_report.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            logger.info(f"Sample output saved to {filename}")
            
        except Exception as e:
            logger.error(f"❌ {format_type.upper()} format failed: {e}")
    
    logger.info("✅ OutputFormatters tests completed")
    return formatters


def test_full_integration():
    """Test full integration of all components"""
    logger.info("Testing full integration...")
    
    try:
        # Initialize all components
        processor = ResultProcessor()
        templates = InsightTemplates()
        recommender = RecommendationEngine()
        formatters = OutputFormatters()
        
        # Initialize optional components if available
        narrator = None
        if NARRATOR_AVAILABLE:
            try:
                narrator = NarrativeGenerator()
                logger.info("✅ NarrativeGenerator initialized")
            except Exception as e:
                logger.warning(f"NarrativeGenerator initialization failed: {e}")
        
        reporter = None
        if REPORTER_AVAILABLE:
            try:
                reporter = ReportGenerator()
                logger.info("✅ ReportGenerator initialized")
            except Exception as e:
                logger.warning(f"ReportGenerator initialization failed: {e}")
        
        # Generate sample data
        sample_data = generate_sample_data()
        
        # Process the data
        logger.info("Processing sample data...")
        
        # Calculate key metrics
        success_count = sum(1 for r in sample_data if r['status'] == 'completed')
        failure_count = sum(1 for r in sample_data if r['status'] in ['failed', 'cancelled'])
        delayed_count = sum(1 for r in sample_data if r['status'] == 'delayed')
        
        # Analyze patterns
        status_patterns = processor.detect_patterns(sample_data, 'status', 'amount')
        delay_stats = processor.calculate_statistics(
            [r for r in sample_data if 'delay_minutes' in r], 'delay_minutes'
        )
        
        # Create analysis results
        analysis_results = {
            'total_records': len(sample_data),
            'success_rate': (success_count / len(sample_data)) * 100,
            'failure_rate': (failure_count / len(sample_data)) * 100,
            'delay_rate': (delayed_count / len(sample_data)) * 100,
            'avg_delay': delay_stats.mean if delay_stats else 0,
            'status_patterns': status_patterns,
            'trend_analysis': {
                'direction': 'stable',
                'change_percentage': 2.5,
                'confidence': 0.75
            }
        }
        
        # Generate recommendations
        query_context = {'analysis_type': 'operational_efficiency'}
        recommendations = recommender.generate_operational_recommendations(
            sample_data, query_context, 'operational_efficiency'
        )
        
        # Create insight template
        insight_template = templates.operational_efficiency_template(
            analysis_results, recommendations
        )
        
        # Create comprehensive report
        report_data = {
            'report_type': 'comprehensive_analysis',
            'analysis_type': 'operational_efficiency',
            'generated_at': datetime.now().isoformat(),
            'executive_summary': f'Analysis of {len(sample_data)} operations reveals {analysis_results["success_rate"]:.1f}% success rate with key improvement opportunities identified.',
            'detailed_insights': insight_template,
            'key_performance_indicators': {
                'total_operations': analysis_results['total_records'],
                'success_rate': analysis_results['success_rate'],
                'failure_rate': analysis_results['failure_rate'],
                'delay_rate': analysis_results['delay_rate'],
                'average_delay_minutes': analysis_results['avg_delay']
            },
            'recommendations': [rec.__dict__ if hasattr(rec, '__dict__') else rec for rec in recommendations],
            'data_quality_score': 95.0,
            'confidence_level': 0.85
        }
        
        # Format the report in multiple formats
        logger.info("Generating formatted reports...")
        
        for format_type in ['json', 'markdown', 'html']:
            formatted_report = formatters.format(report_data, format_type)
            
            # Save the report
            filename = f"comprehensive_report.{format_type}"
            if format_type == 'html':
                filename = "comprehensive_report.html"
            elif format_type == 'markdown':
                filename = "comprehensive_report.md"
            else:
                filename = "comprehensive_report.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            
            logger.info(f"✅ Comprehensive report saved as {filename}")
        
        logger.info("✅ Full integration test completed successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("INSIGHT GENERATION TEST SUMMARY")
        print("="*60)
        print(f"Sample Data: {len(sample_data)} records processed")
        print(f"Success Rate: {analysis_results['success_rate']:.1f}%")
        print(f"Recommendations Generated: {len(recommendations)}")
        print(f"Output Formats: {len(formatters.get_available_formats())} formats supported")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Full integration test failed: {e}")
        return False


def main():
    """Main test function"""
    print("Starting Insight Generation Tests...")
    print("="*50)
    
    try:
        # Run individual component tests
        test_result_processor()
        print()
        
        test_templates()
        print()
        
        test_visualizer()
        print()
        
        test_recommender()
        print()
        
        test_formatters()
        print()
        
        # Run full integration test
        success = test_full_integration()
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("\nGenerated files:")
            print("- sample_report.json")
            print("- sample_report.md")
            print("- sample_report.html")
            print("- sample_report.txt")
            print("- comprehensive_report.json")
            print("- comprehensive_report.md")
            print("- comprehensive_report.html")
        else:
            print("\n❌ Some tests failed. Check the logs above.")
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n❌ Test execution failed: {e}")


if __name__ == "__main__":
    main()
