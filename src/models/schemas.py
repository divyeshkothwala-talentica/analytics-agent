"""
Data models and schemas for MongoDB collections
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class Order:
    """Order data model"""
    order_id: str
    client_id: str
    warehouse_id: str
    driver_id: Optional[str]
    order_date: datetime
    delivery_date: Optional[datetime]
    status: str  # pending, processing, shipped, delivered, cancelled
    items: List[Dict[str, Any]]
    total_amount: float
    delivery_address: str
    priority: str  # low, medium, high, urgent
    special_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self):
        """Convert to dictionary for MongoDB insertion"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass
class WarehouseLog:
    """Warehouse operations log model"""
    log_id: str
    warehouse_id: str
    order_id: str
    operation_type: str  # pick, pack, ship, receive, inventory_check
    timestamp: datetime
    operator_id: str
    items_processed: List[Dict[str, Any]]
    processing_time_minutes: float
    status: str  # success, failed, partial
    notes: Optional[str]
    
    def to_dict(self):
        data = asdict(self)
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data


@dataclass
class FleetLog:
    """Fleet/delivery operations log model"""
    log_id: str
    driver_id: str
    order_id: str
    vehicle_id: str
    timestamp: datetime
    event_type: str  # pickup, delivery, delay, route_change, breakdown
    location: Dict[str, float]  # {"lat": float, "lng": float}
    status: str  # on_time, delayed, completed, failed
    delay_minutes: Optional[int]
    fuel_consumption: Optional[float]
    distance_km: Optional[float]
    notes: Optional[str]
    
    def to_dict(self):
        data = asdict(self)
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data


@dataclass
class ExternalFactor:
    """External factors affecting operations"""
    factor_id: str
    date: datetime
    location: str
    factor_type: str  # weather, traffic, event, holiday, strike
    severity: str  # low, medium, high, critical
    description: str
    impact_areas: List[str]  # warehouse, delivery, both
    duration_hours: Optional[float]
    
    def to_dict(self):
        data = asdict(self)
        if isinstance(data['date'], datetime):
            data['date'] = data['date'].isoformat()
        return data


@dataclass
class Feedback:
    """Customer feedback model"""
    feedback_id: str
    order_id: str
    client_id: str
    feedback_date: datetime
    rating: int  # 1-5 scale
    category: str  # delivery_time, product_quality, service, packaging
    comments: Optional[str]
    resolved: bool
    resolution_notes: Optional[str]
    
    def to_dict(self):
        data = asdict(self)
        if isinstance(data['feedback_date'], datetime):
            data['feedback_date'] = data['feedback_date'].isoformat()
        return data


@dataclass
class Client:
    """Client master data model"""
    client_id: str
    company_name: str
    contact_person: str
    email: str
    phone: str
    address: str
    client_type: str  # enterprise, sme, individual
    credit_limit: float
    payment_terms: str
    preferred_delivery_window: str
    special_requirements: List[str]
    active: bool
    created_date: datetime
    
    def to_dict(self):
        data = asdict(self)
        if isinstance(data['created_date'], datetime):
            data['created_date'] = data['created_date'].isoformat()
        return data


@dataclass
class Warehouse:
    """Warehouse master data model"""
    warehouse_id: str
    name: str
    location: str
    address: str
    coordinates: Dict[str, float]  # {"lat": float, "lng": float}
    capacity: int
    current_utilization: float
    operating_hours: str
    manager_id: str
    contact_info: Dict[str, str]
    specializations: List[str]  # cold_storage, hazardous, fragile
    active: bool
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Driver:
    """Driver master data model"""
    driver_id: str
    name: str
    license_number: str
    phone: str
    email: str
    vehicle_type: str
    vehicle_capacity: float
    experience_years: int
    rating: float
    current_status: str  # available, busy, off_duty
    location: Optional[Dict[str, float]]  # {"lat": float, "lng": float}
    shift_start: str
    shift_end: str
    active: bool
    
    def to_dict(self):
        return asdict(self)


class SchemaValidator:
    """Utility class for validating data against schemas"""
    
    @staticmethod
    def validate_order(data: Dict) -> bool:
        """Validate order data"""
        required_fields = ['order_id', 'client_id', 'warehouse_id', 'order_date', 
                          'status', 'items', 'total_amount', 'delivery_address']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_warehouse_log(data: Dict) -> bool:
        """Validate warehouse log data"""
        required_fields = ['log_id', 'warehouse_id', 'order_id', 'operation_type', 
                          'timestamp', 'operator_id', 'status']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_fleet_log(data: Dict) -> bool:
        """Validate fleet log data"""
        required_fields = ['log_id', 'driver_id', 'order_id', 'vehicle_id', 
                          'timestamp', 'event_type', 'location', 'status']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_external_factor(data: Dict) -> bool:
        """Validate external factor data"""
        required_fields = ['factor_id', 'date', 'location', 'factor_type', 
                          'severity', 'description', 'impact_areas']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_feedback(data: Dict) -> bool:
        """Validate feedback data"""
        required_fields = ['feedback_id', 'order_id', 'client_id', 'feedback_date', 
                          'rating', 'category']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_client(data: Dict) -> bool:
        """Validate client data"""
        required_fields = ['client_id', 'company_name', 'contact_person', 'email', 
                          'phone', 'address', 'client_type']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_warehouse(data: Dict) -> bool:
        """Validate warehouse data"""
        required_fields = ['warehouse_id', 'name', 'location', 'address', 
                          'coordinates', 'capacity']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_driver(data: Dict) -> bool:
        """Validate driver data"""
        required_fields = ['driver_id', 'name', 'license_number', 'phone', 
                          'vehicle_type', 'current_status']
        return all(field in data for field in required_fields)


# Collection name mappings
COLLECTION_SCHEMAS = {
    'orders': Order,
    'warehouse_logs': WarehouseLog,
    'fleet_logs': FleetLog,
    'external_factors': ExternalFactor,
    'feedback': Feedback,
    'clients': Client,
    'warehouses': Warehouse,
    'drivers': Driver
}

COLLECTION_VALIDATORS = {
    'orders': SchemaValidator.validate_order,
    'warehouse_logs': SchemaValidator.validate_warehouse_log,
    'fleet_logs': SchemaValidator.validate_fleet_log,
    'external_factors': SchemaValidator.validate_external_factor,
    'feedback': SchemaValidator.validate_feedback,
    'clients': SchemaValidator.validate_client,
    'warehouses': SchemaValidator.validate_warehouse,
    'drivers': SchemaValidator.validate_driver
}