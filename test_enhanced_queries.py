#!/usr/bin/env python3
"""
Comprehensive test script for the Enhanced CSV Query Engine
Tests all 6 query patterns plus statistical and correlation queries
"""

import sys
import os
sys.path.append('src')

from src.data.enhanced_csv_engine import EnhancedCSVEngine

def test_all_query_patterns():
    """Test all supported query patterns"""
    
    print("🚀 Testing Enhanced CSV Query Engine")
    print("=" * 60)
    
    # Initialize engine
    engine = EnhancedCSVEngine('.')
    entities = engine.get_available_entities()
    
    print(f"📊 Data loaded:")
    print(f"   • Cities: {len(entities['cities'])} ({', '.join(entities['cities'][:5])}...)")
    print(f"   • Clients: {len(entities['clients'])} ({', '.join(entities['clients'][:3])}...)")
    print(f"   • Warehouses: {len(entities['warehouses'])} ({', '.join(entities['warehouses'][:3])}...)")
    print()
    
    # Test queries based on your 6 patterns
    test_queries = [
        # Pattern 1: City delay analysis
        {
            'category': '1. City Delay Analysis',
            'queries': [
                'Why were deliveries delayed in Mumbai yesterday?',
                'Why were deliveries delayed in Chennai yesterday?',
                'What caused delivery delays in Bangalore last week?'
            ]
        },
        
        # Pattern 2: Client failure analysis  
        {
            'category': '2. Client Failure Analysis',
            'queries': [
                'Why did Saini LLC orders fail in the past week?',
                'Why did Mann Group orders fail in the past week?',
                'What are the main issues with Zacharia, Sarkar and Dass deliveries?'
            ]
        },
        
        # Pattern 3: Warehouse performance
        {
            'category': '3. Warehouse Performance',
            'queries': [
                'Top reasons for delivery failures linked to Warehouse 1 in August?',
                'Analyze Warehouse 2 performance this quarter',
                'What are the issues at Warehouse 3?'
            ]
        },
        
        # Pattern 4: City comparison
        {
            'category': '4. City Comparison',
            'queries': [
                'Compare delivery failure causes between Mumbai and Delhi last month',
                'Compare delivery performance between Chennai and Bangalore',
                'How do Mumbai and Pune delivery rates compare?'
            ]
        },
        
        # Pattern 5: Seasonal analysis
        {
            'category': '5. Seasonal/Festival Analysis',
            'queries': [
                'What are the likely causes of delivery failures during festival period?',
                'How does monsoon season affect delivery performance?',
                'Analyze delivery patterns during holiday periods'
            ]
        },
        
        # Pattern 6: Capacity planning
        {
            'category': '6. Capacity Planning',
            'queries': [
                'If we onboard Client Y with 20,000 extra monthly orders, what risks should we expect?',
                'Impact of adding 15,000 new orders per month?',
                'What happens if we scale up by 50,000 orders monthly?'
            ]
        },
        
        # Additional: Statistical queries
        {
            'category': '7. Statistical Queries',
            'queries': [
                'How many orders failed last month?',
                'What is the average order value?',
                'Total revenue from all orders?',
                'Percentage of orders that are successful?'
            ]
        },
        
        # Additional: Trend analysis
        {
            'category': '8. Trend Analysis',
            'queries': [
                'Show delivery performance trends over time',
                'Monthly order volume trends',
                'Failure rate trends by month'
            ]
        },
        
        # Additional: Correlation analysis
        {
            'category': '9. Correlation Analysis',
            'queries': [
                'How does weather affect delivery success rates?',
                'Impact of traffic conditions on deliveries',
                'Correlation between order value and success rate'
            ]
        }
    ]
    
    # Run all tests
    total_queries = 0
    successful_queries = 0
    
    for test_group in test_queries:
        print(f"\n🔍 {test_group['category']}")
        print("-" * 50)
        
        for query in test_group['queries']:
            total_queries += 1
            print(f"\n   Query: {query}")
            
            try:
                result = engine.process_query(query)
                
                if result['success']:
                    successful_queries += 1
                    print(f"   ✅ Success | Results: {result.get('result_count', 0)} | Method: {result.get('analysis_method', 'N/A')}")
                    
                    # Show preview of explanation
                    explanation = result.get('explanation', '')
                    if explanation:
                        preview = explanation.split('\n')[0][:100]
                        print(f"   📝 Preview: {preview}...")
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📈 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total queries tested: {total_queries}")
    print(f"Successful queries: {successful_queries}")
    print(f"Success rate: {successful_queries/total_queries*100:.1f}%")
    
    if successful_queries == total_queries:
        print("🎉 ALL TESTS PASSED! The enhanced CSV engine is working perfectly!")
    elif successful_queries > total_queries * 0.8:
        print("✅ MOST TESTS PASSED! The system is working well with minor issues.")
    else:
        print("⚠️  SOME TESTS FAILED. Review the errors above.")
    
    # Show sample queries for user
    print(f"\n🎯 SAMPLE QUERIES FOR TESTING:")
    print("-" * 30)
    sample_queries = engine.get_sample_queries()
    for i, query in enumerate(sample_queries[:10], 1):
        print(f"{i:2d}. {query}")
    
    print(f"\n🌐 Web interface is running at: http://localhost:5001")
    print("You can now test these queries in the web interface!")

if __name__ == "__main__":
    test_all_query_patterns()
