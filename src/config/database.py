"""
Database configuration and connection management for MongoDB
"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """MongoDB database configuration and connection manager"""
    
    def __init__(self):
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'logistics_analytics')
        self.client = None
        self.database = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second connection timeout
                socketTimeoutMS=20000,   # 20 second socket timeout
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def get_database(self):
        """Get the database instance"""
        if self.database is None:
            if not self.connect():
                raise ConnectionError("Could not establish database connection")
        return self.database
    
    def get_collection(self, collection_name):
        """Get a specific collection from the database"""
        db = self.get_database()
        return db[collection_name]
    
    def close_connection(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    def create_collections(self):
        """Create all required collections with indexes"""
        try:
            db = self.get_database()
            
            # Define collections as per requirements
            collections = [
                'orders',
                'warehouse_logs', 
                'fleet_logs',
                'external_factors',
                'feedback',
                'clients',
                'warehouses',
                'drivers'
            ]
            
            # Create collections if they don't exist
            existing_collections = db.list_collection_names()
            
            for collection_name in collections:
                if collection_name not in existing_collections:
                    db.create_collection(collection_name)
                    logger.info(f"Created collection: {collection_name}")
                else:
                    logger.info(f"Collection already exists: {collection_name}")
            
            # Create indexes for better performance
            self._create_indexes(db)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
            return False
    
    def _create_indexes(self, db):
        """Create indexes for better query performance"""
        try:
            # Orders collection indexes
            db.orders.create_index("order_id")
            db.orders.create_index("client_id")
            db.orders.create_index("order_date")
            db.orders.create_index("status")
            
            # Warehouse logs indexes
            db.warehouse_logs.create_index("warehouse_id")
            db.warehouse_logs.create_index("timestamp")
            db.warehouse_logs.create_index("order_id")
            
            # Fleet logs indexes
            db.fleet_logs.create_index("driver_id")
            db.fleet_logs.create_index("order_id")
            db.fleet_logs.create_index("timestamp")
            
            # External factors indexes
            db.external_factors.create_index("date")
            db.external_factors.create_index("location")
            
            # Feedback indexes
            db.feedback.create_index("order_id")
            db.feedback.create_index("client_id")
            db.feedback.create_index("feedback_date")
            
            # Master data indexes
            db.clients.create_index("client_id")
            db.warehouses.create_index("warehouse_id")
            db.drivers.create_index("driver_id")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")


# Global database instance
db_config = DatabaseConfig()


def get_db():
    """Get database instance - convenience function"""
    return db_config.get_database()


def get_collection(collection_name):
    """Get collection instance - convenience function"""
    return db_config.get_collection(collection_name)