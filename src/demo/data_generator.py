"""
Demo data generator for creating realistic test scenarios
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import csv
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class DemoOrder:
    """Demo order data structure"""
    order_id: str
    client_id: str
    warehouse_id: str
    driver_id: str
    pickup_location: str
    delivery_location: str
    order_date: str
    delivery_date: str
    status: str
    priority: str
    failure_reason: Optional[str] = None
    delay_minutes: int = 0
    customer_rating: Optional[float] = None


@dataclass
class DemoFleetLog:
    """Demo fleet log data structure"""
    log_id: str
    driver_id: str
    vehicle_id: str
    route_id: str
    timestamp: str
    location: str
    status: str
    fuel_level: float
    speed_kmh: float
    issue_reported: Optional[str] = None


@dataclass
class DemoWarehouseLog:
    """Demo warehouse log data structure"""
    log_id: str
    warehouse_id: str
    timestamp: str
    operation_type: str
    order_id: str
    processing_time_minutes: int
    staff_count: int
    equipment_status: str
    issue_reported: Optional[str] = None


class DemoDataGenerator:
    """Generate realistic demo data for testing scenarios"""
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator
        
        Args:
            seed: Random seed for reproducible data generation
        """
        random.seed(seed)
        self.seed = seed
        
        # Demo data configuration
        self.cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Pune', 'Hyderabad', 'Kolkata']
        self.clients = [f'Client_{chr(65+i)}' for i in range(10)]  # Client_A to Client_J
        self.warehouses = [f'WH_{city[:3].upper()}_{i+1}' for city in self.cities[:5] for i in range(2)]
        self.drivers = [f'DRV_{1000+i}' for i in range(50)]
        self.vehicles = [f'VH_{2000+i}' for i in range(30)]
        
        # Failure scenarios
        self.failure_reasons = [
            'address_not_found', 'customer_unavailable', 'payment_failed',
            'vehicle_breakdown', 'traffic_jam', 'weather_conditions',
            'inventory_shortage', 'damaged_package', 'wrong_address',
            'delivery_refused', 'security_issues', 'road_closure'
        ]
        
        self.warehouse_issues = [
            'equipment_malfunction', 'staff_shortage', 'inventory_mismatch',
            'packaging_delay', 'system_downtime', 'quality_check_failed'
        ]
        
        self.vehicle_issues = [
            'engine_trouble', 'flat_tire', 'fuel_shortage', 'gps_malfunction',
            'accident_minor', 'traffic_violation', 'maintenance_required'
        ]
        
        logger.info(f"Demo data generator initialized with seed {seed}")
    
    def generate_orders(self, count: int = 1000, 
                       date_range_days: int = 30,
                       failure_rate: float = 0.15) -> List[DemoOrder]:
        """Generate demo orders
        
        Args:
            count: Number of orders to generate
            date_range_days: Date range for orders (days from today backwards)
            failure_rate: Percentage of orders that should fail (0.0 to 1.0)
            
        Returns:
            List of demo orders
        """
        orders = []
        base_date = datetime.now() - timedelta(days=date_range_days)
        
        for i in range(count):
            # Generate order timing
            order_date = base_date + timedelta(
                days=random.randint(0, date_range_days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Delivery date (usually 1-3 days after order)
            delivery_delay = random.randint(1, 3)
            delivery_date = order_date + timedelta(days=delivery_delay)
            
            # Add some realistic delays
            if random.random() < 0.3:  # 30% chance of delay
                extra_delay = random.randint(1, 8) * 60  # 1-8 hours in minutes
                delivery_date += timedelta(minutes=extra_delay)
                delay_minutes = extra_delay
            else:
                delay_minutes = 0
            
            # Determine status and failure
            if random.random() < failure_rate:
                status = random.choice(['failed', 'cancelled', 'returned'])
                failure_reason = random.choice(self.failure_reasons)
                customer_rating = random.uniform(1.0, 2.5)  # Low rating for failures
            else:
                status = random.choice(['delivered', 'in_transit', 'processing'])
                failure_reason = None
                customer_rating = random.uniform(3.5, 5.0) if status == 'delivered' else None
            
            # Create order
            order = DemoOrder(
                order_id=f'ORD_{10000+i}',
                client_id=random.choice(self.clients),
                warehouse_id=random.choice(self.warehouses),
                driver_id=random.choice(self.drivers),
                pickup_location=random.choice(self.cities),
                delivery_location=random.choice(self.cities),
                order_date=order_date.isoformat(),
                delivery_date=delivery_date.isoformat(),
                status=status,
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                failure_reason=failure_reason,
                delay_minutes=delay_minutes,
                customer_rating=customer_rating
            )
            
            orders.append(order)
        
        logger.info(f"Generated {count} demo orders")
        return orders
    
    def generate_fleet_logs(self, count: int = 2000,
                          date_range_days: int = 30,
                          issue_rate: float = 0.1) -> List[DemoFleetLog]:
        """Generate demo fleet logs
        
        Args:
            count: Number of logs to generate
            date_range_days: Date range for logs
            issue_rate: Percentage of logs with issues
            
        Returns:
            List of demo fleet logs
        """
        logs = []
        base_date = datetime.now() - timedelta(days=date_range_days)
        
        for i in range(count):
            # Generate timestamp
            timestamp = base_date + timedelta(
                days=random.randint(0, date_range_days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Generate realistic vehicle data
            fuel_level = random.uniform(10, 100)
            speed_kmh = random.uniform(0, 80)
            
            # Determine status and issues
            if random.random() < issue_rate:
                status = random.choice(['breakdown', 'maintenance', 'accident'])
                issue_reported = random.choice(self.vehicle_issues)
            else:
                status = random.choice(['active', 'idle', 'loading', 'unloading'])
                issue_reported = None
            
            log = DemoFleetLog(
                log_id=f'FL_{20000+i}',
                driver_id=random.choice(self.drivers),
                vehicle_id=random.choice(self.vehicles),
                route_id=f'RT_{random.randint(100, 999)}',
                timestamp=timestamp.isoformat(),
                location=random.choice(self.cities),
                status=status,
                fuel_level=fuel_level,
                speed_kmh=speed_kmh,
                issue_reported=issue_reported
            )
            
            logs.append(log)
        
        logger.info(f"Generated {count} demo fleet logs")
        return logs
    
    def generate_warehouse_logs(self, count: int = 1500,
                              date_range_days: int = 30,
                              issue_rate: float = 0.08) -> List[DemoWarehouseLog]:
        """Generate demo warehouse logs
        
        Args:
            count: Number of logs to generate
            date_range_days: Date range for logs
            issue_rate: Percentage of logs with issues
            
        Returns:
            List of demo warehouse logs
        """
        logs = []
        base_date = datetime.now() - timedelta(days=date_range_days)
        
        for i in range(count):
            # Generate timestamp
            timestamp = base_date + timedelta(
                days=random.randint(0, date_range_days),
                hours=random.randint(6, 22),  # Warehouse hours
                minutes=random.randint(0, 59)
            )
            
            # Generate processing data
            operation_type = random.choice(['pickup', 'packing', 'sorting', 'loading', 'inventory'])
            processing_time = random.randint(5, 120)  # 5 minutes to 2 hours
            staff_count = random.randint(3, 15)
            
            # Determine equipment status and issues
            if random.random() < issue_rate:
                equipment_status = random.choice(['malfunction', 'maintenance', 'offline'])
                issue_reported = random.choice(self.warehouse_issues)
                processing_time *= 2  # Issues double processing time
            else:
                equipment_status = random.choice(['operational', 'optimal'])
                issue_reported = None
            
            log = DemoWarehouseLog(
                log_id=f'WL_{30000+i}',
                warehouse_id=random.choice(self.warehouses),
                timestamp=timestamp.isoformat(),
                operation_type=operation_type,
                order_id=f'ORD_{random.randint(10000, 11000)}',
                processing_time_minutes=processing_time,
                staff_count=staff_count,
                equipment_status=equipment_status,
                issue_reported=issue_reported
            )
            
            logs.append(log)
        
        logger.info(f"Generated {count} demo warehouse logs")
        return logs
    
    def generate_external_factors(self, date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Generate external factors data (weather, traffic, events)
        
        Args:
            date_range_days: Date range for factors
            
        Returns:
            List of external factor records
        """
        factors = []
        base_date = datetime.now() - timedelta(days=date_range_days)
        
        # Generate daily factors for each city
        for day in range(date_range_days):
            current_date = base_date + timedelta(days=day)
            
            for city in self.cities:
                # Weather conditions
                weather_conditions = random.choice([
                    'clear', 'cloudy', 'light_rain', 'heavy_rain', 
                    'fog', 'storm', 'extreme_heat'
                ])
                
                # Traffic conditions
                traffic_level = random.choice(['low', 'medium', 'high', 'severe'])
                
                # Special events
                special_event = None
                if random.random() < 0.1:  # 10% chance of special event
                    special_event = random.choice([
                        'festival', 'strike', 'road_construction', 'sports_event',
                        'political_rally', 'concert', 'exhibition'
                    ])
                
                factor = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'city': city,
                    'weather_condition': weather_conditions,
                    'temperature_celsius': random.randint(15, 45),
                    'rainfall_mm': random.randint(0, 50) if 'rain' in weather_conditions else 0,
                    'traffic_level': traffic_level,
                    'traffic_delay_factor': {
                        'low': 1.0, 'medium': 1.2, 'high': 1.5, 'severe': 2.0
                    }[traffic_level],
                    'special_event': special_event,
                    'delivery_impact_score': self._calculate_impact_score(
                        weather_conditions, traffic_level, special_event
                    )
                }
                
                factors.append(factor)
        
        logger.info(f"Generated external factors for {date_range_days} days across {len(self.cities)} cities")
        return factors
    
    def generate_feedback_data(self, order_count: int = 800) -> List[Dict[str, Any]]:
        """Generate customer feedback data
        
        Args:
            order_count: Number of feedback records to generate
            
        Returns:
            List of feedback records
        """
        feedback_data = []
        
        for i in range(order_count):
            # Generate feedback timing
            feedback_date = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23)
            )
            
            # Generate ratings (1-5 scale)
            delivery_rating = random.uniform(1.0, 5.0)
            driver_rating = random.uniform(1.0, 5.0)
            packaging_rating = random.uniform(1.0, 5.0)
            
            # Overall rating (weighted average)
            overall_rating = (delivery_rating * 0.4 + driver_rating * 0.3 + packaging_rating * 0.3)
            
            # Generate comments based on rating
            if overall_rating >= 4.0:
                comment_type = random.choice(['excellent', 'good', 'satisfied'])
                comments = {
                    'excellent': ['Outstanding service!', 'Perfect delivery', 'Highly recommended'],
                    'good': ['Good service', 'Delivered on time', 'Professional driver'],
                    'satisfied': ['Satisfactory', 'As expected', 'No issues']
                }
            elif overall_rating >= 3.0:
                comment_type = 'average'
                comments = {
                    'average': ['Average service', 'Could be better', 'Acceptable']
                }
            else:
                comment_type = random.choice(['poor', 'bad'])
                comments = {
                    'poor': ['Delayed delivery', 'Package damaged', 'Unprofessional'],
                    'bad': ['Terrible service', 'Lost package', 'Rude driver']
                }
            
            feedback = {
                'feedback_id': f'FB_{40000+i}',
                'order_id': f'ORD_{random.randint(10000, 11000)}',
                'customer_id': f'CUST_{random.randint(5000, 9999)}',
                'feedback_date': feedback_date.isoformat(),
                'delivery_rating': round(delivery_rating, 1),
                'driver_rating': round(driver_rating, 1),
                'packaging_rating': round(packaging_rating, 1),
                'overall_rating': round(overall_rating, 1),
                'comment': random.choice(comments[comment_type]),
                'would_recommend': overall_rating >= 3.5,
                'delivery_city': random.choice(self.cities)
            }
            
            feedback_data.append(feedback)
        
        logger.info(f"Generated {order_count} feedback records")
        return feedback_data
    
    def _calculate_impact_score(self, weather: str, traffic: str, event: Optional[str]) -> float:
        """Calculate delivery impact score based on external factors"""
        score = 1.0  # Base score (no impact)
        
        # Weather impact
        weather_impact = {
            'clear': 0.0, 'cloudy': 0.1, 'light_rain': 0.2,
            'heavy_rain': 0.5, 'fog': 0.3, 'storm': 0.8, 'extreme_heat': 0.2
        }
        score += weather_impact.get(weather, 0.0)
        
        # Traffic impact
        traffic_impact = {
            'low': 0.0, 'medium': 0.2, 'high': 0.4, 'severe': 0.8
        }
        score += traffic_impact.get(traffic, 0.0)
        
        # Event impact
        if event:
            event_impact = {
                'festival': 0.6, 'strike': 0.9, 'road_construction': 0.4,
                'sports_event': 0.3, 'political_rally': 0.5, 'concert': 0.2,
                'exhibition': 0.1
            }
            score += event_impact.get(event, 0.3)
        
        return round(min(score, 3.0), 2)  # Cap at 3.0 (300% impact)
    
    def create_scenario_data(self, scenario_name: str) -> Dict[str, List[Any]]:
        """Create data for a specific demo scenario
        
        Args:
            scenario_name: Name of the scenario to create data for
            
        Returns:
            Dict with all data collections for the scenario
        """
        scenario_configs = {
            'mumbai_delays': {
                'orders': {'count': 200, 'failure_rate': 0.4, 'date_range_days': 2},
                'fleet_logs': {'count': 300, 'issue_rate': 0.3, 'date_range_days': 2},
                'focus_city': 'Mumbai'
            },
            'client_abc_failures': {
                'orders': {'count': 150, 'failure_rate': 0.25, 'date_range_days': 7},
                'focus_client': 'Client_A'
            },
            'warehouse_performance': {
                'warehouse_logs': {'count': 200, 'issue_rate': 0.2, 'date_range_days': 30},
                'orders': {'count': 300, 'failure_rate': 0.18, 'date_range_days': 30},
                'focus_warehouse': 'WH_MUM_1'
            },
            'seasonal_analysis': {
                'orders': {'count': 500, 'failure_rate': 0.3, 'date_range_days': 60},
                'external_factors': {'date_range_days': 60},
                'special_events': True
            }
        }
        
        config = scenario_configs.get(scenario_name, {})
        data = {}
        
        # Generate orders
        if 'orders' in config:
            orders_config = config['orders']
            data['orders'] = self.generate_orders(**orders_config)
        
        # Generate fleet logs
        if 'fleet_logs' in config:
            fleet_config = config['fleet_logs']
            data['fleet_logs'] = self.generate_fleet_logs(**fleet_config)
        
        # Generate warehouse logs
        if 'warehouse_logs' in config:
            warehouse_config = config['warehouse_logs']
            data['warehouse_logs'] = self.generate_warehouse_logs(**warehouse_config)
        
        # Generate external factors
        if 'external_factors' in config:
            factors_config = config['external_factors']
            data['external_factors'] = self.generate_external_factors(**factors_config)
        
        # Generate feedback
        if scenario_name in ['client_abc_failures', 'seasonal_analysis']:
            data['feedback'] = self.generate_feedback_data(
                order_count=len(data.get('orders', [])) // 2
            )
        
        logger.info(f"Created scenario data for '{scenario_name}'")
        return data
    
    def export_to_csv(self, data: Dict[str, List[Any]], output_dir: str):
        """Export generated data to CSV files
        
        Args:
            data: Dict with data collections
            output_dir: Directory to save CSV files
        """
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        for collection_name, records in data.items():
            if not records:
                continue
            
            filepath = os.path.join(output_dir, f"{collection_name}.csv")
            
            # Convert dataclass objects to dicts if needed
            if hasattr(records[0], '__dict__'):
                records = [asdict(record) for record in records]
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if records:
                    fieldnames = records[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
            
            logger.info(f"Exported {len(records)} records to {filepath}")
    
    def export_to_json(self, data: Dict[str, List[Any]], filepath: str):
        """Export generated data to JSON file
        
        Args:
            data: Dict with data collections
            filepath: Path to save JSON file
        """
        # Convert dataclass objects to dicts if needed
        json_data = {}
        for collection_name, records in data.items():
            if hasattr(records[0], '__dict__'):
                json_data[collection_name] = [asdict(record) for record in records]
            else:
                json_data[collection_name] = records
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        logger.info(f"Exported data to {filepath}")


def main():
    """Main function for standalone data generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate demo data for analytics tool')
    parser.add_argument('--scenario', type=str, help='Generate data for specific scenario')
    parser.add_argument('--output-dir', type=str, default='demo_data', help='Output directory for CSV files')
    parser.add_argument('--output-json', type=str, help='Output JSON file path')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--orders', type=int, default=1000, help='Number of orders to generate')
    parser.add_argument('--logs', type=int, default=2000, help='Number of logs to generate')
    
    args = parser.parse_args()
    
    # Create generator
    generator = DemoDataGenerator(seed=args.seed)
    
    if args.scenario:
        # Generate scenario-specific data
        data = generator.create_scenario_data(args.scenario)
    else:
        # Generate general demo data
        data = {
            'orders': generator.generate_orders(count=args.orders),
            'fleet_logs': generator.generate_fleet_logs(count=args.logs),
            'warehouse_logs': generator.generate_warehouse_logs(count=args.logs//2),
            'external_factors': generator.generate_external_factors(),
            'feedback': generator.generate_feedback_data(order_count=args.orders//2)
        }
    
    # Export data
    if args.output_json:
        generator.export_to_json(data, args.output_json)
    else:
        generator.export_to_csv(data, args.output_dir)
    
    print(f"✅ Demo data generation completed!")
    print(f"Generated collections: {list(data.keys())}")
    for name, records in data.items():
        print(f"  {name}: {len(records)} records")


if __name__ == "__main__":
    main()
