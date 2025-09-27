"""
Warehouse Capacity Analyzer for Natural Language Queries
Integrates with the Analytics Agent to handle warehouse-related questions
"""

import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from ..config.database import get_db, get_collection

logger = logging.getLogger(__name__)


class WarehouseCapacityAnalyzer:
    """Analyze warehouse capacity data through natural language queries"""
    
    def __init__(self):
        """Initialize warehouse analyzer"""
        self.db = get_db()
        self.warehouses_collection = get_collection('warehouses')
        logger.info("WarehouseCapacityAnalyzer initialized")
    
    def get_state_capacity(self, state_name: str) -> Dict[str, Any]:
        """Get total capacity for a specific state"""
        try:
            pipeline = [
                {"$match": {"state": state_name}},
                {
                    "$group": {
                        "_id": "$state",
                        "total_capacity": {"$sum": "$capacity"},
                        "warehouse_count": {"$sum": 1},
                        "avg_capacity": {"$avg": "$capacity"},
                        "cities": {"$addToSet": "$city"},
                        "warehouses": {
                            "$push": {
                                "warehouse_id": "$warehouse_id",
                                "warehouse_name": "$warehouse_name",
                                "city": "$city",
                                "capacity": "$capacity",
                                "manager_name": "$manager_name"
                            }
                        }
                    }
                }
            ]
            
            result = list(self.warehouses_collection.aggregate(pipeline))
            
            if not result:
                return {
                    "error": f"No warehouses found in {state_name}",
                    "total_capacity": 0,
                    "warehouse_count": 0
                }
            
            data = result[0]
            
            # Get city-wise breakdown
            city_pipeline = [
                {"$match": {"state": state_name}},
                {
                    "$group": {
                        "_id": "$city",
                        "total_capacity": {"$sum": "$capacity"},
                        "warehouse_count": {"$sum": 1},
                        "avg_capacity": {"$avg": "$capacity"}
                    }
                },
                {"$sort": {"total_capacity": -1}}
            ]
            
            city_results = list(self.warehouses_collection.aggregate(city_pipeline))
            
            return {
                "state": state_name,
                "total_capacity": data["total_capacity"],
                "warehouse_count": data["warehouse_count"],
                "average_capacity": round(data["avg_capacity"], 2),
                "cities": data["cities"],
                "city_breakdown": city_results,
                "warehouses": data["warehouses"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing state capacity for {state_name}: {e}")
            return {"error": str(e)}
    
    def get_city_capacity(self, city_name: str, state_name: str = None) -> Dict[str, Any]:
        """Get total capacity for a specific city"""
        try:
            match_criteria = {"city": city_name}
            if state_name:
                match_criteria["state"] = state_name
            
            pipeline = [
                {"$match": match_criteria},
                {
                    "$group": {
                        "_id": {
                            "city": "$city",
                            "state": "$state"
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
                }
            ]
            
            result = list(self.warehouses_collection.aggregate(pipeline))
            
            if not result:
                location = f"{city_name}, {state_name}" if state_name else city_name
                return {
                    "error": f"No warehouses found in {location}",
                    "total_capacity": 0,
                    "warehouse_count": 0
                }
            
            data = result[0]
            
            return {
                "city": data["_id"]["city"],
                "state": data["_id"]["state"],
                "total_capacity": data["total_capacity"],
                "warehouse_count": data["warehouse_count"],
                "average_capacity": round(data["avg_capacity"], 2),
                "warehouses": data["warehouses"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing city capacity for {city_name}: {e}")
            return {"error": str(e)}
    
    def get_all_states_summary(self) -> Dict[str, Any]:
        """Get capacity summary for all states"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$state",
                        "total_capacity": {"$sum": "$capacity"},
                        "warehouse_count": {"$sum": 1},
                        "avg_capacity": {"$avg": "$capacity"},
                        "cities": {"$addToSet": "$city"}
                    }
                },
                {"$sort": {"total_capacity": -1}}
            ]
            
            results = list(self.warehouses_collection.aggregate(pipeline))
            
            # Calculate overall totals
            total_capacity = sum(state["total_capacity"] for state in results)
            total_warehouses = sum(state["warehouse_count"] for state in results)
            
            return {
                "overall_summary": {
                    "total_capacity": total_capacity,
                    "total_warehouses": total_warehouses,
                    "average_capacity": round(total_capacity / total_warehouses, 2) if total_warehouses > 0 else 0,
                    "states_count": len(results)
                },
                "state_breakdown": results
            }
            
        except Exception as e:
            logger.error(f"Error getting all states summary: {e}")
            return {"error": str(e)}
    
    def get_top_cities_by_capacity(self, limit: int = 10) -> Dict[str, Any]:
        """Get top cities by total warehouse capacity"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "city": "$city",
                            "state": "$state"
                        },
                        "total_capacity": {"$sum": "$capacity"},
                        "warehouse_count": {"$sum": 1},
                        "avg_capacity": {"$avg": "$capacity"}
                    }
                },
                {"$sort": {"total_capacity": -1}},
                {"$limit": limit}
            ]
            
            results = list(self.warehouses_collection.aggregate(pipeline))
            
            return {
                "top_cities": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting top cities: {e}")
            return {"error": str(e)}
    
    def analyze_warehouse_query(self, query: str) -> Dict[str, Any]:
        """Analyze natural language query about warehouse capacity"""
        query_lower = query.lower()
        
        # Extract state names (you could expand this list)
        states = ["gujarat", "maharashtra", "karnataka", "tamil nadu", "delhi"]
        cities = ["mumbai", "pune", "nagpur", "ahmedabad", "surat", "bengaluru", "mysuru", 
                 "chennai", "coimbatore", "new delhi"]
        
        found_state = None
        found_city = None
        
        for state in states:
            if state in query_lower:
                found_state = state.title()
                break
        
        for city in cities:
            if city in query_lower:
                found_city = city.title()
                break
        
        # Determine query type and execute appropriate analysis
        if "total capacity" in query_lower or "sum of capacity" in query_lower:
            if found_state:
                result = self.get_state_capacity(found_state)
                result["query_type"] = "state_capacity"
                result["analysis"] = f"Total warehouse capacity analysis for {found_state}"
                return result
            elif found_city:
                result = self.get_city_capacity(found_city)
                result["query_type"] = "city_capacity"
                result["analysis"] = f"Total warehouse capacity analysis for {found_city}"
                return result
        
        elif "top cities" in query_lower or "highest capacity" in query_lower:
            result = self.get_top_cities_by_capacity()
            result["query_type"] = "top_cities"
            result["analysis"] = "Top cities by warehouse capacity"
            return result
        
        elif "all states" in query_lower or "summary" in query_lower:
            result = self.get_all_states_summary()
            result["query_type"] = "all_states"
            result["analysis"] = "Warehouse capacity summary for all states"
            return result
        
        # Default: return all states summary
        result = self.get_all_states_summary()
        result["query_type"] = "general"
        result["analysis"] = "General warehouse capacity analysis"
        result["suggestion"] = "Try queries like 'total capacity in Gujarat' or 'top cities by capacity'"
        return result
    
    def format_analysis_result(self, result: Dict[str, Any]) -> str:
        """Format analysis result into human-readable text"""
        if "error" in result:
            return f"❌ Error: {result['error']}"
        
        query_type = result.get("query_type", "general")
        
        if query_type == "state_capacity":
            state = result["state"]
            capacity = result["total_capacity"]
            count = result["warehouse_count"]
            cities = len(result.get("city_breakdown", []))
            
            response = f"🏭 **Warehouse Capacity Analysis for {state}**\n\n"
            response += f"📊 **Total Capacity**: {capacity:,} units\n"
            response += f"🏢 **Number of Warehouses**: {count}\n"
            response += f"🏙️ **Cities Covered**: {cities}\n"
            response += f"📈 **Average Capacity**: {result['average_capacity']:.2f} units\n\n"
            
            if result.get("city_breakdown"):
                response += "**City-wise Breakdown:**\n"
                for city_data in result["city_breakdown"]:
                    city = city_data["_id"]
                    city_capacity = city_data["total_capacity"]
                    city_count = city_data["warehouse_count"]
                    response += f"• {city}: {city_capacity:,} units ({city_count} warehouses)\n"
            
            return response
        
        elif query_type == "city_capacity":
            city = result["city"]
            state = result["state"]
            capacity = result["total_capacity"]
            count = result["warehouse_count"]
            
            response = f"🏭 **Warehouse Capacity Analysis for {city}, {state}**\n\n"
            response += f"📊 **Total Capacity**: {capacity:,} units\n"
            response += f"🏢 **Number of Warehouses**: {count}\n"
            response += f"📈 **Average Capacity**: {result['average_capacity']:.2f} units\n"
            
            return response
        
        elif query_type == "top_cities":
            response = "🏆 **Top Cities by Warehouse Capacity**\n\n"
            for i, city_data in enumerate(result["top_cities"], 1):
                city = city_data["_id"]["city"]
                state = city_data["_id"]["state"]
                capacity = city_data["total_capacity"]
                count = city_data["warehouse_count"]
                response += f"{i}. **{city}, {state}**: {capacity:,} units ({count} warehouses)\n"
            
            return response
        
        elif query_type == "all_states":
            summary = result["overall_summary"]
            response = f"🗺️ **Overall Warehouse Capacity Summary**\n\n"
            response += f"📊 **Total Capacity**: {summary['total_capacity']:,} units\n"
            response += f"🏢 **Total Warehouses**: {summary['total_warehouses']}\n"
            response += f"🏛️ **States Covered**: {summary['states_count']}\n"
            response += f"📈 **Average Capacity**: {summary['average_capacity']:.2f} units\n\n"
            
            response += "**State-wise Breakdown:**\n"
            for state_data in result["state_breakdown"]:
                state = state_data["_id"]
                capacity = state_data["total_capacity"]
                count = state_data["warehouse_count"]
                cities = len(state_data["cities"])
                response += f"• **{state}**: {capacity:,} units ({count} warehouses, {cities} cities)\n"
            
            return response
        
        return "📊 Warehouse capacity analysis completed."
