"""
CSV Reader module for data validation and cleaning
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVReader:
    """CSV reader with validation and cleaning capabilities"""
    
    def __init__(self, data_directory: str = "."):
        self.data_directory = Path(data_directory)
        self.csv_files = {
            'orders': 'orders.csv',
            'warehouse_logs': 'warehouse_logs.csv',
            'fleet_logs': 'fleet_logs.csv',
            'clients': 'clients.csv',
            'drivers': 'drivers.csv',
            'warehouses': 'warehouses.csv',
            'feedback': 'feedback.csv',
            'external_factors': 'external_factors.csv'
        }
        
    def read_csv_file(self, file_type: str) -> Optional[pd.DataFrame]:
        """Read and validate a CSV file"""
        if file_type not in self.csv_files:
            logger.error(f"Unknown file type: {file_type}")
            return None
            
        file_path = self.data_directory / self.csv_files[file_type]
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
            
        try:
            logger.info(f"Reading {file_type} from {file_path}")
            df = pd.read_csv(file_path)
            
            # Basic validation
            if df.empty:
                logger.warning(f"Empty CSV file: {file_path}")
                return df
                
            logger.info(f"Successfully read {len(df)} rows from {file_type}")
            
            # Apply specific cleaning based on file type
            df = self._clean_dataframe(df, file_type)
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """Apply file-specific cleaning logic"""
        
        if file_type == 'orders':
            return self._clean_orders(df)
        elif file_type == 'warehouse_logs':
            return self._clean_warehouse_logs(df)
        elif file_type == 'fleet_logs':
            return self._clean_fleet_logs(df)
        elif file_type == 'clients':
            return self._clean_clients(df)
        elif file_type == 'drivers':
            return self._clean_drivers(df)
        elif file_type == 'warehouses':
            return self._clean_warehouses(df)
        elif file_type == 'feedback':
            return self._clean_feedback(df)
        elif file_type == 'external_factors':
            return self._clean_external_factors(df)
        
        return df
    
    def _clean_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean orders data"""
        # Convert date columns
        date_columns = ['order_date', 'promised_delivery_date', 'actual_delivery_date', 'created_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean phone numbers
        if 'customer_phone' in df.columns:
            df['customer_phone'] = df['customer_phone'].astype(str).str.replace(r'[^\d+]', '', regex=True)
        
        # Clean amount column
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Clean address fields - handle multiline addresses
        address_columns = ['delivery_address_line1', 'delivery_address_line2']
        for col in address_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\n', ' ', regex=True).str.strip()
        
        # Standardize status values
        if 'status' in df.columns:
            status_mapping = {
                'delivered': 'Delivered',
                'pending': 'Pending', 
                'failed': 'Failed',
                'in-transit': 'In-Transit',
                'returned': 'Returned'
            }
            df['status'] = df['status'].str.lower().map(status_mapping).fillna(df['status'])
        
        return df
    
    def _clean_warehouse_logs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean warehouse logs data"""
        # Convert datetime columns
        datetime_columns = ['picking_start', 'picking_end', 'dispatch_time']
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate processing time if not present
        if 'picking_start' in df.columns and 'picking_end' in df.columns:
            df['processing_time_minutes'] = (
                df['picking_end'] - df['picking_start']
            ).dt.total_seconds() / 60
        
        # Extract issues from notes
        if 'notes' in df.columns:
            df['issues'] = df['notes'].apply(self._extract_issues_from_notes)
        
        return df
    
    def _clean_fleet_logs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean fleet logs data"""
        # Convert datetime columns
        datetime_columns = ['departure_time', 'arrival_time', 'created_at']
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate delivery time in hours
        if 'departure_time' in df.columns and 'arrival_time' in df.columns:
            df['delivery_time_hours'] = (
                df['arrival_time'] - df['departure_time']
            ).dt.total_seconds() / 3600
        
        # Extract delay reasons from GPS delay notes
        if 'gps_delay_notes' in df.columns:
            df['delay_reasons'] = df['gps_delay_notes'].apply(self._extract_delay_reasons)
        
        return df
    
    def _clean_clients(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean clients data"""
        # Convert created_at
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # Clean phone numbers
        if 'contact_phone' in df.columns:
            df['contact_phone'] = df['contact_phone'].astype(str).str.replace(r'[^\d+]', '', regex=True)
        
        # Clean address fields
        address_columns = ['address_line1', 'address_line2']
        for col in address_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\n', ' ', regex=True).str.strip()
        
        return df
    
    def _clean_drivers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean drivers data"""
        # Convert created_at
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # Clean phone numbers
        if 'phone' in df.columns:
            df['phone'] = df['phone'].astype(str).str.replace(r'[^\d+]', '', regex=True)
        
        # Standardize status
        if 'status' in df.columns:
            df['status'] = df['status'].str.title()
        
        return df
    
    def _clean_warehouses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean warehouses data"""
        # Convert created_at
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # Clean phone numbers
        if 'contact_phone' in df.columns:
            df['contact_phone'] = df['contact_phone'].astype(str).str.replace(r'[^\d+]', '', regex=True)
        
        # Ensure capacity is numeric
        if 'capacity' in df.columns:
            df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
        
        return df
    
    def _clean_feedback(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean feedback data"""
        # Convert created_at
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # Ensure rating is numeric
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Standardize sentiment
        if 'sentiment' in df.columns:
            df['sentiment'] = df['sentiment'].str.title()
        
        return df
    
    def _clean_external_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean external factors data"""
        # Convert recorded_at
        if 'recorded_at' in df.columns:
            df['recorded_at'] = pd.to_datetime(df['recorded_at'], errors='coerce')
        
        # Standardize condition values
        condition_columns = ['traffic_condition', 'weather_condition']
        for col in condition_columns:
            if col in df.columns:
                df[col] = df[col].str.title()
        
        return df
    
    def _extract_issues_from_notes(self, notes: str) -> List[str]:
        """Extract issues from warehouse notes"""
        if pd.isna(notes) or not notes:
            return []
        
        issues = []
        notes_lower = str(notes).lower()
        
        # Define issue patterns
        issue_patterns = {
            'stock_delay': ['stock delay', 'out of stock', 'inventory issue'],
            'slow_packing': ['slow packing', 'packing delay', 'slow process'],
            'system_issue': ['system issue', 'system down', 'technical problem'],
            'staff_shortage': ['staff shortage', 'understaffed', 'manpower issue'],
            'equipment_failure': ['equipment failure', 'machine down', 'breakdown']
        }
        
        for issue_type, patterns in issue_patterns.items():
            if any(pattern in notes_lower for pattern in patterns):
                issues.append(issue_type)
        
        return issues if issues else ['other']
    
    def _extract_delay_reasons(self, gps_notes: str) -> List[str]:
        """Extract delay reasons from GPS delay notes"""
        if pd.isna(gps_notes) or not gps_notes:
            return []
        
        reasons = []
        notes_lower = str(gps_notes).lower()
        
        # Define delay reason patterns
        delay_patterns = {
            'traffic': ['traffic', 'congestion', 'heavy traffic'],
            'weather': ['weather', 'rain', 'fog', 'storm'],
            'breakdown': ['breakdown', 'vehicle issue', 'mechanical'],
            'address_issue': ['address not found', 'wrong address', 'address issue'],
            'customer_unavailable': ['customer not available', 'customer absent'],
            'route_change': ['route change', 'detour', 'road closure']
        }
        
        for reason_type, patterns in delay_patterns.items():
            if any(pattern in notes_lower for pattern in patterns):
                reasons.append(reason_type)
        
        return reasons if reasons else ['other']
    
    def validate_data_integrity(self, df: pd.DataFrame, file_type: str) -> Tuple[bool, List[str]]:
        """Validate data integrity for a dataframe"""
        errors = []
        
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        # Check for required columns based on file type
        required_columns = self._get_required_columns(file_type)
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for duplicate IDs
        id_column = self._get_id_column(file_type)
        if id_column and id_column in df.columns:
            duplicates = df[id_column].duplicated().sum()
            if duplicates > 0:
                errors.append(f"Found {duplicates} duplicate {id_column} values")
        
        # Check for null values in critical columns
        critical_columns = self._get_critical_columns(file_type)
        for col in critical_columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    errors.append(f"Found {null_count} null values in critical column: {col}")
        
        return len(errors) == 0, errors
    
    def _get_required_columns(self, file_type: str) -> List[str]:
        """Get required columns for each file type"""
        required_columns_map = {
            'orders': ['order_id', 'client_id', 'customer_name', 'order_date', 'status'],
            'warehouse_logs': ['log_id', 'order_id', 'warehouse_id'],
            'fleet_logs': ['fleet_log_id', 'order_id', 'driver_id'],
            'clients': ['client_id', 'client_name'],
            'drivers': ['driver_id', 'driver_name'],
            'warehouses': ['warehouse_id', 'warehouse_name'],
            'feedback': ['feedback_id', 'order_id'],
            'external_factors': ['factor_id', 'order_id']
        }
        return required_columns_map.get(file_type, [])
    
    def _get_id_column(self, file_type: str) -> Optional[str]:
        """Get the ID column for each file type"""
        id_column_map = {
            'orders': 'order_id',
            'warehouse_logs': 'log_id',
            'fleet_logs': 'fleet_log_id',
            'clients': 'client_id',
            'drivers': 'driver_id',
            'warehouses': 'warehouse_id',
            'feedback': 'feedback_id',
            'external_factors': 'factor_id'
        }
        return id_column_map.get(file_type)
    
    def _get_critical_columns(self, file_type: str) -> List[str]:
        """Get critical columns that shouldn't have null values"""
        critical_columns_map = {
            'orders': ['order_id', 'client_id', 'order_date', 'status'],
            'warehouse_logs': ['log_id', 'order_id', 'warehouse_id'],
            'fleet_logs': ['fleet_log_id', 'order_id', 'driver_id'],
            'clients': ['client_id', 'client_name'],
            'drivers': ['driver_id', 'driver_name'],
            'warehouses': ['warehouse_id', 'warehouse_name'],
            'feedback': ['feedback_id', 'order_id'],
            'external_factors': ['factor_id', 'order_id']
        }
        return critical_columns_map.get(file_type, [])
    
    def read_all_csv_files(self) -> Dict[str, pd.DataFrame]:
        """Read all CSV files and return as dictionary"""
        dataframes = {}
        
        for file_type in self.csv_files.keys():
            df = self.read_csv_file(file_type)
            if df is not None:
                # Validate data integrity
                is_valid, errors = self.validate_data_integrity(df, file_type)
                if not is_valid:
                    logger.warning(f"Data integrity issues in {file_type}: {errors}")
                
                dataframes[file_type] = df
            else:
                logger.error(f"Failed to read {file_type}")
        
        return dataframes
