#!/usr/bin/env python3
"""
Test script for warehouse capacity natural language queries
Demonstrates integration with the Analytics Agent system
"""

import sys
import os
from typing import List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_warehouse_queries():
    """Test various warehouse capacity queries"""
    
    # Import after adding src to path
    try:
        from ai.warehouse_analyzer import WarehouseCapacityAnalyzer
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure MongoDB is running and data is loaded")
        return
    
    analyzer = WarehouseCapacityAnalyzer()
    
    # Test queries
    test_queries = [
        "What is the total capacity of warehouses in Gujarat?",
        "Total warehouse capacity in Maharashtra",
        "Show me warehouse capacity for Tamil Nadu",
        "What are the top cities by warehouse capacity?",
        "Give me a summary of all warehouse capacities by state",
        "Warehouse capacity in Ahmedabad",
        "Total capacity in Surat",
        "Show warehouse analysis for Karnataka"
    ]
    
    print("🏭 WAREHOUSE CAPACITY NATURAL LANGUAGE QUERY TESTING")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)
        
        try:
            # Analyze the query
            result = analyzer.analyze_warehouse_query(query)
            
            # Format and display result
            formatted_result = analyzer.format_analysis_result(result)
            print(formatted_result)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 DIRECT API EXAMPLES")
    print("=" * 70)
    
    # Direct API examples
    print("\n📍 Direct State Analysis (Gujarat):")
    try:
        gujarat_result = analyzer.get_state_capacity("Gujarat")
        if "error" not in gujarat_result:
            print(f"Total Capacity: {gujarat_result['total_capacity']:,} units")
            print(f"Warehouses: {gujarat_result['warehouse_count']}")
            print(f"Cities: {len(gujarat_result['city_breakdown'])}")
        else:
            print(f"Error: {gujarat_result['error']}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n🏆 Top 5 Cities by Capacity:")
    try:
        top_cities = analyzer.get_top_cities_by_capacity(5)
        if "error" not in top_cities:
            for i, city in enumerate(top_cities['top_cities'], 1):
                city_name = city['_id']['city']
                state_name = city['_id']['state']
                capacity = city['total_capacity']
                count = city['warehouse_count']
                print(f"{i}. {city_name}, {state_name}: {capacity:,} units ({count} warehouses)")
        else:
            print(f"Error: {top_cities['error']}")
    except Exception as e:
        print(f"Error: {e}")

def demonstrate_mongodb_integration():
    """Demonstrate MongoDB query generation"""
    print("\n" + "=" * 70)
    print("🔍 MONGODB QUERY EXAMPLES")
    print("=" * 70)
    
    # Example MongoDB queries for different scenarios
    queries = {
        "State Total Capacity": [
            {"$match": {"state": "Gujarat"}},
            {"$group": {
                "_id": "$state",
                "total_capacity": {"$sum": "$capacity"},
                "warehouse_count": {"$sum": 1},
                "avg_capacity": {"$avg": "$capacity"}
            }}
        ],
        
        "City-wise Breakdown": [
            {"$group": {
                "_id": {"state": "$state", "city": "$city"},
                "total_capacity": {"$sum": "$capacity"},
                "warehouse_count": {"$sum": 1}
            }},
            {"$sort": {"total_capacity": -1}}
        ],
        
        "Top Warehouses by Capacity": [
            {"$sort": {"capacity": -1}},
            {"$limit": 10},
            {"$project": {
                "warehouse_name": 1,
                "city": 1,
                "state": 1,
                "capacity": 1,
                "manager_name": 1
            }}
        ]
    }
    
    import json
    for query_name, pipeline in queries.items():
        print(f"\n📋 {query_name}:")
        print(json.dumps(pipeline, indent=2))

def main():
    """Main function"""
    print("🚀 Starting Warehouse Capacity Analysis Tests...")
    
    # Test natural language queries
    test_warehouse_queries()
    
    # Show MongoDB integration
    demonstrate_mongodb_integration()
    
    print(f"\n✅ Testing completed!")
    print(f"\n💡 Integration Points:")
    print(f"   • Natural language query processing")
    print(f"   • MongoDB aggregation pipelines")
    print(f"   • Formatted business-friendly outputs")
    print(f"   • State and city-level analysis")
    print(f"   • Capacity summaries and rankings")

if __name__ == "__main__":
    main()
