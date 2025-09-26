#!/usr/bin/env python3
"""
Test script for the data pipeline implementation
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.pipeline import DataPipeline
from config.database import DatabaseConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_pipeline_prerequisites():
    """Test pipeline prerequisites"""
    print("=" * 60)
    print("TESTING PIPELINE PREREQUISITES")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = DataPipeline(data_directory=".")
    
    # Validate prerequisites
    validation_results = pipeline.validate_pipeline_prerequisites()
    
    print(f"Prerequisites Valid: {validation_results['valid']}")
    print(f"Checks: {validation_results['checks']}")
    
    if validation_results['errors']:
        print("Errors found:")
        for error in validation_results['errors']:
            print(f"  - {error}")
    
    return validation_results['valid']


def test_csv_reading():
    """Test CSV reading functionality"""
    print("\n" + "=" * 60)
    print("TESTING CSV READING")
    print("=" * 60)
    
    from data.csv_reader import CSVReader
    
    csv_reader = CSVReader(data_directory=".")
    
    # Test reading individual files
    test_files = ['orders', 'warehouse_logs', 'fleet_logs', 'clients']
    
    for file_type in test_files:
        print(f"\nTesting {file_type}:")
        df = csv_reader.read_csv_file(file_type)
        if df is not None:
            print(f"  ✓ Successfully read {len(df)} rows")
            print(f"  ✓ Columns: {list(df.columns)}")
            
            # Validate data integrity
            is_valid, errors = csv_reader.validate_data_integrity(df, file_type)
            print(f"  ✓ Data integrity: {'Valid' if is_valid else 'Issues found'}")
            if errors:
                for error in errors[:3]:  # Show first 3 errors
                    print(f"    - {error}")
        else:
            print(f"  ✗ Failed to read {file_type}")
    
    # Test reading all files
    print(f"\nTesting read_all_csv_files:")
    all_dataframes = csv_reader.read_all_csv_files()
    print(f"  ✓ Successfully read {len(all_dataframes)} files")
    
    total_rows = sum(len(df) for df in all_dataframes.values())
    print(f"  ✓ Total rows across all files: {total_rows}")
    
    return len(all_dataframes) > 0


def test_data_transformation():
    """Test data transformation functionality"""
    print("\n" + "=" * 60)
    print("TESTING DATA TRANSFORMATION")
    print("=" * 60)
    
    from data.csv_reader import CSVReader
    from data.transformer import DataTransformer
    
    # Read sample data
    csv_reader = CSVReader(data_directory=".")
    dataframes = csv_reader.read_all_csv_files()
    
    if not dataframes:
        print("  ✗ No dataframes to transform")
        return False
    
    # Initialize transformer
    transformer = DataTransformer()
    
    # Test transformation of each collection
    for collection_type, df in dataframes.items():
        if df.empty:
            continue
            
        print(f"\nTesting transformation of {collection_type}:")
        documents = transformer.transform_dataframe(df, collection_type)
        
        if documents:
            print(f"  ✓ Transformed {len(documents)} documents")
            
            # Show sample document structure
            if documents:
                sample_doc = documents[0]
                print(f"  ✓ Sample document keys: {list(sample_doc.keys())}")
        else:
            print(f"  ✗ Failed to transform {collection_type}")
    
    # Test transform_all_data
    print(f"\nTesting transform_all_data:")
    all_transformed = transformer.transform_all_data(dataframes)
    total_docs = sum(len(docs) for docs in all_transformed.values())
    print(f"  ✓ Transformed {len(all_transformed)} collections with {total_docs} total documents")
    
    return len(all_transformed) > 0


def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    from data.loader import MongoDBLoader
    
    loader = MongoDBLoader()
    
    # Test connection
    connected = loader.connect()
    print(f"Database connection: {'✓ Success' if connected else '✗ Failed'}")
    
    if connected:
        # Test getting collection stats
        stats = loader.get_collection_stats()
        print(f"Collection stats retrieved: {'✓ Success' if stats else '✗ Failed'}")
        
        if stats and not stats.get('error'):
            print("Current collection document counts:")
            for collection, stat in stats.items():
                if isinstance(stat, dict) and 'document_count' in stat:
                    print(f"  - {collection}: {stat['document_count']} documents")
    
    return connected


def test_small_pipeline_run():
    """Test running pipeline with a small subset of data"""
    print("\n" + "=" * 60)
    print("TESTING SMALL PIPELINE RUN")
    print("=" * 60)
    
    from data.csv_reader import CSVReader
    from data.transformer import DataTransformer
    from data.loader import MongoDBLoader
    
    try:
        # Read small sample of data
        csv_reader = CSVReader(data_directory=".")
        
        # Read just orders for testing
        orders_df = csv_reader.read_csv_file('orders')
        if orders_df is None or orders_df.empty:
            print("  ✗ No orders data available for testing")
            return False
        
        # Take small sample
        sample_size = min(100, len(orders_df))
        orders_sample = orders_df.head(sample_size)
        print(f"  ✓ Using sample of {len(orders_sample)} orders")
        
        # Transform sample data
        transformer = DataTransformer()
        sample_documents = transformer.transform_dataframe(orders_sample, 'orders')
        print(f"  ✓ Transformed {len(sample_documents)} documents")
        
        # Load to database
        loader = MongoDBLoader()
        if not loader.connect():
            print("  ✗ Failed to connect to database")
            return False
        
        # Create a test collection
        test_collection = 'test_orders'
        inserted, updated, errors = loader.load_documents(test_collection, sample_documents)
        
        print(f"  ✓ Loaded documents: {inserted} inserted, {updated} updated")
        if errors:
            print(f"  ! Errors encountered: {len(errors)}")
            for error in errors[:3]:
                print(f"    - {error}")
        
        # Clean up test collection
        if loader.database is not None:
            loader.database.drop_collection(test_collection)
            print(f"  ✓ Cleaned up test collection")
        
        return inserted > 0 or updated > 0
        
    except Exception as e:
        print(f"  ✗ Pipeline test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("DATA PIPELINE TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    
    # Run tests
    test_results['prerequisites'] = test_pipeline_prerequisites()
    test_results['csv_reading'] = test_csv_reading()
    test_results['transformation'] = test_data_transformation()
    test_results['database'] = test_database_connection()
    test_results['small_pipeline'] = test_small_pipeline_run()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name.upper():20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Pipeline is ready for full execution.")
        
        # Ask if user wants to run full pipeline
        response = input("\nWould you like to run the full pipeline now? (y/N): ")
        if response.lower() in ['y', 'yes']:
            run_full_pipeline()
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues before running full pipeline.")


def run_full_pipeline():
    """Run the complete data pipeline"""
    print("\n" + "=" * 80)
    print("RUNNING FULL DATA PIPELINE")
    print("=" * 80)
    
    pipeline = DataPipeline(data_directory=".")
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(upsert=True, create_correlations=True)
    
    if results['success']:
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"Total processing time: {results['pipeline_state']['total_processing_time']:.2f} seconds")
        print(f"Stages completed: {results['pipeline_state']['stages_completed']}")
        
        # Show final statistics
        if 'final_statistics' in results:
            stats = results['final_statistics']
            print(f"\nFinal Statistics:")
            print(f"  - Overall quality score: {stats.get('data_quality', {}).get('overall_quality_score', 0):.1f}%")
            print(f"  - Collections loaded: {len(stats.get('collection_statistics', {}))}")
            print(f"  - Correlations created: {stats.get('correlation_summary', {}).get('status', 'unknown')}")
    else:
        print("\n❌ PIPELINE FAILED!")
        print(f"Error: {results['error']}")
        if results['pipeline_state']['errors']:
            print("Additional errors:")
            for error in results['pipeline_state']['errors']:
                print(f"  - {error}")


if __name__ == "__main__":
    main()
