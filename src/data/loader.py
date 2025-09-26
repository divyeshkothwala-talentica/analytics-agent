"""
MongoDB Loader module for batch inserting documents with indexing
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError, DuplicateKeyError
from datetime import datetime
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import DatabaseConfig

logger = logging.getLogger(__name__)


class MongoDBLoader:
    """MongoDB loader with batch insert and indexing capabilities"""
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None):
        self.db_config = db_config or DatabaseConfig()
        self.database = None
        self.batch_size = 1000  # Default batch size for bulk operations
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            if self.db_config.connect():
                self.database = self.db_config.get_database()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def create_indexes(self) -> bool:
        """Create optimized indexes for all collections"""
        if self.database is None:
            logger.error("Database not connected")
            return False
        
        try:
            # Orders collection indexes
            orders_collection = self.database.orders
            orders_collection.create_index("order_id", unique=True)
            orders_collection.create_index("client_id")
            orders_collection.create_index("dates.order_date")
            orders_collection.create_index("dates.promised_delivery")
            orders_collection.create_index("dates.actual_delivery")
            orders_collection.create_index("status")
            orders_collection.create_index("customer_info.address.city")
            orders_collection.create_index("customer_info.address.state")
            orders_collection.create_index("failure_reason")
            orders_collection.create_index([("dates.order_date", DESCENDING)])
            
            # Warehouse logs collection indexes
            warehouse_logs_collection = self.database.warehouse_logs
            warehouse_logs_collection.create_index("log_id", unique=True)
            warehouse_logs_collection.create_index("order_id")
            warehouse_logs_collection.create_index("warehouse_id")
            warehouse_logs_collection.create_index("timing.picking_start")
            warehouse_logs_collection.create_index("timing.dispatch_time")
            warehouse_logs_collection.create_index("issues")
            warehouse_logs_collection.create_index([("warehouse_id", ASCENDING), ("timing.picking_start", DESCENDING)])
            
            # Fleet logs collection indexes
            fleet_logs_collection = self.database.fleet_logs
            fleet_logs_collection.create_index("fleet_log_id", unique=True)
            fleet_logs_collection.create_index("order_id")
            fleet_logs_collection.create_index("driver_id")
            fleet_logs_collection.create_index("timing.departure")
            fleet_logs_collection.create_index("timing.arrival")
            fleet_logs_collection.create_index("route_code")
            fleet_logs_collection.create_index("delay_reasons")
            fleet_logs_collection.create_index([("driver_id", ASCENDING), ("timing.departure", DESCENDING)])
            
            # External factors collection indexes
            external_factors_collection = self.database.external_factors
            external_factors_collection.create_index("factor_id", unique=True)
            external_factors_collection.create_index("order_id")
            external_factors_collection.create_index("recorded_at")
            external_factors_collection.create_index("conditions.traffic")
            external_factors_collection.create_index("conditions.weather")
            external_factors_collection.create_index("event_type")
            external_factors_collection.create_index("severity_score")
            
            # Feedback collection indexes
            feedback_collection = self.database.feedback
            feedback_collection.create_index("feedback_id", unique=True)
            feedback_collection.create_index("order_id")
            feedback_collection.create_index("sentiment")
            feedback_collection.create_index("rating")
            feedback_collection.create_index("keywords")
            feedback_collection.create_index([("rating", DESCENDING)])
            
            # Master data indexes
            clients_collection = self.database.clients
            clients_collection.create_index("client_id", unique=True)
            clients_collection.create_index("client_name")
            clients_collection.create_index("address.city")
            clients_collection.create_index("address.state")
            
            drivers_collection = self.database.drivers
            drivers_collection.create_index("driver_id", unique=True)
            drivers_collection.create_index("driver_name")
            drivers_collection.create_index("status")
            drivers_collection.create_index("location.city")
            drivers_collection.create_index("location.state")
            drivers_collection.create_index("partner_company")
            
            warehouses_collection = self.database.warehouses
            warehouses_collection.create_index("warehouse_id", unique=True)
            warehouses_collection.create_index("warehouse_name")
            warehouses_collection.create_index("location.city")
            warehouses_collection.create_index("location.state")
            
            logger.info("Successfully created all indexes")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def load_documents(self, collection_name: str, documents: List[Dict[str, Any]], 
                      upsert: bool = False) -> Tuple[int, int, List[str]]:
        """
        Load documents into MongoDB collection with batch processing
        
        Returns:
            Tuple of (inserted_count, updated_count, errors)
        """
        if self.database is None:
            logger.error("Database not connected")
            return 0, 0, ["Database not connected"]
        
        if not documents:
            logger.warning(f"No documents to load for {collection_name}")
            return 0, 0, []
        
        collection = self.database[collection_name]
        inserted_count = 0
        updated_count = 0
        errors = []
        
        # Process documents in batches
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            
            try:
                if upsert:
                    # Use upsert for handling duplicates
                    batch_inserted, batch_updated, batch_errors = self._upsert_batch(
                        collection, batch, collection_name
                    )
                    inserted_count += batch_inserted
                    updated_count += batch_updated
                    errors.extend(batch_errors)
                else:
                    # Simple insert
                    result = collection.insert_many(batch, ordered=False)
                    inserted_count += len(result.inserted_ids)
                    
            except BulkWriteError as e:
                # Handle bulk write errors
                inserted_count += e.details.get('nInserted', 0)
                for error in e.details.get('writeErrors', []):
                    errors.append(f"Error in batch {i//self.batch_size + 1}: {error['errmsg']}")
                    
            except Exception as e:
                error_msg = f"Error loading batch {i//self.batch_size + 1} for {collection_name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Loaded {inserted_count} documents into {collection_name}")
        if updated_count > 0:
            logger.info(f"Updated {updated_count} documents in {collection_name}")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors while loading {collection_name}")
        
        return inserted_count, updated_count, errors
    
    def _upsert_batch(self, collection, batch: List[Dict[str, Any]], 
                     collection_name: str) -> Tuple[int, int, List[str]]:
        """Perform upsert operation for a batch of documents"""
        inserted_count = 0
        updated_count = 0
        errors = []
        
        # Determine the unique key for each collection
        unique_keys = {
            'orders': 'order_id',
            'warehouse_logs': 'log_id',
            'fleet_logs': 'fleet_log_id',
            'external_factors': 'factor_id',
            'feedback': 'feedback_id',
            'clients': 'client_id',
            'drivers': 'driver_id',
            'warehouses': 'warehouse_id'
        }
        
        unique_key = unique_keys.get(collection_name)
        if not unique_key:
            # Fallback to insert_many if no unique key defined
            try:
                result = collection.insert_many(batch, ordered=False)
                return len(result.inserted_ids), 0, []
            except Exception as e:
                return 0, 0, [str(e)]
        
        # Perform individual upserts
        for doc in batch:
            try:
                if unique_key in doc and doc[unique_key] is not None:
                    filter_query = {unique_key: doc[unique_key]}
                    result = collection.replace_one(filter_query, doc, upsert=True)
                    
                    if result.upserted_id:
                        inserted_count += 1
                    elif result.modified_count > 0:
                        updated_count += 1
                else:
                    # If no unique key value, just insert
                    collection.insert_one(doc)
                    inserted_count += 1
                    
            except Exception as e:
                errors.append(f"Error upserting document with {unique_key}={doc.get(unique_key)}: {e}")
        
        return inserted_count, updated_count, errors
    
    def validate_data_integrity(self, collection_name: str) -> Dict[str, Any]:
        """Validate data integrity after loading"""
        if self.database is None:
            return {"error": "Database not connected"}
        
        collection = self.database[collection_name]
        
        try:
            # Basic statistics
            total_count = collection.count_documents({})
            
            validation_results = {
                "collection": collection_name,
                "total_documents": total_count,
                "validation_timestamp": datetime.utcnow(),
                "checks": {}
            }
            
            # Collection-specific validation
            if collection_name == 'orders':
                validation_results["checks"] = self._validate_orders_collection(collection)
            elif collection_name == 'warehouse_logs':
                validation_results["checks"] = self._validate_warehouse_logs_collection(collection)
            elif collection_name == 'fleet_logs':
                validation_results["checks"] = self._validate_fleet_logs_collection(collection)
            elif collection_name == 'feedback':
                validation_results["checks"] = self._validate_feedback_collection(collection)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating {collection_name}: {e}")
            return {"error": str(e)}
    
    def _validate_orders_collection(self, collection) -> Dict[str, Any]:
        """Validate orders collection"""
        checks = {}
        
        # Check for null order_ids
        null_order_ids = collection.count_documents({"order_id": None})
        checks["null_order_ids"] = null_order_ids
        
        # Check for null client_ids
        null_client_ids = collection.count_documents({"client_id": None})
        checks["null_client_ids"] = null_client_ids
        
        # Check date consistency
        invalid_dates = collection.count_documents({
            "$expr": {
                "$gt": ["$dates.order_date", "$dates.promised_delivery"]
            }
        })
        checks["invalid_date_sequences"] = invalid_dates
        
        # Status distribution
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_distribution = list(collection.aggregate(status_pipeline))
        checks["status_distribution"] = status_distribution
        
        return checks
    
    def _validate_warehouse_logs_collection(self, collection) -> Dict[str, Any]:
        """Validate warehouse logs collection"""
        checks = {}
        
        # Check for null processing times
        null_processing_times = collection.count_documents({"processing_time_minutes": None})
        checks["null_processing_times"] = null_processing_times
        
        # Check for negative processing times
        negative_processing_times = collection.count_documents({
            "processing_time_minutes": {"$lt": 0}
        })
        checks["negative_processing_times"] = negative_processing_times
        
        # Average processing time by warehouse
        avg_processing_pipeline = [
            {"$match": {"processing_time_minutes": {"$ne": None}}},
            {"$group": {
                "_id": "$warehouse_id",
                "avg_processing_time": {"$avg": "$processing_time_minutes"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"avg_processing_time": -1}}
        ]
        avg_processing_times = list(collection.aggregate(avg_processing_pipeline))
        checks["avg_processing_times_by_warehouse"] = avg_processing_times[:10]  # Top 10
        
        return checks
    
    def _validate_fleet_logs_collection(self, collection) -> Dict[str, Any]:
        """Validate fleet logs collection"""
        checks = {}
        
        # Check for null delivery times
        null_delivery_times = collection.count_documents({"delivery_time_hours": None})
        checks["null_delivery_times"] = null_delivery_times
        
        # Check for negative delivery times
        negative_delivery_times = collection.count_documents({
            "delivery_time_hours": {"$lt": 0}
        })
        checks["negative_delivery_times"] = negative_delivery_times
        
        # Delay reasons distribution
        delay_reasons_pipeline = [
            {"$unwind": "$delay_reasons"},
            {"$group": {"_id": "$delay_reasons", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        delay_reasons_distribution = list(collection.aggregate(delay_reasons_pipeline))
        checks["delay_reasons_distribution"] = delay_reasons_distribution
        
        return checks
    
    def _validate_feedback_collection(self, collection) -> Dict[str, Any]:
        """Validate feedback collection"""
        checks = {}
        
        # Rating distribution
        rating_pipeline = [
            {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        rating_distribution = list(collection.aggregate(rating_pipeline))
        checks["rating_distribution"] = rating_distribution
        
        # Sentiment distribution
        sentiment_pipeline = [
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sentiment_distribution = list(collection.aggregate(sentiment_pipeline))
        checks["sentiment_distribution"] = sentiment_distribution
        
        return checks
    
    def load_all_data(self, transformed_data: Dict[str, List[Dict[str, Any]]], 
                     upsert: bool = True) -> Dict[str, Dict[str, Any]]:
        """Load all transformed data into MongoDB"""
        if not self.connect():
            return {"error": "Failed to connect to database"}
        
        # Create indexes first
        if not self.create_indexes():
            logger.warning("Failed to create some indexes, continuing with data loading")
        
        results = {}
        
        for collection_name, documents in transformed_data.items():
            if documents:
                logger.info(f"Loading {len(documents)} documents into {collection_name}")
                inserted, updated, errors = self.load_documents(collection_name, documents, upsert)
                
                # Validate data integrity
                validation_results = self.validate_data_integrity(collection_name)
                
                results[collection_name] = {
                    "inserted_count": inserted,
                    "updated_count": updated,
                    "errors": errors,
                    "validation": validation_results
                }
            else:
                logger.warning(f"No documents to load for {collection_name}")
                results[collection_name] = {
                    "inserted_count": 0,
                    "updated_count": 0,
                    "errors": [],
                    "validation": {"message": "No documents to validate"}
                }
        
        return results
    
    def get_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all collections"""
        if self.database is None:
            return {"error": "Database not connected"}
        
        stats = {}
        collections = ['orders', 'warehouse_logs', 'fleet_logs', 'external_factors', 
                      'feedback', 'clients', 'drivers', 'warehouses']
        
        for collection_name in collections:
            try:
                collection = self.database[collection_name]
                count = collection.count_documents({})
                
                # Get sample document to understand structure
                sample = collection.find_one({})
                
                stats[collection_name] = {
                    "document_count": count,
                    "has_data": count > 0,
                    "sample_fields": list(sample.keys()) if sample else []
                }
                
            except Exception as e:
                stats[collection_name] = {"error": str(e)}
        
        return stats
    
    def close_connection(self):
        """Close database connection"""
        if self.db_config:
            self.db_config.close_connection()
