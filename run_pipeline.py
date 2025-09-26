#!/usr/bin/env python3
"""
Script to run the full data pipeline
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.pipeline import DataPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run the complete data pipeline"""
    print("=" * 80)
    print("RUNNING FULL DATA PIPELINE")
    print("=" * 80)
    
    pipeline = DataPipeline(data_directory=".")
    
    # Validate prerequisites first
    print("Validating prerequisites...")
    validation_results = pipeline.validate_pipeline_prerequisites()
    if not validation_results['valid']:
        print("❌ Pipeline prerequisites validation failed:")
        for error in validation_results['errors']:
            print(f"  - {error}")
        return False
    
    print("✅ Prerequisites validation passed")
    
    # Run full pipeline
    print("\nStarting pipeline execution...")
    results = pipeline.run_full_pipeline(upsert=True, create_correlations=True)
    
    if results['success']:
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"Total processing time: {results['pipeline_state']['total_processing_time']:.2f} seconds")
        print(f"Stages completed: {results['pipeline_state']['stages_completed']}")
        
        # Show final statistics
        if 'final_statistics' in results:
            stats = results['final_statistics']
            print(f"\nFinal Statistics:")
            
            # Data loading statistics
            load_stats = results.get('load_results', {})
            total_inserted = sum(result.get("inserted_count", 0) for result in load_stats.values() if isinstance(result, dict))
            total_updated = sum(result.get("updated_count", 0) for result in load_stats.values() if isinstance(result, dict))
            
            print(f"  - Documents inserted: {total_inserted}")
            print(f"  - Documents updated: {total_updated}")
            print(f"  - Overall quality score: {stats.get('data_quality', {}).get('overall_quality_score', 0):.1f}%")
            print(f"  - Collections loaded: {len(stats.get('collection_statistics', {}))}")
            print(f"  - Correlations status: {stats.get('correlation_summary', {}).get('status', 'unknown')}")
            
            # Show collection statistics
            collection_stats = stats.get('collection_statistics', {})
            if collection_stats:
                print(f"\nCollection Document Counts:")
                for collection, stat in collection_stats.items():
                    if isinstance(stat, dict) and 'document_count' in stat:
                        print(f"  - {collection}: {stat['document_count']} documents")
        
        return True
    else:
        print("\n❌ PIPELINE FAILED!")
        print(f"Error: {results['error']}")
        if results['pipeline_state']['errors']:
            print("Additional errors:")
            for error in results['pipeline_state']['errors']:
                print(f"  - {error}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
