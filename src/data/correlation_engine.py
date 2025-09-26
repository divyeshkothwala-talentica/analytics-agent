"""
Data Correlation Engine to link related data across collections
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pymongo import MongoClient
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import DatabaseConfig

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """Engine to create correlations and relationships between collections"""
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None):
        self.db_config = db_config or DatabaseConfig()
        self.database = None
        
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
    
    def create_order_correlations(self) -> Dict[str, Any]:
        """Create correlations for orders with warehouse and fleet logs"""
        if self.database is None:
            logger.error("Database not connected")
            return {"error": "Database not connected"}
        
        results = {
            "order_warehouse_correlations": 0,
            "order_fleet_correlations": 0,
            "order_feedback_correlations": 0,
            "order_external_factor_correlations": 0,
            "errors": []
        }
        
        try:
            orders_collection = self.database.orders
            
            # Get all orders
            orders = list(orders_collection.find({}))
            logger.info(f"Processing correlations for {len(orders)} orders")
            
            for order in orders:
                order_id = order.get('order_id')
                if not order_id:
                    continue
                
                # Find warehouse operations for this order
                warehouse_ops = self._find_warehouse_operations(order_id)
                if warehouse_ops:
                    # Update order with warehouse correlation
                    orders_collection.update_one(
                        {"order_id": order_id},
                        {"$set": {"warehouse_operations": warehouse_ops}}
                    )
                    results["order_warehouse_correlations"] += 1
                
                # Find fleet operations for this order
                fleet_ops = self._find_fleet_operations(order_id)
                if fleet_ops:
                    # Update order with fleet correlation
                    orders_collection.update_one(
                        {"order_id": order_id},
                        {"$set": {"fleet_operations": fleet_ops}}
                    )
                    results["order_fleet_correlations"] += 1
                
                # Find feedback for this order
                feedback_data = self._find_order_feedback(order_id)
                if feedback_data:
                    # Update order with feedback correlation
                    orders_collection.update_one(
                        {"order_id": order_id},
                        {"$set": {"customer_feedback": feedback_data}}
                    )
                    results["order_feedback_correlations"] += 1
                
                # Find external factors affecting this order
                external_factors = self._find_external_factors(order_id, order.get('dates', {}))
                if external_factors:
                    # Update order with external factors correlation
                    orders_collection.update_one(
                        {"order_id": order_id},
                        {"$set": {"external_factors": external_factors}}
                    )
                    results["order_external_factor_correlations"] += 1
            
            logger.info(f"Created correlations: {results}")
            return results
            
        except Exception as e:
            error_msg = f"Error creating order correlations: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results
    
    def _find_warehouse_operations(self, order_id: int) -> List[Dict[str, Any]]:
        """Find warehouse operations for an order"""
        try:
            warehouse_logs = self.database.warehouse_logs
            operations = list(warehouse_logs.find({"order_id": order_id}))
            
            # Enrich with warehouse details
            enriched_ops = []
            for op in operations:
                warehouse_id = op.get('warehouse_id')
                if warehouse_id:
                    warehouse_info = self.database.warehouses.find_one({"warehouse_id": warehouse_id})
                    if warehouse_info:
                        op['warehouse_info'] = {
                            "name": warehouse_info.get('warehouse_name'),
                            "location": warehouse_info.get('location')
                        }
                enriched_ops.append(op)
            
            return enriched_ops
            
        except Exception as e:
            logger.error(f"Error finding warehouse operations for order {order_id}: {e}")
            return []
    
    def _find_fleet_operations(self, order_id: int) -> List[Dict[str, Any]]:
        """Find fleet operations for an order"""
        try:
            fleet_logs = self.database.fleet_logs
            operations = list(fleet_logs.find({"order_id": order_id}))
            
            # Enrich with driver details
            enriched_ops = []
            for op in operations:
                driver_id = op.get('driver_id')
                if driver_id:
                    driver_info = self.database.drivers.find_one({"driver_id": driver_id})
                    if driver_info:
                        op['driver_info'] = {
                            "name": driver_info.get('driver_name'),
                            "partner_company": driver_info.get('partner_company'),
                            "location": driver_info.get('location')
                        }
                enriched_ops.append(op)
            
            return enriched_ops
            
        except Exception as e:
            logger.error(f"Error finding fleet operations for order {order_id}: {e}")
            return []
    
    def _find_order_feedback(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Find customer feedback for an order"""
        try:
            feedback_collection = self.database.feedback
            feedback = feedback_collection.find_one({"order_id": order_id})
            return feedback
            
        except Exception as e:
            logger.error(f"Error finding feedback for order {order_id}: {e}")
            return None
    
    def _find_external_factors(self, order_id: int, order_dates: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find external factors affecting an order based on timing"""
        try:
            external_factors_collection = self.database.external_factors
            
            # Direct order_id match
            direct_factors = list(external_factors_collection.find({"order_id": order_id}))
            
            # Time-based correlation for orders without direct external factor records
            time_based_factors = []
            if not direct_factors and order_dates.get('order_date'):
                order_date = order_dates['order_date']
                if isinstance(order_date, str):
                    from dateutil import parser
                    order_date = parser.parse(order_date)
                
                # Look for external factors within +/- 1 day of order date
                start_date = order_date - timedelta(days=1)
                end_date = order_date + timedelta(days=1)
                
                time_based_factors = list(external_factors_collection.find({
                    "recorded_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }))
            
            return direct_factors + time_based_factors
            
        except Exception as e:
            logger.error(f"Error finding external factors for order {order_id}: {e}")
            return []
    
    def create_performance_metrics(self) -> Dict[str, Any]:
        """Create performance metrics and correlations"""
        if self.database is None:
            logger.error("Database not connected")
            return {"error": "Database not connected"}
        
        results = {
            "warehouse_performance_metrics": 0,
            "driver_performance_metrics": 0,
            "route_performance_metrics": 0,
            "client_satisfaction_metrics": 0,
            "errors": []
        }
        
        try:
            # Create warehouse performance metrics
            warehouse_metrics = self._create_warehouse_performance_metrics()
            results["warehouse_performance_metrics"] = warehouse_metrics
            
            # Create driver performance metrics
            driver_metrics = self._create_driver_performance_metrics()
            results["driver_performance_metrics"] = driver_metrics
            
            # Create route performance metrics
            route_metrics = self._create_route_performance_metrics()
            results["route_performance_metrics"] = route_metrics
            
            # Create client satisfaction metrics
            client_metrics = self._create_client_satisfaction_metrics()
            results["client_satisfaction_metrics"] = client_metrics
            
            return results
            
        except Exception as e:
            error_msg = f"Error creating performance metrics: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results
    
    def _create_warehouse_performance_metrics(self) -> int:
        """Create warehouse performance metrics"""
        try:
            # Aggregate warehouse performance data
            pipeline = [
                {
                    "$group": {
                        "_id": "$warehouse_id",
                        "total_orders": {"$sum": 1},
                        "avg_processing_time": {"$avg": "$processing_time_minutes"},
                        "total_processing_time": {"$sum": "$processing_time_minutes"},
                        "issues_count": {"$sum": {"$size": "$issues"}}
                    }
                },
                {
                    "$lookup": {
                        "from": "warehouses",
                        "localField": "_id",
                        "foreignField": "warehouse_id",
                        "as": "warehouse_info"
                    }
                },
                {
                    "$unwind": "$warehouse_info"
                },
                {
                    "$addFields": {
                        "efficiency_score": {
                            "$divide": [
                                "$total_orders",
                                {"$add": ["$avg_processing_time", 1]}  # Avoid division by zero
                            ]
                        },
                        "issue_rate": {
                            "$divide": ["$issues_count", "$total_orders"]
                        }
                    }
                }
            ]
            
            warehouse_metrics = list(self.database.warehouse_logs.aggregate(pipeline))
            
            # Store metrics in a separate collection
            if warehouse_metrics:
                metrics_collection = self.database.warehouse_performance_metrics
                metrics_collection.delete_many({})  # Clear existing metrics
                
                for metric in warehouse_metrics:
                    metric["calculated_at"] = datetime.utcnow()
                
                metrics_collection.insert_many(warehouse_metrics)
                logger.info(f"Created warehouse performance metrics for {len(warehouse_metrics)} warehouses")
            
            return len(warehouse_metrics)
            
        except Exception as e:
            logger.error(f"Error creating warehouse performance metrics: {e}")
            return 0
    
    def _create_driver_performance_metrics(self) -> int:
        """Create driver performance metrics"""
        try:
            # Aggregate driver performance data
            pipeline = [
                {
                    "$group": {
                        "_id": "$driver_id",
                        "total_deliveries": {"$sum": 1},
                        "avg_delivery_time": {"$avg": "$delivery_time_hours"},
                        "total_delays": {"$sum": {"$size": "$delay_reasons"}},
                        "routes_covered": {"$addToSet": "$route_code"}
                    }
                },
                {
                    "$lookup": {
                        "from": "drivers",
                        "localField": "_id",
                        "foreignField": "driver_id",
                        "as": "driver_info"
                    }
                },
                {
                    "$unwind": "$driver_info"
                },
                {
                    "$addFields": {
                        "performance_score": {
                            "$divide": [
                                "$total_deliveries",
                                {"$add": ["$avg_delivery_time", 1]}  # Avoid division by zero
                            ]
                        },
                        "delay_rate": {
                            "$divide": ["$total_delays", "$total_deliveries"]
                        },
                        "route_diversity": {"$size": "$routes_covered"}
                    }
                }
            ]
            
            driver_metrics = list(self.database.fleet_logs.aggregate(pipeline))
            
            # Store metrics in a separate collection
            if driver_metrics:
                metrics_collection = self.database.driver_performance_metrics
                metrics_collection.delete_many({})  # Clear existing metrics
                
                for metric in driver_metrics:
                    metric["calculated_at"] = datetime.utcnow()
                
                metrics_collection.insert_many(driver_metrics)
                logger.info(f"Created driver performance metrics for {len(driver_metrics)} drivers")
            
            return len(driver_metrics)
            
        except Exception as e:
            logger.error(f"Error creating driver performance metrics: {e}")
            return 0
    
    def _create_route_performance_metrics(self) -> int:
        """Create route performance metrics"""
        try:
            # Aggregate route performance data
            pipeline = [
                {
                    "$group": {
                        "_id": "$route_code",
                        "total_trips": {"$sum": 1},
                        "avg_delivery_time": {"$avg": "$delivery_time_hours"},
                        "total_delays": {"$sum": {"$size": "$delay_reasons"}},
                        "unique_drivers": {"$addToSet": "$driver_id"}
                    }
                },
                {
                    "$addFields": {
                        "route_efficiency": {
                            "$divide": [
                                "$total_trips",
                                {"$add": ["$avg_delivery_time", 1]}
                            ]
                        },
                        "delay_frequency": {
                            "$divide": ["$total_delays", "$total_trips"]
                        },
                        "driver_count": {"$size": "$unique_drivers"}
                    }
                }
            ]
            
            route_metrics = list(self.database.fleet_logs.aggregate(pipeline))
            
            # Store metrics in a separate collection
            if route_metrics:
                metrics_collection = self.database.route_performance_metrics
                metrics_collection.delete_many({})  # Clear existing metrics
                
                for metric in route_metrics:
                    metric["calculated_at"] = datetime.utcnow()
                
                metrics_collection.insert_many(route_metrics)
                logger.info(f"Created route performance metrics for {len(route_metrics)} routes")
            
            return len(route_metrics)
            
        except Exception as e:
            logger.error(f"Error creating route performance metrics: {e}")
            return 0
    
    def _create_client_satisfaction_metrics(self) -> int:
        """Create client satisfaction metrics"""
        try:
            # Aggregate client satisfaction data
            pipeline = [
                {
                    "$lookup": {
                        "from": "orders",
                        "localField": "order_id",
                        "foreignField": "order_id",
                        "as": "order_info"
                    }
                },
                {
                    "$unwind": "$order_info"
                },
                {
                    "$group": {
                        "_id": "$order_info.client_id",
                        "total_feedback": {"$sum": 1},
                        "avg_rating": {"$avg": "$rating"},
                        "positive_feedback": {
                            "$sum": {"$cond": [{"$eq": ["$sentiment", "Positive"]}, 1, 0]}
                        },
                        "negative_feedback": {
                            "$sum": {"$cond": [{"$eq": ["$sentiment", "Negative"]}, 1, 0]}
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "clients",
                        "localField": "_id",
                        "foreignField": "client_id",
                        "as": "client_info"
                    }
                },
                {
                    "$unwind": "$client_info"
                },
                {
                    "$addFields": {
                        "satisfaction_score": {
                            "$multiply": ["$avg_rating", 20]  # Convert to 100-point scale
                        },
                        "positive_feedback_rate": {
                            "$divide": ["$positive_feedback", "$total_feedback"]
                        },
                        "negative_feedback_rate": {
                            "$divide": ["$negative_feedback", "$total_feedback"]
                        }
                    }
                }
            ]
            
            client_metrics = list(self.database.feedback.aggregate(pipeline))
            
            # Store metrics in a separate collection
            if client_metrics:
                metrics_collection = self.database.client_satisfaction_metrics
                metrics_collection.delete_many({})  # Clear existing metrics
                
                for metric in client_metrics:
                    metric["calculated_at"] = datetime.utcnow()
                
                metrics_collection.insert_many(client_metrics)
                logger.info(f"Created client satisfaction metrics for {len(client_metrics)} clients")
            
            return len(client_metrics)
            
        except Exception as e:
            logger.error(f"Error creating client satisfaction metrics: {e}")
            return 0
    
    def create_time_based_correlations(self) -> Dict[str, Any]:
        """Create time-based correlations for delay analysis"""
        if self.database is None:
            logger.error("Database not connected")
            return {"error": "Database not connected"}
        
        results = {
            "delay_pattern_analysis": 0,
            "seasonal_trend_analysis": 0,
            "peak_hour_analysis": 0,
            "errors": []
        }
        
        try:
            # Analyze delay patterns
            delay_patterns = self._analyze_delay_patterns()
            results["delay_pattern_analysis"] = delay_patterns
            
            # Analyze seasonal trends
            seasonal_trends = self._analyze_seasonal_trends()
            results["seasonal_trend_analysis"] = seasonal_trends
            
            # Analyze peak hour patterns
            peak_hours = self._analyze_peak_hour_patterns()
            results["peak_hour_analysis"] = peak_hours
            
            return results
            
        except Exception as e:
            error_msg = f"Error creating time-based correlations: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results
    
    def _analyze_delay_patterns(self) -> int:
        """Analyze delay patterns across different dimensions"""
        try:
            # Analyze delays by external factors
            pipeline = [
                {
                    "$lookup": {
                        "from": "external_factors",
                        "localField": "order_id",
                        "foreignField": "order_id",
                        "as": "external_factors"
                    }
                },
                {
                    "$match": {
                        "delivery_delay_hours": {"$exists": True, "$gt": 0}
                    }
                },
                {
                    "$unwind": {
                        "path": "$external_factors",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "weather": "$external_factors.conditions.weather",
                            "traffic": "$external_factors.conditions.traffic",
                            "event_type": "$external_factors.event_type"
                        },
                        "avg_delay_hours": {"$avg": "$delivery_delay_hours"},
                        "delay_count": {"$sum": 1},
                        "max_delay_hours": {"$max": "$delivery_delay_hours"}
                    }
                },
                {
                    "$sort": {"avg_delay_hours": -1}
                }
            ]
            
            delay_patterns = list(self.database.orders.aggregate(pipeline))
            
            # Store delay pattern analysis
            if delay_patterns:
                analysis_collection = self.database.delay_pattern_analysis
                analysis_collection.delete_many({})  # Clear existing analysis
                
                analysis_doc = {
                    "analysis_type": "delay_patterns",
                    "patterns": delay_patterns,
                    "calculated_at": datetime.utcnow()
                }
                
                analysis_collection.insert_one(analysis_doc)
                logger.info(f"Created delay pattern analysis with {len(delay_patterns)} patterns")
            
            return len(delay_patterns)
            
        except Exception as e:
            logger.error(f"Error analyzing delay patterns: {e}")
            return 0
    
    def _analyze_seasonal_trends(self) -> int:
        """Analyze seasonal trends in orders and delays"""
        try:
            # Analyze monthly trends
            pipeline = [
                {
                    "$addFields": {
                        "order_month": {"$month": "$dates.order_date"},
                        "order_year": {"$year": "$dates.order_date"}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": "$order_year",
                            "month": "$order_month"
                        },
                        "total_orders": {"$sum": 1},
                        "avg_delay_hours": {"$avg": "$delivery_delay_hours"},
                        "failed_orders": {
                            "$sum": {"$cond": [{"$eq": ["$status", "Failed"]}, 1, 0]}
                        },
                        "delivered_orders": {
                            "$sum": {"$cond": [{"$eq": ["$status", "Delivered"]}, 1, 0]}
                        }
                    }
                },
                {
                    "$addFields": {
                        "success_rate": {
                            "$divide": ["$delivered_orders", "$total_orders"]
                        },
                        "failure_rate": {
                            "$divide": ["$failed_orders", "$total_orders"]
                        }
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                }
            ]
            
            seasonal_trends = list(self.database.orders.aggregate(pipeline))
            
            # Store seasonal trend analysis
            if seasonal_trends:
                analysis_collection = self.database.seasonal_trend_analysis
                analysis_collection.delete_many({})  # Clear existing analysis
                
                analysis_doc = {
                    "analysis_type": "seasonal_trends",
                    "trends": seasonal_trends,
                    "calculated_at": datetime.utcnow()
                }
                
                analysis_collection.insert_one(analysis_doc)
                logger.info(f"Created seasonal trend analysis with {len(seasonal_trends)} data points")
            
            return len(seasonal_trends)
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal trends: {e}")
            return 0
    
    def _analyze_peak_hour_patterns(self) -> int:
        """Analyze peak hour patterns for orders and deliveries"""
        try:
            # Analyze hourly patterns
            pipeline = [
                {
                    "$addFields": {
                        "order_hour": {"$hour": "$dates.order_date"},
                        "order_day_of_week": {"$dayOfWeek": "$dates.order_date"}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "hour": "$order_hour",
                            "day_of_week": "$order_day_of_week"
                        },
                        "order_count": {"$sum": 1},
                        "avg_delay_hours": {"$avg": "$delivery_delay_hours"},
                        "success_rate": {
                            "$avg": {"$cond": [{"$eq": ["$status", "Delivered"]}, 1, 0]}
                        }
                    }
                },
                {
                    "$sort": {"_id.day_of_week": 1, "_id.hour": 1}
                }
            ]
            
            peak_hour_patterns = list(self.database.orders.aggregate(pipeline))
            
            # Store peak hour analysis
            if peak_hour_patterns:
                analysis_collection = self.database.peak_hour_analysis
                analysis_collection.delete_many({})  # Clear existing analysis
                
                analysis_doc = {
                    "analysis_type": "peak_hour_patterns",
                    "patterns": peak_hour_patterns,
                    "calculated_at": datetime.utcnow()
                }
                
                analysis_collection.insert_one(analysis_doc)
                logger.info(f"Created peak hour analysis with {len(peak_hour_patterns)} patterns")
            
            return len(peak_hour_patterns)
            
        except Exception as e:
            logger.error(f"Error analyzing peak hour patterns: {e}")
            return 0
    
    def run_full_correlation_analysis(self) -> Dict[str, Any]:
        """Run complete correlation analysis"""
        if not self.connect():
            return {"error": "Failed to connect to database"}
        
        logger.info("Starting full correlation analysis")
        
        results = {
            "order_correlations": {},
            "performance_metrics": {},
            "time_based_correlations": {},
            "total_processing_time": None,
            "errors": []
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Create order correlations
            logger.info("Creating order correlations...")
            results["order_correlations"] = self.create_order_correlations()
            
            # Create performance metrics
            logger.info("Creating performance metrics...")
            results["performance_metrics"] = self.create_performance_metrics()
            
            # Create time-based correlations
            logger.info("Creating time-based correlations...")
            results["time_based_correlations"] = self.create_time_based_correlations()
            
            end_time = datetime.utcnow()
            results["total_processing_time"] = (end_time - start_time).total_seconds()
            
            logger.info(f"Completed full correlation analysis in {results['total_processing_time']} seconds")
            
        except Exception as e:
            error_msg = f"Error in full correlation analysis: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
