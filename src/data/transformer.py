"""
Data Transformer module to convert CSV data to MongoDB documents
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform CSV data to MongoDB document format"""
    
    def __init__(self):
        self.transformers = {
            'orders': self._transform_orders,
            'warehouse_logs': self._transform_warehouse_logs,
            'fleet_logs': self._transform_fleet_logs,
            'clients': self._transform_clients,
            'drivers': self._transform_drivers,
            'warehouses': self._transform_warehouses,
            'feedback': self._transform_feedback,
            'external_factors': self._transform_external_factors
        }
    
    def _safe_list_conversion(self, value) -> List[str]:
        """Safely convert various types to list"""
        if value is None:
            return []
        
        if isinstance(value, list):
            return [str(item) for item in value if item is not None and str(item).strip()]
        
        if isinstance(value, str):
            return [value] if value.strip() else []
        
        # Check for pandas NA values safely
        try:
            if pd.isna(value):
                return []
        except (ValueError, TypeError):
            # If pd.isna fails (e.g., on lists), continue with other checks
            pass
        
        if hasattr(value, '__iter__') and not isinstance(value, str):
            try:
                return [str(item) for item in value if item is not None and str(item).strip()]
            except:
                return []
        
        return [str(value)] if str(value).strip() else []
    
    def transform_dataframe(self, df: pd.DataFrame, collection_type: str) -> List[Dict[str, Any]]:
        """Transform a dataframe to MongoDB documents"""
        if collection_type not in self.transformers:
            logger.error(f"Unknown collection type: {collection_type}")
            return []
        
        try:
            transformer = self.transformers[collection_type]
            documents = transformer(df)
            logger.info(f"Transformed {len(documents)} documents for {collection_type}")
            return documents
        except Exception as e:
            logger.error(f"Error transforming {collection_type}: {e}")
            return []
    
    def _transform_orders(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform orders CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "order_id": int(row['order_id']) if pd.notna(row['order_id']) else None,
                "client_id": int(row['client_id']) if pd.notna(row['client_id']) else None,
                "customer_info": {
                    "name": str(row['customer_name']) if pd.notna(row['customer_name']) else "",
                    "phone": str(row['customer_phone']) if pd.notna(row['customer_phone']) else "",
                    "address": {
                        "line1": str(row['delivery_address_line1']) if pd.notna(row['delivery_address_line1']) else "",
                        "line2": str(row['delivery_address_line2']) if pd.notna(row['delivery_address_line2']) else "",
                        "city": str(row['city']) if pd.notna(row['city']) else "",
                        "state": str(row['state']) if pd.notna(row['state']) else "",
                        "pincode": str(row['pincode']) if pd.notna(row['pincode']) else ""
                    }
                },
                "dates": {
                    "order_date": row['order_date'] if pd.notna(row['order_date']) else None,
                    "promised_delivery": row['promised_delivery_date'] if pd.notna(row['promised_delivery_date']) else None,
                    "actual_delivery": row['actual_delivery_date'] if pd.notna(row['actual_delivery_date']) else None
                },
                "status": str(row['status']) if pd.notna(row['status']) else "Unknown",
                "payment_mode": str(row['payment_mode']) if pd.notna(row['payment_mode']) else "",
                "amount": float(row['amount']) if pd.notna(row['amount']) else 0.0,
                "failure_reason": str(row['failure_reason']) if pd.notna(row['failure_reason']) else None,
                "created_at": row['created_at'] if pd.notna(row['created_at']) else datetime.utcnow()
            }
            
            # Calculate delivery delay if both dates are available
            if (doc['dates']['promised_delivery'] and doc['dates']['actual_delivery']):
                promised = pd.to_datetime(doc['dates']['promised_delivery'])
                actual = pd.to_datetime(doc['dates']['actual_delivery'])
                delay_hours = (actual - promised).total_seconds() / 3600
                doc['delivery_delay_hours'] = delay_hours
            
            documents.append(doc)
        
        return documents
    
    def _transform_warehouse_logs(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform warehouse logs CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "log_id": int(row['log_id']) if pd.notna(row['log_id']) else None,
                "order_id": int(row['order_id']) if pd.notna(row['order_id']) else None,
                "warehouse_id": int(row['warehouse_id']) if pd.notna(row['warehouse_id']) else None,
                "timing": {
                    "picking_start": row['picking_start'] if pd.notna(row['picking_start']) else None,
                    "picking_end": row['picking_end'] if pd.notna(row['picking_end']) else None,
                    "dispatch_time": row['dispatch_time'] if pd.notna(row['dispatch_time']) else None
                },
                "processing_time_minutes": float(row['processing_time_minutes']) if pd.notna(row['processing_time_minutes']) else None,
                "notes": str(row['notes']) if pd.notna(row['notes']) else "",
                "issues": self._safe_list_conversion(row.get('issues', []))
            }
            
            # Calculate processing time if not available but timestamps are
            if (doc['processing_time_minutes'] is None and 
                doc['timing']['picking_start'] and doc['timing']['picking_end']):
                start = pd.to_datetime(doc['timing']['picking_start'])
                end = pd.to_datetime(doc['timing']['picking_end'])
                doc['processing_time_minutes'] = (end - start).total_seconds() / 60
            
            documents.append(doc)
        
        return documents
    
    def _transform_fleet_logs(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform fleet logs CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "fleet_log_id": int(row['fleet_log_id']) if pd.notna(row['fleet_log_id']) else None,
                "order_id": int(row['order_id']) if pd.notna(row['order_id']) else None,
                "driver_id": int(row['driver_id']) if pd.notna(row['driver_id']) else None,
                "vehicle_number": str(row['vehicle_number']) if pd.notna(row['vehicle_number']) else "",
                "route_code": str(row['route_code']) if pd.notna(row['route_code']) else "",
                "gps_delay_notes": str(row['gps_delay_notes']) if pd.notna(row['gps_delay_notes']) else "",
                "timing": {
                    "departure": row['departure_time'] if pd.notna(row['departure_time']) else None,
                    "arrival": row['arrival_time'] if pd.notna(row['arrival_time']) else None
                },
                "delivery_time_hours": float(row['delivery_time_hours']) if pd.notna(row['delivery_time_hours']) else None,
                "delay_reasons": self._safe_list_conversion(row.get('delay_reasons', [])),
                "created_at": row['created_at'] if pd.notna(row['created_at']) else datetime.utcnow()
            }
            
            # Calculate delivery time if not available but timestamps are
            if (doc['delivery_time_hours'] is None and 
                doc['timing']['departure'] and doc['timing']['arrival']):
                departure = pd.to_datetime(doc['timing']['departure'])
                arrival = pd.to_datetime(doc['timing']['arrival'])
                doc['delivery_time_hours'] = (arrival - departure).total_seconds() / 3600
            
            documents.append(doc)
        
        return documents
    
    def _transform_clients(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform clients CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "client_id": int(row['client_id']) if pd.notna(row['client_id']) else None,
                "client_name": str(row['client_name']) if pd.notna(row['client_name']) else "",
                "gst_number": str(row['gst_number']) if pd.notna(row['gst_number']) else "",
                "contact_info": {
                    "person": str(row['contact_person']) if pd.notna(row['contact_person']) else "",
                    "phone": str(row['contact_phone']) if pd.notna(row['contact_phone']) else "",
                    "email": str(row['contact_email']) if pd.notna(row['contact_email']) else ""
                },
                "address": {
                    "line1": str(row['address_line1']) if pd.notna(row['address_line1']) else "",
                    "line2": str(row['address_line2']) if pd.notna(row['address_line2']) else "",
                    "city": str(row['city']) if pd.notna(row['city']) else "",
                    "state": str(row['state']) if pd.notna(row['state']) else "",
                    "pincode": str(row['pincode']) if pd.notna(row['pincode']) else ""
                },
                "created_at": row['created_at'] if pd.notna(row['created_at']) else datetime.utcnow()
            }
            documents.append(doc)
        
        return documents
    
    def _transform_drivers(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform drivers CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "driver_id": int(row['driver_id']) if pd.notna(row['driver_id']) else None,
                "driver_name": str(row['driver_name']) if pd.notna(row['driver_name']) else "",
                "phone": str(row['phone']) if pd.notna(row['phone']) else "",
                "license_number": str(row['license_number']) if pd.notna(row['license_number']) else "",
                "partner_company": str(row['partner_company']) if pd.notna(row['partner_company']) else "",
                "location": {
                    "city": str(row['city']) if pd.notna(row['city']) else "",
                    "state": str(row['state']) if pd.notna(row['state']) else ""
                },
                "status": str(row['status']) if pd.notna(row['status']) else "Unknown",
                "created_at": row['created_at'] if pd.notna(row['created_at']) else datetime.utcnow()
            }
            documents.append(doc)
        
        return documents
    
    def _transform_warehouses(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform warehouses CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "warehouse_id": int(row['warehouse_id']) if pd.notna(row['warehouse_id']) else None,
                "warehouse_name": str(row['warehouse_name']) if pd.notna(row['warehouse_name']) else "",
                "location": {
                    "state": str(row['state']) if pd.notna(row['state']) else "",
                    "city": str(row['city']) if pd.notna(row['city']) else "",
                    "pincode": str(row['pincode']) if pd.notna(row['pincode']) else ""
                },
                "capacity": int(row['capacity']) if pd.notna(row['capacity']) else 0,
                "manager_info": {
                    "name": str(row['manager_name']) if pd.notna(row['manager_name']) else "",
                    "phone": str(row['contact_phone']) if pd.notna(row['contact_phone']) else ""
                },
                "created_at": row['created_at'] if pd.notna(row['created_at']) else datetime.utcnow()
            }
            documents.append(doc)
        
        return documents
    
    def _transform_feedback(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform feedback CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "feedback_id": int(row['feedback_id']) if pd.notna(row['feedback_id']) else None,
                "order_id": int(row['order_id']) if pd.notna(row['order_id']) else None,
                "customer_name": str(row['customer_name']) if pd.notna(row['customer_name']) else "",
                "feedback_text": str(row['feedback_text']) if pd.notna(row['feedback_text']) else "",
                "sentiment": str(row['sentiment']) if pd.notna(row['sentiment']) else "Neutral",
                "rating": int(row['rating']) if pd.notna(row['rating']) else 0,
                "created_at": row['created_at'] if pd.notna(row['created_at']) else datetime.utcnow()
            }
            
            # Extract keywords from feedback text
            doc['keywords'] = self._extract_feedback_keywords(doc['feedback_text'])
            
            documents.append(doc)
        
        return documents
    
    def _transform_external_factors(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform external factors CSV to MongoDB documents"""
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                "factor_id": int(row['factor_id']) if pd.notna(row['factor_id']) else None,
                "order_id": int(row['order_id']) if pd.notna(row['order_id']) else None,
                "conditions": {
                    "traffic": str(row['traffic_condition']) if pd.notna(row['traffic_condition']) else "",
                    "weather": str(row['weather_condition']) if pd.notna(row['weather_condition']) else ""
                },
                "event_type": str(row['event_type']) if pd.notna(row['event_type']) else None,
                "recorded_at": row['recorded_at'] if pd.notna(row['recorded_at']) else datetime.utcnow()
            }
            
            # Calculate severity score based on conditions
            doc['severity_score'] = self._calculate_severity_score(doc['conditions'], doc['event_type'])
            
            documents.append(doc)
        
        return documents
    
    def _extract_feedback_keywords(self, feedback_text: str) -> List[str]:
        """Extract keywords from feedback text"""
        if not feedback_text or pd.isna(feedback_text):
            return []
        
        keywords = []
        text_lower = str(feedback_text).lower()
        
        # Define keyword patterns
        keyword_patterns = {
            'delivery_delay': ['late', 'delay', 'slow', 'behind schedule'],
            'driver_issue': ['driver', 'rude', 'polite', 'professional', 'unprofessional'],
            'package_condition': ['damaged', 'broken', 'good condition', 'perfect'],
            'communication': ['no update', 'informed', 'called', 'message'],
            'address_issue': ['wrong address', 'address not found', 'location'],
            'service_quality': ['excellent', 'good', 'bad', 'terrible', 'satisfied']
        }
        
        for keyword_type, patterns in keyword_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                keywords.append(keyword_type)
        
        return keywords if keywords else ['general']
    
    def _calculate_severity_score(self, conditions: Dict[str, str], event_type: str) -> int:
        """Calculate severity score for external factors (1-10 scale)"""
        score = 1  # Base score
        
        # Traffic condition impact
        traffic_scores = {
            'clear': 1,
            'moderate': 3,
            'heavy': 6,
            'congested': 8
        }
        traffic = conditions.get('traffic', '').lower()
        score += traffic_scores.get(traffic, 2)
        
        # Weather condition impact
        weather_scores = {
            'clear': 1,
            'cloudy': 2,
            'rain': 4,
            'heavy rain': 6,
            'fog': 5,
            'storm': 8
        }
        weather = conditions.get('weather', '').lower()
        score += weather_scores.get(weather, 2)
        
        # Event type impact
        event_scores = {
            'holiday': 2,
            'strike': 7,
            'festival': 3,
            'emergency': 8,
            'road closure': 6
        }
        if event_type:
            event = str(event_type).lower()
            score += event_scores.get(event, 1)
        
        return min(score, 10)  # Cap at 10
    
    def transform_all_data(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict[str, Any]]]:
        """Transform all dataframes to MongoDB documents"""
        transformed_data = {}
        
        for collection_type, df in dataframes.items():
            if not df.empty:
                documents = self.transform_dataframe(df, collection_type)
                transformed_data[collection_type] = documents
                logger.info(f"Transformed {len(documents)} documents for {collection_type}")
            else:
                logger.warning(f"Empty dataframe for {collection_type}")
                transformed_data[collection_type] = []
        
        return transformed_data
