"""
Main Data Pipeline orchestrator for CSV to MongoDB ingestion
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.csv_reader import CSVReader
from data.transformer import DataTransformer
from data.loader import MongoDBLoader
from data.correlation_engine import CorrelationEngine
from config.database import DatabaseConfig

logger = logging.getLogger(__name__)


class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, data_directory: str = ".", db_config: Optional[DatabaseConfig] = None):
        self.data_directory = Path(data_directory)
        self.db_config = db_config or DatabaseConfig()
        
        # Initialize components
        self.csv_reader = CSVReader(data_directory)
        self.transformer = DataTransformer()
        self.loader = MongoDBLoader(self.db_config)
        self.correlation_engine = CorrelationEngine(self.db_config)
        
        # Pipeline state
        self.pipeline_state = {
            "start_time": None,
            "end_time": None,
            "total_processing_time": None,
            "stages_completed": [],
            "errors": [],
            "statistics": {}
        }
    
    def run_full_pipeline(self, upsert: bool = True, create_correlations: bool = True) -> Dict[str, Any]:
        """Run the complete data pipeline"""
        logger.info("Starting full data pipeline execution")
        self.pipeline_state["start_time"] = datetime.utcnow()
        
        try:
            # Stage 1: Read CSV files
            logger.info("Stage 1: Reading CSV files")
            dataframes = self._read_csv_files()
            if not dataframes:
                raise Exception("Failed to read CSV files")
            self.pipeline_state["stages_completed"].append("csv_reading")
            
            # Stage 2: Transform data
            logger.info("Stage 2: Transforming data")
            transformed_data = self._transform_data(dataframes)
            if not transformed_data:
                raise Exception("Failed to transform data")
            self.pipeline_state["stages_completed"].append("data_transformation")
            
            # Stage 3: Load data to MongoDB
            logger.info("Stage 3: Loading data to MongoDB")
            load_results = self._load_data(transformed_data, upsert)
            if not load_results:
                raise Exception("Failed to load data to MongoDB")
            self.pipeline_state["stages_completed"].append("data_loading")
            
            # Stage 4: Create correlations (optional)
            correlation_results = {}
            if create_correlations:
                logger.info("Stage 4: Creating data correlations")
                correlation_results = self._create_correlations()
                self.pipeline_state["stages_completed"].append("correlation_creation")
            
            # Stage 5: Generate final statistics
            logger.info("Stage 5: Generating pipeline statistics")
            final_stats = self._generate_pipeline_statistics(load_results, correlation_results)
            
            self.pipeline_state["end_time"] = datetime.utcnow()
            self.pipeline_state["total_processing_time"] = (
                self.pipeline_state["end_time"] - self.pipeline_state["start_time"]
            ).total_seconds()
            
            logger.info(f"Pipeline completed successfully in {self.pipeline_state['total_processing_time']} seconds")
            
            return {
                "success": True,
                "pipeline_state": self.pipeline_state,
                "load_results": load_results,
                "correlation_results": correlation_results,
                "final_statistics": final_stats
            }
            
        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            logger.error(error_msg)
            self.pipeline_state["errors"].append(error_msg)
            self.pipeline_state["end_time"] = datetime.utcnow()
            
            return {
                "success": False,
                "pipeline_state": self.pipeline_state,
                "error": error_msg
            }
    
    def _read_csv_files(self) -> Dict[str, Any]:
        """Read all CSV files"""
        try:
            dataframes = self.csv_reader.read_all_csv_files()
            
            # Log statistics
            stats = {}
            for file_type, df in dataframes.items():
                stats[file_type] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
                }
            
            self.pipeline_state["statistics"]["csv_reading"] = {
                "files_read": len(dataframes),
                "total_rows": sum(stats[ft]["rows"] for ft in stats),
                "file_statistics": stats
            }
            
            logger.info(f"Successfully read {len(dataframes)} CSV files with {self.pipeline_state['statistics']['csv_reading']['total_rows']} total rows")
            return dataframes
            
        except Exception as e:
            error_msg = f"Error reading CSV files: {e}"
            logger.error(error_msg)
            self.pipeline_state["errors"].append(error_msg)
            return {}
    
    def _transform_data(self, dataframes: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Transform all dataframes to MongoDB documents"""
        try:
            transformed_data = self.transformer.transform_all_data(dataframes)
            
            # Log statistics
            stats = {}
            for collection_type, documents in transformed_data.items():
                stats[collection_type] = {
                    "documents": len(documents),
                    "sample_document_keys": list(documents[0].keys()) if documents else []
                }
            
            self.pipeline_state["statistics"]["data_transformation"] = {
                "collections_transformed": len(transformed_data),
                "total_documents": sum(stats[ct]["documents"] for ct in stats),
                "collection_statistics": stats
            }
            
            logger.info(f"Successfully transformed data for {len(transformed_data)} collections with {self.pipeline_state['statistics']['data_transformation']['total_documents']} total documents")
            return transformed_data
            
        except Exception as e:
            error_msg = f"Error transforming data: {e}"
            logger.error(error_msg)
            self.pipeline_state["errors"].append(error_msg)
            return {}
    
    def _load_data(self, transformed_data: Dict[str, List[Dict[str, Any]]], upsert: bool = True) -> Dict[str, Any]:
        """Load transformed data to MongoDB"""
        try:
            load_results = self.loader.load_all_data(transformed_data, upsert)
            
            # Calculate statistics
            total_inserted = sum(result.get("inserted_count", 0) for result in load_results.values() if isinstance(result, dict))
            total_updated = sum(result.get("updated_count", 0) for result in load_results.values() if isinstance(result, dict))
            total_errors = sum(len(result.get("errors", [])) for result in load_results.values() if isinstance(result, dict))
            
            self.pipeline_state["statistics"]["data_loading"] = {
                "collections_loaded": len(load_results),
                "total_documents_inserted": total_inserted,
                "total_documents_updated": total_updated,
                "total_errors": total_errors,
                "load_results": load_results
            }
            
            logger.info(f"Successfully loaded data: {total_inserted} inserted, {total_updated} updated, {total_errors} errors")
            return load_results
            
        except Exception as e:
            error_msg = f"Error loading data: {e}"
            logger.error(error_msg)
            self.pipeline_state["errors"].append(error_msg)
            return {}
    
    def _create_correlations(self) -> Dict[str, Any]:
        """Create data correlations"""
        try:
            correlation_results = self.correlation_engine.run_full_correlation_analysis()
            
            self.pipeline_state["statistics"]["correlation_creation"] = {
                "correlations_created": True,
                "processing_time": correlation_results.get("total_processing_time", 0),
                "correlation_results": correlation_results
            }
            
            logger.info(f"Successfully created correlations in {correlation_results.get('total_processing_time', 0)} seconds")
            return correlation_results
            
        except Exception as e:
            error_msg = f"Error creating correlations: {e}"
            logger.error(error_msg)
            self.pipeline_state["errors"].append(error_msg)
            return {}
    
    def _generate_pipeline_statistics(self, load_results: Dict[str, Any], 
                                    correlation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive pipeline statistics"""
        try:
            # Get collection statistics from MongoDB
            collection_stats = self.loader.get_collection_stats()
            
            # Calculate data quality metrics
            quality_metrics = self._calculate_data_quality_metrics(load_results)
            
            # Performance metrics
            performance_metrics = {
                "total_processing_time_seconds": self.pipeline_state["total_processing_time"],
                "stages_completed": len(self.pipeline_state["stages_completed"]),
                "total_stages": 5,  # csv_reading, transformation, loading, correlation, statistics
                "success_rate": len(self.pipeline_state["stages_completed"]) / 5 * 100,
                "errors_encountered": len(self.pipeline_state["errors"])
            }
            
            final_stats = {
                "pipeline_execution": performance_metrics,
                "data_quality": quality_metrics,
                "collection_statistics": collection_stats,
                "correlation_summary": self._summarize_correlations(correlation_results),
                "generated_at": datetime.utcnow()
            }
            
            self.pipeline_state["statistics"]["final_statistics"] = final_stats
            
            return final_stats
            
        except Exception as e:
            error_msg = f"Error generating pipeline statistics: {e}"
            logger.error(error_msg)
            self.pipeline_state["errors"].append(error_msg)
            return {}
    
    def _calculate_data_quality_metrics(self, load_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        quality_metrics = {
            "overall_quality_score": 0,
            "collection_quality": {},
            "data_integrity_issues": []
        }
        
        total_collections = 0
        quality_sum = 0
        
        for collection_name, result in load_results.items():
            if isinstance(result, dict) and "validation" in result:
                validation = result["validation"]
                
                # Calculate quality score for this collection
                collection_quality = self._calculate_collection_quality_score(validation)
                quality_metrics["collection_quality"][collection_name] = collection_quality
                
                quality_sum += collection_quality["quality_score"]
                total_collections += 1
                
                # Collect data integrity issues
                if "checks" in validation and isinstance(validation["checks"], dict):
                    for check_name, check_result in validation["checks"].items():
                        if isinstance(check_result, int) and check_result > 0:
                            quality_metrics["data_integrity_issues"].append({
                                "collection": collection_name,
                                "issue": check_name,
                                "count": check_result
                            })
        
        # Calculate overall quality score
        if total_collections > 0:
            quality_metrics["overall_quality_score"] = quality_sum / total_collections
        
        return quality_metrics
    
    def _calculate_collection_quality_score(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality score for a single collection"""
        if "error" in validation:
            return {"quality_score": 0, "issues": ["Validation failed"]}
        
        total_documents = validation.get("total_documents", 0)
        if total_documents == 0:
            return {"quality_score": 0, "issues": ["No documents"]}
        
        quality_score = 100  # Start with perfect score
        issues = []
        
        checks = validation.get("checks", {})
        
        # Deduct points for various issues
        for check_name, check_result in checks.items():
            if isinstance(check_result, int) and check_result > 0:
                # Calculate percentage of issues
                issue_percentage = (check_result / total_documents) * 100
                
                if "null" in check_name.lower():
                    quality_score -= min(issue_percentage * 0.5, 20)  # Max 20 points deduction
                    issues.append(f"{check_name}: {check_result} ({issue_percentage:.1f}%)")
                elif "negative" in check_name.lower():
                    quality_score -= min(issue_percentage * 2, 30)  # Max 30 points deduction
                    issues.append(f"{check_name}: {check_result} ({issue_percentage:.1f}%)")
                elif "invalid" in check_name.lower():
                    quality_score -= min(issue_percentage * 1.5, 25)  # Max 25 points deduction
                    issues.append(f"{check_name}: {check_result} ({issue_percentage:.1f}%)")
        
        return {
            "quality_score": max(quality_score, 0),  # Don't go below 0
            "issues": issues
        }
    
    def _summarize_correlations(self, correlation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize correlation results"""
        if not correlation_results or "error" in correlation_results:
            return {"status": "failed", "reason": correlation_results.get("error", "Unknown error")}
        
        summary = {
            "status": "completed",
            "order_correlations": correlation_results.get("order_correlations", {}),
            "performance_metrics": correlation_results.get("performance_metrics", {}),
            "time_based_correlations": correlation_results.get("time_based_correlations", {}),
            "processing_time": correlation_results.get("total_processing_time", 0)
        }
        
        return summary
    
    def validate_pipeline_prerequisites(self) -> Dict[str, Any]:
        """Validate that all prerequisites are met before running pipeline"""
        validation_results = {
            "valid": True,
            "checks": {},
            "errors": []
        }
        
        # Check if data directory exists
        if not self.data_directory.exists():
            validation_results["valid"] = False
            validation_results["errors"].append(f"Data directory not found: {self.data_directory}")
        
        validation_results["checks"]["data_directory_exists"] = self.data_directory.exists()
        
        # Check if required CSV files exist
        required_files = ['orders.csv', 'warehouse_logs.csv', 'fleet_logs.csv', 'clients.csv', 
                         'drivers.csv', 'warehouses.csv', 'feedback.csv', 'external_factors.csv']
        
        missing_files = []
        for file_name in required_files:
            file_path = self.data_directory / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        validation_results["checks"]["required_files_exist"] = len(missing_files) == 0
        if missing_files:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Missing required files: {missing_files}")
        
        # Check database connectivity
        try:
            db_connected = self.db_config.connect()
            validation_results["checks"]["database_connection"] = db_connected
            if not db_connected:
                validation_results["valid"] = False
                validation_results["errors"].append("Cannot connect to MongoDB")
        except Exception as e:
            validation_results["checks"]["database_connection"] = False
            validation_results["valid"] = False
            validation_results["errors"].append(f"Database connection error: {e}")
        
        return validation_results
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "pipeline_state": self.pipeline_state,
            "components_initialized": {
                "csv_reader": self.csv_reader is not None,
                "transformer": self.transformer is not None,
                "loader": self.loader is not None,
                "correlation_engine": self.correlation_engine is not None
            }
        }


def main():
    """Main function to run the data pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the data pipeline")
    parser.add_argument("--data-dir", default=".", help="Directory containing CSV files")
    parser.add_argument("--no-correlations", action="store_true", help="Skip correlation creation")
    parser.add_argument("--no-upsert", action="store_true", help="Use insert instead of upsert")
    parser.add_argument("--validate-only", action="store_true", help="Only validate prerequisites")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize pipeline
    pipeline = DataPipeline(data_directory=args.data_dir)
    
    if args.validate_only:
        # Only validate prerequisites
        validation_results = pipeline.validate_pipeline_prerequisites()
        print("Pipeline Prerequisites Validation:")
        print(f"Valid: {validation_results['valid']}")
        if validation_results['errors']:
            print("Errors:")
            for error in validation_results['errors']:
                print(f"  - {error}")
        return
    
    # Validate prerequisites first
    validation_results = pipeline.validate_pipeline_prerequisites()
    if not validation_results['valid']:
        print("Pipeline prerequisites validation failed:")
        for error in validation_results['errors']:
            print(f"  - {error}")
        return
    
    # Run the pipeline
    results = pipeline.run_full_pipeline(
        upsert=not args.no_upsert,
        create_correlations=not args.no_correlations
    )
    
    if results['success']:
        print("Pipeline completed successfully!")
        print(f"Processing time: {results['pipeline_state']['total_processing_time']} seconds")
        print(f"Stages completed: {results['pipeline_state']['stages_completed']}")
    else:
        print("Pipeline failed!")
        print(f"Error: {results['error']}")
        if results['pipeline_state']['errors']:
            print("Additional errors:")
            for error in results['pipeline_state']['errors']:
                print(f"  - {error}")


if __name__ == "__main__":
    main()
