#!/usr/bin/env python3
"""
Warehouse Capacity Analysis Script
Analyzes warehouse data by city and state for comprehensive logistics insights
"""

import pandas as pd
import sys
import os
from typing import Dict, List, Any
from collections import defaultdict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_warehouse_data(csv_path: str = "warehouses.csv") -> pd.DataFrame:
    """Load warehouse data from CSV file"""
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} warehouses from {csv_path}")
        return df
    except Exception as e:
        print(f"❌ Error loading warehouse data: {e}")
        return pd.DataFrame()

def analyze_warehouse_capacity_by_state(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze warehouse capacity grouped by state"""
    if df.empty:
        return {}
    
    state_analysis = df.groupby('state').agg({
        'capacity': ['sum', 'mean', 'count', 'min', 'max'],
        'warehouse_id': 'count'
    }).round(2)
    
    # Flatten column names
    state_analysis.columns = ['total_capacity', 'avg_capacity', 'capacity_count', 
                             'min_capacity', 'max_capacity', 'warehouse_count']
    
    return state_analysis.to_dict('index')

def analyze_warehouse_capacity_by_city(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze warehouse capacity grouped by city"""
    if df.empty:
        return {}
    
    city_analysis = df.groupby(['state', 'city']).agg({
        'capacity': ['sum', 'mean', 'count', 'min', 'max'],
        'warehouse_id': 'count'
    }).round(2)
    
    # Flatten column names
    city_analysis.columns = ['total_capacity', 'avg_capacity', 'capacity_count', 
                            'min_capacity', 'max_capacity', 'warehouse_count']
    
    return city_analysis.to_dict('index')

def get_state_detailed_analysis(df: pd.DataFrame, state_name: str) -> Dict[str, Any]:
    """Get detailed analysis for warehouses in a specific state"""
    state_df = df[df['state'] == state_name].copy()
    
    if state_df.empty:
        return {"error": f"No warehouses found in {state_name}"}
    
    # Overall state statistics
    total_capacity = state_df['capacity'].sum()
    avg_capacity = state_df['capacity'].mean()
    warehouse_count = len(state_df)
    
    # City-wise breakdown in the state
    city_breakdown = state_df.groupby('city').agg({
        'capacity': ['sum', 'mean', 'count', 'min', 'max'],
        'warehouse_id': 'count'
    }).round(2)
    
    city_breakdown.columns = ['total_capacity', 'avg_capacity', 'capacity_count', 
                             'min_capacity', 'max_capacity', 'warehouse_count']
    
    # Individual warehouse details
    warehouse_details = state_df[['warehouse_id', 'warehouse_name', 'city', 
                                 'capacity', 'manager_name']].to_dict('records')
    
    return {
        "state": state_name,
        "total_capacity": int(total_capacity),
        "average_capacity": round(avg_capacity, 2),
        "warehouse_count": warehouse_count,
        "city_breakdown": city_breakdown.to_dict('index'),
        "warehouse_details": warehouse_details
    }

def generate_capacity_report(df: pd.DataFrame, focus_state: str = None) -> str:
    """Generate a comprehensive capacity analysis report"""
    if df.empty:
        return "❌ No warehouse data available for analysis"
    
    # Get analyses
    state_analysis = analyze_warehouse_capacity_by_state(df)
    city_analysis = analyze_warehouse_capacity_by_city(df)
    
    # Get detailed analysis for focus state if specified
    detailed_state_analysis = None
    if focus_state:
        detailed_state_analysis = get_state_detailed_analysis(df, focus_state)
    
    report = []
    report.append("=" * 80)
    report.append("🏭 WAREHOUSE CAPACITY ANALYSIS REPORT")
    report.append("=" * 80)
    
    # Overall summary
    total_warehouses = len(df)
    total_capacity = df['capacity'].sum()
    avg_capacity = df['capacity'].mean()
    
    report.append(f"\n📊 OVERALL SUMMARY")
    report.append(f"   Total Warehouses: {total_warehouses}")
    report.append(f"   Total Capacity: {total_capacity:,} units")
    report.append(f"   Average Capacity: {avg_capacity:.2f} units")
    
    # State-wise analysis
    report.append(f"\n🗺️  STATE-WISE CAPACITY ANALYSIS")
    report.append("-" * 50)
    
    # Sort states by total capacity
    sorted_states = sorted(state_analysis.items(), 
                          key=lambda x: x[1]['total_capacity'], reverse=True)
    
    for state, data in sorted_states:
        report.append(f"\n📍 {state}")
        report.append(f"   Total Capacity: {data['total_capacity']:,} units")
        report.append(f"   Warehouses: {data['warehouse_count']}")
        report.append(f"   Average Capacity: {data['avg_capacity']:.2f} units")
        report.append(f"   Range: {data['min_capacity']:.0f} - {data['max_capacity']:.0f} units")
    
    # Detailed state analysis if requested
    if detailed_state_analysis and 'error' not in detailed_state_analysis:
        state_name = detailed_state_analysis['state']
        report.append(f"\n🎯 {state_name.upper()} DETAILED ANALYSIS")
        report.append("=" * 50)
        report.append(f"Total Capacity in {state_name}: {detailed_state_analysis['total_capacity']:,} units")
        report.append(f"Number of Warehouses: {detailed_state_analysis['warehouse_count']}")
        report.append(f"Average Capacity: {detailed_state_analysis['average_capacity']:.2f} units")
        
        report.append(f"\n🏙️  City-wise Breakdown in {state_name}:")
        for city, data in detailed_state_analysis['city_breakdown'].items():
            report.append(f"   📍 {city}")
            report.append(f"      Total Capacity: {data['total_capacity']:,} units")
            report.append(f"      Warehouses: {data['warehouse_count']}")
            report.append(f"      Average: {data['avg_capacity']:.2f} units")
        
        report.append(f"\n📋 Individual Warehouses in {state_name}:")
        for warehouse in detailed_state_analysis['warehouse_details']:
            report.append(f"   • {warehouse['warehouse_name']} ({warehouse['city']})")
            report.append(f"     Capacity: {warehouse['capacity']:,} units | Manager: {warehouse['manager_name']}")
    
    # Top cities by capacity
    report.append(f"\n🏆 TOP CITIES BY TOTAL CAPACITY")
    report.append("-" * 40)
    
    # Sort cities by total capacity
    sorted_cities = sorted(city_analysis.items(), 
                          key=lambda x: x[1]['total_capacity'], reverse=True)
    
    for i, ((state, city), data) in enumerate(sorted_cities[:10], 1):
        report.append(f"{i:2d}. {city}, {state}: {data['total_capacity']:,} units ({data['warehouse_count']} warehouses)")
    
    return "\n".join(report)

def create_mongodb_query_for_state(state_name: str = None):
    """Generate MongoDB aggregation query for warehouse capacity analysis"""
    query = []
    
    # Add match stage if specific state is requested
    if state_name:
        query.append({
            "$match": {
                "state": state_name
            }
        })
    
    query.extend([
        {
            "$group": {
                "_id": {
                    "state": "$state",
                    "city": "$city"
                },
                "total_capacity": {"$sum": "$capacity"},
                "warehouse_count": {"$sum": 1},
                "avg_capacity": {"$avg": "$capacity"},
                "warehouses": {
                    "$push": {
                        "warehouse_id": "$warehouse_id",
                        "warehouse_name": "$warehouse_name",
                        "capacity": "$capacity",
                        "manager_name": "$manager_name"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$_id.state",
                "total_state_capacity": {"$sum": "$total_capacity"},
                "total_warehouses": {"$sum": "$warehouse_count"},
                "cities": {
                    "$push": {
                        "city": "$_id.city",
                        "total_capacity": "$total_capacity",
                        "warehouse_count": "$warehouse_count",
                        "avg_capacity": "$avg_capacity",
                        "warehouses": "$warehouses"
                    }
                }
            }
        },
        {
            "$project": {
                "state": "$_id",
                "total_capacity": "$total_state_capacity",
                "total_warehouses": "$total_warehouses",
                "average_capacity": {"$divide": ["$total_state_capacity", "$total_warehouses"]},
                "cities": 1,
                "_id": 0
            }
        }
    ])
    
    return query

def analyze_specific_state(df: pd.DataFrame, state_name: str):
    """Analyze capacity for a specific state and provide quick answer"""
    state_data = get_state_detailed_analysis(df, state_name)
    if 'error' not in state_data:
        print(f"\n🎯 QUICK ANSWER FOR {state_name.upper()}:")
        print(f"Total Warehouse Capacity in {state_name}: {state_data['total_capacity']:,} units")
        print(f"This is the sum of capacity from {state_data['warehouse_count']} warehouses across {len(state_data['city_breakdown'])} cities")
        
        print(f"\nCity breakdown in {state_name}:")
        for city, data in state_data['city_breakdown'].items():
            print(f"  • {city}: {data['total_capacity']:,} units ({data['warehouse_count']} warehouses)")
    else:
        print(f"❌ {state_data['error']}")

def main():
    """Main function to run warehouse capacity analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Warehouse Capacity Analysis')
    parser.add_argument('--state', '-s', type=str, help='Focus on specific state for detailed analysis')
    parser.add_argument('--city', '-c', type=str, help='Focus on specific city for analysis')
    parser.add_argument('--export', '-e', action='store_true', help='Export results to file')
    args = parser.parse_args()
    
    print("🏭 Starting Warehouse Capacity Analysis...")
    
    # Load data
    df = load_warehouse_data()
    if df.empty:
        print("❌ No data to analyze. Exiting.")
        return
    
    # Generate and display report
    report = generate_capacity_report(df, focus_state=args.state)
    print(report)
    
    # Export report if requested
    if args.export:
        filename = f"warehouse_capacity_analysis_report_{args.state or 'all'}.txt"
        with open(filename, "w") as f:
            f.write(report)
        print(f"\n💾 Report saved to: {filename}")
    
    # Generate MongoDB query
    mongodb_query = create_mongodb_query_for_state(args.state)
    print(f"\n🔍 MongoDB Query for {'All States' if not args.state else args.state} Analysis:")
    print("=" * 50)
    import json
    print(json.dumps(mongodb_query, indent=2))
    
    # Quick answer for specific state if requested
    if args.state:
        analyze_specific_state(df, args.state)
    
    # Show available states for reference
    available_states = df['state'].unique()
    print(f"\n📍 Available States: {', '.join(sorted(available_states))}")
    
    # Show example usage
    print(f"\n💡 Example Usage:")
    print(f"   python analyze_warehouse_capacity.py --state Gujarat")
    print(f"   python analyze_warehouse_capacity.py --state Maharashtra --export")
    print(f"   python analyze_warehouse_capacity.py  # For all states analysis")

if __name__ == "__main__":
    main()
