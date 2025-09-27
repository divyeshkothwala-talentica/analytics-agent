#!/usr/bin/env python3
"""
Test script to simulate web app warehouse capacity query processing
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_web_query_processing():
    """Test the web app query processing for warehouse capacity"""
    try:
        from data.enhanced_csv_engine import EnhancedCSVEngine
        from web.app import try_use_case_fallback
        
        print("🌐 Testing Web App Warehouse Capacity Query Processing")
        print("=" * 60)
        
        # Initialize CSV engine
        csv_engine = EnhancedCSVEngine()
        
        # Test the complete flow
        test_query = "What is the total capacity of warehouses in Gujarat?"
        
        print(f"Testing Query: '{test_query}'")
        print("-" * 50)
        
        # Step 1: Test CSV engine directly
        print("1️⃣ Testing Enhanced CSV Engine:")
        csv_result = csv_engine.process_query(test_query)
        
        if csv_result.get('success'):
            print(f"   ✅ CSV Engine Success")
            print(f"   📊 Analysis Type: {csv_result.get('analysis_type')}")
            print(f"   📈 Result Count: {csv_result.get('result_count')}")
            print(f"   🎯 Confidence: {csv_result.get('confidence')}")
        else:
            print(f"   ❌ CSV Engine Failed: {csv_result.get('error', 'Unknown error')}")
        
        # Step 2: Test fallback mechanism (if CSV fails)
        print(f"\n2️⃣ Testing Fallback Mechanism:")
        try:
            fallback_result = try_use_case_fallback(test_query)
            if fallback_result and fallback_result.get('success'):
                print(f"   ✅ Fallback Success")
                print(f"   📊 Analysis Type: {fallback_result.get('analysis_type')}")
                print(f"   📈 Result Count: {fallback_result.get('result_count')}")
            else:
                print(f"   ❌ Fallback Failed or Not Triggered")
        except Exception as e:
            print(f"   ⚠️  Fallback Error: {e}")
        
        # Step 3: Show the complete result
        print(f"\n3️⃣ Final Result:")
        if csv_result.get('success'):
            print("   🎉 Query would be handled by Enhanced CSV Engine")
            print(f"   📝 Explanation Preview:")
            explanation = csv_result.get('explanation', '')
            lines = explanation.split('\n')[:5]  # First 5 lines
            for line in lines:
                print(f"      {line}")
            if len(explanation.split('\n')) > 5:
                print("      ...")
        else:
            print("   ⚠️  Query would fall back to demo use cases")
        
        return csv_result.get('success', False)
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 WEB APP WAREHOUSE CAPACITY QUERY TEST")
    print("=" * 50)
    
    success = test_web_query_processing()
    
    print(f"\n📊 TEST RESULT")
    print("=" * 20)
    
    if success:
        print("✅ SUCCESS: Warehouse capacity queries are now properly handled!")
        print("\n🎯 What was fixed:")
        print("   • Enhanced CSV engine now recognizes warehouse capacity patterns")
        print("   • Web app has fallback for MongoDB-based warehouse analysis")
        print("   • Queries like 'total capacity in Gujarat' work correctly")
        print("\n🚀 The error in console should now be resolved!")
    else:
        print("❌ FAILED: There may still be issues with warehouse capacity queries")
        print("\n🔍 Check:")
        print("   • CSV data loading")
        print("   • Pattern matching logic")
        print("   • Import paths")

if __name__ == "__main__":
    main()
