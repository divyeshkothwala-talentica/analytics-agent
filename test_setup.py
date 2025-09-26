#!/usr/bin/env python3
"""
Test script to verify environment setup and database connectivity
Run this script to ensure all components are properly configured
"""

import sys
import os
import traceback
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    try:
        import pymongo
        print("✅ pymongo imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pymongo: {e}")
        return False
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import openai: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pandas: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False
    
    try:
        import flask
        print("✅ flask imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import flask: {e}")
        return False
    
    return True


def test_environment_variables():
    """Test that environment variables are loaded correctly"""
    print("\n🔍 Testing environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_database = os.getenv('MONGODB_DATABASE')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    log_level = os.getenv('LOG_LEVEL')
    
    if mongodb_uri:
        print(f"✅ MONGODB_URI loaded: {mongodb_uri}")
    else:
        print("❌ MONGODB_URI not found in environment")
        return False
    
    if mongodb_database:
        print(f"✅ MONGODB_DATABASE loaded: {mongodb_database}")
    else:
        print("❌ MONGODB_DATABASE not found in environment")
        return False
    
    if openai_api_key and openai_api_key != 'your_openai_api_key_here':
        print("✅ OPENAI_API_KEY loaded (hidden for security)")
    else:
        print("⚠️  OPENAI_API_KEY not configured or using default placeholder")
    
    if log_level:
        print(f"✅ LOG_LEVEL loaded: {log_level}")
    else:
        print("⚠️  LOG_LEVEL not set, using default")
    
    return True


def test_logging():
    """Test logging configuration"""
    print("\n🔍 Testing logging configuration...")
    
    try:
        from src.utils.logger import setup_logging, get_logger
        
        # Setup logging
        setup_logging()
        logger = get_logger(__name__)
        
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        
        print("✅ Logging system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        traceback.print_exc()
        return False


def test_database_connection():
    """Test MongoDB database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from src.config.database import DatabaseConfig
        
        # Create database config instance
        db_config = DatabaseConfig()
        
        # Test connection
        if db_config.connect():
            print("✅ Successfully connected to MongoDB")
            
            # Test database operations
            db = db_config.get_database()
            
            # Test creating collections
            if db_config.create_collections():
                print("✅ Collections created/verified successfully")
            else:
                print("⚠️  Issue with collection creation")
            
            # List collections
            collections = db.list_collection_names()
            print(f"✅ Available collections: {collections}")
            
            # Close connection
            db_config.close_connection()
            return True
        else:
            print("❌ Failed to connect to MongoDB")
            print("💡 Make sure MongoDB is running locally or check your connection string")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False


def test_data_models():
    """Test data models and schemas"""
    print("\n🔍 Testing data models...")
    
    try:
        from src.models.schemas import (
            Order, WarehouseLog, FleetLog, ExternalFactor, 
            Feedback, Client, Warehouse, Driver, SchemaValidator
        )
        
        # Test creating a sample order
        sample_order = Order(
            order_id="ORD001",
            client_id="CLI001",
            warehouse_id="WH001",
            driver_id="DRV001",
            order_date=datetime.now(),
            delivery_date=None,
            status="pending",
            items=[{"product": "Widget", "quantity": 10}],
            total_amount=100.0,
            delivery_address="123 Main St",
            priority="medium",
            special_instructions=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Convert to dict
        order_dict = sample_order.to_dict()
        
        # Validate
        if SchemaValidator.validate_order(order_dict):
            print("✅ Order model and validation working correctly")
        else:
            print("❌ Order validation failed")
            return False
        
        print("✅ All data models imported and working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        traceback.print_exc()
        return False


def test_project_structure():
    """Test that project structure is correct"""
    print("\n🔍 Testing project structure...")
    
    required_dirs = [
        'src',
        'src/config',
        'src/models', 
        'src/utils',
        'data',
        'logs'
    ]
    
    required_files = [
        'requirements.txt',
        '.env',
        '.env.template',
        'src/__init__.py',
        'src/config/__init__.py',
        'src/config/database.py',
        'src/models/__init__.py',
        'src/models/schemas.py',
        'src/utils/__init__.py',
        'src/utils/logger.py'
    ]
    
    # Check directories
    for directory in required_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            return False
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            return False
    
    return True


def main():
    """Run all tests"""
    print("🚀 Starting Analytics Agent Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Logging System", test_logging),
        ("Data Models", test_data_models),
        ("Database Connection", test_database_connection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your environment is ready.")
        print("\n📝 Next steps:")
        print("1. Update .env file with your actual OpenAI API key")
        print("2. Ensure MongoDB is running (local or Atlas)")
        print("3. Run the data pipeline to load CSV data")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)