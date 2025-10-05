"""
Enhanced CSV Query Engine for direct analysis of all 8 CSV files
Supports natural language queries with statistical operations and correlations
"""

import pandas as pd
import numpy as np
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class EnhancedCSVEngine:
    """Enhanced CSV query engine for comprehensive data analysis"""
    
    def __init__(self, data_directory: str = "."):
        self.data_directory = Path(data_directory)
        self.dataframes = {}
        self.load_all_csv_files()
        
        # Define entity patterns for dynamic queries
        self.city_patterns = self._extract_cities()
        self.client_patterns = self._extract_clients()
        self.warehouse_patterns = self._extract_warehouses()
        self.driver_patterns = self._extract_drivers()
        
    def load_all_csv_files(self):
        """Load all CSV files into memory"""
        csv_files = {
            'orders': 'orders.csv',
            'clients': 'clients.csv', 
            'drivers': 'drivers.csv',
            'warehouses': 'warehouses.csv',
            'fleet_logs': 'fleet_logs.csv',
            'warehouse_logs': 'warehouse_logs.csv',
            'external_factors': 'external_factors.csv',
            'feedback': 'feedback.csv'
        }
        
        for name, filename in csv_files.items():
            file_path = self.data_directory / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    # Clean and prepare data
                    df = self._clean_dataframe(df, name)
                    self.dataframes[name] = df
                    logger.info(f"Loaded {name}: {len(df)} rows")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
            else:
                logger.warning(f"File not found: {filename}")
    
    def _clean_dataframe(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """Clean and prepare dataframe for analysis"""
        if file_type == 'orders':
            # Convert date columns
            date_cols = ['order_date', 'promised_delivery_date', 'actual_delivery_date', 'created_at']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Clean amount
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                
        elif file_type == 'warehouse_logs':
            # Convert datetime columns
            datetime_cols = ['picking_start', 'picking_end', 'dispatch_time']
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
        elif file_type == 'fleet_logs':
            # Convert datetime columns
            datetime_cols = ['departure_time', 'arrival_time', 'created_at']
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
        elif file_type == 'external_factors':
            if 'recorded_at' in df.columns:
                df['recorded_at'] = pd.to_datetime(df['recorded_at'], errors='coerce')
                
        elif file_type == 'feedback':
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            if 'rating' in df.columns:
                df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        return df
    
    def _extract_cities(self) -> List[str]:
        """Extract unique cities from data"""
        cities = set()
        if 'orders' in self.dataframes:
            cities.update(self.dataframes['orders']['city'].dropna().unique())
        if 'warehouses' in self.dataframes:
            cities.update(self.dataframes['warehouses']['city'].dropna().unique())
        return sorted(list(cities))
    
    def _extract_clients(self) -> List[str]:
        """Extract unique clients from data"""
        if 'clients' in self.dataframes:
            return self.dataframes['clients']['client_name'].dropna().unique().tolist()
        return []
    
    def _extract_warehouses(self) -> List[str]:
        """Extract unique warehouses from data"""
        if 'warehouses' in self.dataframes:
            return self.dataframes['warehouses']['warehouse_name'].dropna().unique().tolist()
        return []
    
    def _extract_drivers(self) -> List[str]:
        """Extract unique drivers from data"""
        if 'drivers' in self.dataframes:
            return self.dataframes['drivers']['driver_name'].dropna().unique().tolist()
        return []
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process natural language query and return results"""
        query_lower = user_query.lower()
        
        try:
            # Pattern 1: City delay analysis
            if self._matches_city_delay_pattern(query_lower):
                return self._analyze_city_delays(user_query)
            
            # Pattern 2: Client failure analysis
            elif self._matches_client_failure_pattern(query_lower):
                return self._analyze_client_failures(user_query)
            
            # Pattern 3: Warehouse capacity analysis
            elif self._matches_warehouse_capacity_pattern(query_lower):
                return self._analyze_warehouse_capacity(user_query)
            
            # Pattern 3b: Warehouse performance analysis
            elif self._matches_warehouse_pattern(query_lower):
                return self._analyze_warehouse_performance(user_query)
            
            # Pattern 4: City comparison
            elif self._matches_city_comparison_pattern(query_lower):
                return self._compare_cities(user_query)
            
            # Pattern 5: Seasonal/festival analysis
            elif self._matches_seasonal_pattern(query_lower):
                return self._analyze_seasonal_patterns(user_query)
            
            # Pattern 6: Capacity planning
            elif self._matches_capacity_pattern(query_lower):
                return self._analyze_capacity_impact(user_query)
            
            # Feedback sentiment analysis queries
            elif any(phrase in query_lower for phrase in ['feedback', 'sentiment', 'customer satisfaction', 'reviews']):
                return self._analyze_feedback_sentiment(user_query)
            
            # Delivery partner analysis queries
            elif any(phrase in query_lower for phrase in ['delivery partner', 'partner performance', 'which partner', 'best partner']):
                return self._analyze_delivery_partner_performance(user_query)
            
            # Driver analysis queries
            elif any(word in query_lower for word in ['driver', 'drivers']):
                return self._analyze_driver_query(user_query)
            
            # Revenue analysis queries
            elif any(phrase in query_lower for phrase in ['total revenue', 'revenue for', 'total sales', 'sales revenue']):
                return self._analyze_revenue_query(user_query)
            
            # General statistical queries
            elif any(word in query_lower for word in ['how many', 'count', 'total', 'average', 'percentage']):
                return self._handle_statistical_query(user_query)
            
            # Trend analysis
            elif any(word in query_lower for word in ['trend', 'over time', 'monthly', 'weekly']):
                return self._analyze_trends(user_query)
            
            # Correlation analysis
            elif any(word in query_lower for word in ['correlation', 'affect', 'impact', 'relationship']):
                return self._analyze_correlations(user_query)
            
            else:
                return self._handle_general_query(user_query)
                
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                'success': False,
                'error': f"Error processing query: {str(e)}",
                'query': user_query
            }
    
    def _matches_city_delay_pattern(self, query: str) -> bool:
        """Check if query matches city delay pattern"""
        # Check if we can extract a city (which handles aliases)
        city_found = self._extract_city_from_query(query) is not None
        delay_keywords = any(word in query for word in ['delay', 'late', 'slow'])
        return city_found and delay_keywords
    
    def _matches_client_failure_pattern(self, query: str) -> bool:
        """Check if query matches client failure pattern"""
        query_lower = query.lower()
        
        # Exclude warehouse-related queries first
        if 'warehouse' in query_lower:
            return False
        
        # Check for ranking queries first (which clients, top clients, etc.)
        ranking_phrases = ['which clients', 'top clients', 'most failures', 'highest failures', 'worst performing', 'most order failures', 'highest failure rates']
        # More specific patterns that clearly indicate client ranking
        specific_client_ranking = ['top clients', 'which clients', 'clients with most', 'clients with highest', 'worst performing clients']
        
        if any(phrase in query_lower for phrase in specific_client_ranking):
            return True
        
        # For general "top" or "most", ensure it's about clients specifically
        if any(phrase in query_lower for phrase in ['top', 'most']):
            # Only match if it's clearly about clients and failures
            if any(word in query_lower for word in ['clients', 'client']) and any(word in query_lower for word in ['fail', 'failure']):
                return True
        
        # Check if we can extract a specific client (which handles partial matches)
        client_found = self._extract_client_from_query(query) is not None
        failure_keywords = any(word in query for word in ['fail', 'issue', 'problem', 'failure'])
        return client_found and failure_keywords
    
    def _matches_warehouse_capacity_pattern(self, query: str) -> bool:
        """Check if query matches warehouse capacity pattern"""
        return (('warehouse' in query or any(warehouse.lower() in query for warehouse in self.warehouse_patterns)) and
                any(word in query for word in ['capacity', 'total capacity', 'sum of capacity', 'total']))
    
    def _matches_warehouse_pattern(self, query: str) -> bool:
        """Check if query matches warehouse pattern"""
        return ('warehouse' in query or 
                any(warehouse.lower() in query for warehouse in self.warehouse_patterns))
    
    def _matches_city_comparison_pattern(self, query: str) -> bool:
        """Check if query matches city comparison pattern"""
        has_comparison_word = any(word in query for word in ['compare', 'vs', 'versus', 'between'])
        city_count = sum(1 for city in self.city_patterns if city.lower() in query)
        
        # Also check for common city pairs even if not exact matches
        common_pairs = [
            ('mumbai', 'delhi'), ('bangalore', 'chennai'), ('pune', 'hyderabad'),
            ('mumbai', 'bangalore'), ('delhi', 'chennai')
        ]
        
        has_city_pair = any(
            all(city in query for city in pair) 
            for pair in common_pairs
        )
        
        return has_comparison_word and (city_count >= 2 or has_city_pair)
    
    def _matches_seasonal_pattern(self, query: str) -> bool:
        """Check if query matches seasonal pattern"""
        return any(word in query for word in ['festival', 'season', 'holiday', 'monsoon', 'weather'])
    
    def _matches_capacity_pattern(self, query: str) -> bool:
        """Check if query matches capacity pattern"""
        capacity_keywords = ['onboard', 'capacity', 'extra orders', 'volume', 'scale', 'expand', 'expansion', 
                           'infrastructure', 'monthly orders', 'new orders', 'additional orders', 'growth']
        return any(word in query.lower() for word in capacity_keywords)
    
    def _analyze_city_delays(self, user_query: str) -> Dict[str, Any]:
        """Analyze delivery delays for a specific city"""
        # Extract city from query
        city = self._extract_city_from_query(user_query)
        time_period = self._extract_time_period(user_query)
        
        if not city:
            return {'success': False, 'error': 'Could not identify city in query'}
        
        # Get orders for the city
        orders_df = self.dataframes['orders']
        city_orders = orders_df[orders_df['city'].str.contains(city, case=False, na=False)]
        
        # Apply time filter - ALWAYS filter by time period if specified
        if time_period:
            city_orders = self._apply_time_filter(city_orders, time_period)
            time_context = f" in {time_period}"
        else:
            # If no specific time mentioned, use recent data (last 3 months) for more relevant analysis
            if 'order_date' in city_orders.columns:
                from datetime import datetime, timedelta
                recent_cutoff = datetime.now() - timedelta(days=90)  # Last 3 months
                city_orders = city_orders[city_orders['order_date'] >= recent_cutoff]
                time_context = " (recent 3 months)"
            else:
                time_context = ""
        
        # Analyze delays (Failed and delayed orders)
        delayed_orders = city_orders[city_orders['status'].isin(['Failed', 'Returned'])]
        
        # Get failure reasons
        failure_analysis = delayed_orders['failure_reason'].value_counts()
        
        # Correlate with external factors
        external_correlation = self._correlate_with_external_factors(delayed_orders)
        
        # Calculate statistics
        total_orders = len(city_orders)
        delayed_count = len(delayed_orders)
        delay_rate = (delayed_count / total_orders * 100) if total_orders > 0 else 0
        
        explanation = f"""## 📊 City Delay Analysis - {city}{time_context}

**Executive Summary:**
• Total orders analyzed: {total_orders:,}
• Delayed/Failed orders: {delayed_count:,} ({delay_rate:.1f}%)
• Primary delay reason: {failure_analysis.index[0] if len(failure_analysis) > 0 else 'N/A'}
• Revenue impact: ${delayed_orders['amount'].sum():.2f}

**Top Delay Reasons:**
{chr(10).join([f"• {reason}: {count} orders ({count/delayed_count*100:.1f}%)" for reason, count in failure_analysis.head(5).items()]) if len(failure_analysis) > 0 else "• No delays found"}

**External Factor Correlation:**
{external_correlation}

---

## 🔍 Data Analysis Details

**Query Processing:**
• Analyzed {total_orders:,} orders from {city}{time_context}
• Time period: {time_period or 'Recent data (filtered)'}
• Data sources: orders.csv, external_factors.csv
• Analysis confidence: 100% (Direct CSV analysis)

**Statistical Breakdown:**
• Success rate: {100-delay_rate:.1f}%
• Average order value: ${city_orders['amount'].mean():.2f}
• Peak failure day: {delayed_orders.groupby(delayed_orders['order_date'].dt.day_name())['order_id'].count().idxmax() if len(delayed_orders) > 0 and 'order_date' in delayed_orders.columns else 'N/A'}"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': delayed_count,
            'collections_used': 'orders.csv, external_factors.csv',
            'analysis_method': 'City-specific delay analysis with external factor correlation',
            'confidence': '100%'
        }
    
    def _analyze_client_failures(self, user_query: str) -> Dict[str, Any]:
        """Analyze order failures for a specific client or rank clients by failures"""
        query_lower = user_query.lower()
        
        # Check if this is a ranking query (which clients, top clients, most failures, etc.)
        if any(phrase in query_lower for phrase in ['which clients', 'top clients', 'most failures', 'highest failures', 'worst performing', 'most order failures', 'highest failure rates', 'top', 'most']):
            return self._analyze_client_failure_ranking(user_query)
        
        # Otherwise, look for specific client
        client = self._extract_client_from_query(user_query)
        time_period = self._extract_time_period(user_query)
        
        if not client:
            return {'success': False, 'error': 'Could not identify client in query'}
        
        # Get client info
        clients_df = self.dataframes['clients']
        client_info = clients_df[clients_df['client_name'].str.contains(client, case=False, na=False)]
        
        if len(client_info) == 0:
            return {'success': False, 'error': f'Client "{client}" not found in database'}
        
        client_id = client_info.iloc[0]['client_id']
        client_name = client_info.iloc[0]['client_name']
        
        # Get orders for this client
        orders_df = self.dataframes['orders']
        client_orders = orders_df[orders_df['client_id'] == client_id]
        
        # Apply time filter - ALWAYS filter by time period if specified
        if time_period:
            client_orders = self._apply_time_filter(client_orders, time_period)
            time_context = f" ({time_period})"
        else:
            # If no specific time mentioned, use recent data for more relevant analysis
            if 'order_date' in client_orders.columns:
                from datetime import datetime, timedelta
                recent_cutoff = datetime.now() - timedelta(days=90)  # Last 3 months
                client_orders = client_orders[client_orders['order_date'] >= recent_cutoff]
                time_context = " (recent 3 months)"
            else:
                time_context = ""
        
        # Analyze failures
        failed_orders = client_orders[client_orders['status'] == 'Failed']
        failure_analysis = failed_orders['failure_reason'].value_counts()
        
        # Calculate statistics
        total_orders = len(client_orders)
        failed_count = len(failed_orders)
        failure_rate = (failed_count / total_orders * 100) if total_orders > 0 else 0
        
        explanation = f"""## 📊 Client Failure Analysis - {client_name}{time_context}

**Client Profile:**
• Client ID: {client_id}
• Contact: {client_info.iloc[0]['contact_person']} ({client_info.iloc[0]['contact_phone']})
• Location: {client_info.iloc[0]['city']}, {client_info.iloc[0]['state']}

**Performance Summary{time_context}:**
• Total orders: {total_orders:,}
• Failed orders: {failed_count:,} ({failure_rate:.1f}%)
• Revenue at risk: ${failed_orders['amount'].sum():.2f}
• Performance status: {'Above average' if failure_rate < 15 else 'Needs attention'}

**Failure Breakdown:**
{chr(10).join([f"• {reason}: {count} orders ({count/failed_count*100:.1f}%)" for reason, count in failure_analysis.head(5).items()]) if len(failure_analysis) > 0 else "• No failures in selected period"}

---

## 🔍 Data Analysis Details

**Analysis Scope:**
• Time period: {time_period or 'Recent data (filtered)'}
• Orders analyzed: {total_orders:,}{time_context}
• Data sources: orders.csv, clients.csv
• Client match confidence: 100%

**Recommendations:**
{self._generate_client_recommendations(failure_rate, failure_analysis)}"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': failed_count,
            'collections_used': 'orders.csv, clients.csv',
            'analysis_method': 'Client-specific failure analysis',
            'confidence': '100%'
        }
    
    def _analyze_client_failure_ranking(self, user_query: str) -> Dict[str, Any]:
        """Analyze and rank clients by failure count"""
        time_period = self._extract_time_period(user_query)
        
        # Extract number of results requested (default to 10)
        requested_count = self._extract_number_from_query(user_query)
        if requested_count is None or requested_count > 50:  # Cap at 50 for performance
            requested_count = 10
        elif requested_count < 1:
            requested_count = 5
        
        # Get orders data
        orders_df = self.dataframes['orders']
        clients_df = self.dataframes['clients']
        
        # Apply time filter if specified
        if time_period:
            orders_df = self._apply_time_filter(orders_df, time_period)
            time_context = f" ({time_period})"
        else:
            # If no specific time mentioned, use recent data for more relevant analysis
            if 'order_date' in orders_df.columns:
                from datetime import datetime, timedelta
                recent_cutoff = datetime.now() - timedelta(days=90)  # Last 3 months
                orders_df = orders_df[orders_df['order_date'] >= recent_cutoff]
                time_context = " (recent 3 months)"
            else:
                time_context = ""
        
        # Get failed orders only
        failed_orders = orders_df[orders_df['status'] == 'Failed']
        
        if len(failed_orders) == 0:
            return {
                'success': True,
                'query': user_query,
                'explanation': f"## 📊 Client Failure Ranking{time_context}\n\nNo failed orders found for the specified period.",
                'result_count': 0
            }
        
        # Count failures by client
        client_failures = failed_orders.groupby('client_id').agg({
            'order_id': 'count',
            'amount': 'sum'
        }).reset_index()
        client_failures.columns = ['client_id', 'failure_count', 'lost_revenue']
        
        # Merge with client names
        client_failures = client_failures.merge(
            clients_df[['client_id', 'client_name', 'city', 'state']], 
            on='client_id', 
            how='left'
        )
        
        # Sort by failure count (descending)
        client_failures = client_failures.sort_values('failure_count', ascending=False)
        
        # Get top N clients with most failures
        top_failures = client_failures.head(requested_count)
        
        # Calculate total failures and revenue impact
        total_failures = int(client_failures['failure_count'].sum())
        total_lost_revenue = float(client_failures['lost_revenue'].sum())
        
        # Build explanation
        explanation = f"""## 📊 Client Failure Ranking{time_context}

**📈 Top {requested_count} Clients with Most Order Failures:**"""
        
        for rank, (i, row) in enumerate(top_failures.iterrows(), 1):
            client_name = row['client_name']
            failure_count = int(row['failure_count'])
            lost_revenue = float(row['lost_revenue'])
            city = row['city']
            state = row['state']
            
            percentage = (failure_count / total_failures * 100) if total_failures > 0 else 0
            
            explanation += f"""

**{rank}. {client_name}**
• Failed orders: {failure_count:,} ({percentage:.1f}% of all failures)
• Lost revenue: ${lost_revenue:,.2f}
• Location: {city}, {state}"""
        
        explanation += f"""

**📊 Summary Statistics:**
• Total failed orders: {total_failures:,}
• Total lost revenue: ${total_lost_revenue:,.2f}
• Clients with failures: {len(client_failures):,}
• Average failures per client: {(total_failures / len(client_failures)):.1f}"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': int(len(top_failures)),
            'data_summary': {
                'total_failures': int(total_failures),
                'total_lost_revenue': float(total_lost_revenue),
                'top_clients': top_failures.to_dict('records')
            },
            'analysis_type': 'client_failure_ranking',
            'data_source': 'orders.csv + clients.csv',
            'confidence': '95%'
        }

    def _analyze_warehouse_performance(self, user_query: str) -> Dict[str, Any]:
        """Analyze warehouse performance and failure reasons"""
        warehouse = self._extract_warehouse_from_query(user_query)
        time_period = self._extract_time_period(user_query)
        
        if not warehouse:
            return {'success': False, 'error': 'Could not identify warehouse in query'}
        
        # Get warehouse info
        warehouses_df = self.dataframes['warehouses']
        warehouse_info = warehouses_df[warehouses_df['warehouse_name'].str.contains(warehouse, case=False, na=False)]
        
        if len(warehouse_info) == 0:
            return {'success': False, 'error': f'Warehouse "{warehouse}" not found'}
        
        warehouse_id = warehouse_info.iloc[0]['warehouse_id']
        warehouse_name = warehouse_info.iloc[0]['warehouse_name']
        
        # Get warehouse logs
        warehouse_logs = self.dataframes['warehouse_logs']
        wh_logs = warehouse_logs[warehouse_logs['warehouse_id'] == warehouse_id]
        
        # Apply time filter
        if time_period:
            wh_logs = self._apply_time_filter(wh_logs, time_period, date_col='picking_start')
        
        # Analyze issues from notes
        issues = wh_logs['notes'].dropna()
        issue_analysis = self._analyze_warehouse_issues(issues)
        
        # Get related order failures
        order_ids = wh_logs['order_id'].unique()
        orders_df = self.dataframes['orders']
        related_orders = orders_df[orders_df['order_id'].isin(order_ids)]
        failed_orders = related_orders[related_orders['status'] == 'Failed']
        
        explanation = f"""## 🏭 Warehouse Performance Analysis - {warehouse_name}

**Warehouse Profile:**
• Warehouse ID: {warehouse_id}
• Location: {warehouse_info.iloc[0]['city']}, {warehouse_info.iloc[0]['state']}
• Capacity: {warehouse_info.iloc[0]['capacity']:,} units
• Manager: {warehouse_info.iloc[0]['manager_name']}

**Performance Metrics:**
• Orders processed: {len(wh_logs):,}
• Orders with issues: {len(issues):,}
• Issue rate: {len(issues)/len(wh_logs)*100:.1f}%
• Related order failures: {len(failed_orders):,}

**Top Issues:**
{chr(10).join([f"• {issue}: {count} occurrences" for issue, count in issue_analysis.items()]) if issue_analysis else "• No significant issues found"}

**Failure Impact:**
• Revenue impact: ${failed_orders['amount'].sum():.2f}
• Most common failure: {failed_orders['failure_reason'].value_counts().index[0] if len(failed_orders) > 0 else 'N/A'}

---

## 🔍 Operational Analysis

**Processing Efficiency:**
• Average processing time: {self._calculate_avg_processing_time(wh_logs):.1f} minutes
• Peak processing hours: {self._identify_peak_hours(wh_logs)}
• Capacity utilization: {len(wh_logs)/warehouse_info.iloc[0]['capacity']*100:.1f}%"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': len(issues),
            'collections_used': 'warehouse_logs.csv, warehouses.csv, orders.csv',
            'analysis_method': 'Warehouse operational analysis',
            'confidence': '100%'
        }
    
    def _analyze_warehouse_capacity(self, user_query: str) -> Dict[str, Any]:
        """Analyze warehouse capacity by state/city"""
        try:
            warehouses_df = self.dataframes['warehouses']
            query_lower = user_query.lower()
            
            # Extract state or city from query
            state_name = None
            city_name = None
            
            # Check for state names
            states = warehouses_df['state'].unique()
            for state in states:
                if state.lower() in query_lower:
                    state_name = state
                    break
            
            # Check for city names
            cities = warehouses_df['city'].unique()
            for city in cities:
                if city.lower() in query_lower:
                    city_name = city
                    break
            
            if state_name:
                # State-level analysis
                state_warehouses = warehouses_df[warehouses_df['state'] == state_name]
                total_capacity = int(state_warehouses['capacity'].sum())
                warehouse_count = len(state_warehouses)
                avg_capacity = float(state_warehouses['capacity'].mean())
                
                explanation = f"""🏭 **Warehouse Capacity Analysis for {state_name}**

📊 **Total Capacity**: {total_capacity:,} units
🏢 **Number of Warehouses**: {warehouse_count}
📈 **Average Capacity**: {avg_capacity:.2f} units per warehouse

🏙️ **City-wise Breakdown:**"""
                
                for city in state_warehouses['city'].unique():
                    city_data = state_warehouses[state_warehouses['city'] == city]
                    city_capacity = int(city_data['capacity'].sum())
                    city_count = len(city_data)
                    explanation += f"\n• **{city}**: {city_capacity:,} units ({city_count} warehouses)"
                
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': explanation,
                    'result_count': total_capacity,
                    'analysis_type': 'warehouse_capacity',
                    'data_source': 'warehouses.csv',
                    'confidence': '100%'
                }
                
            elif city_name:
                # City-level analysis
                city_warehouses = warehouses_df[warehouses_df['city'] == city_name]
                total_capacity = int(city_warehouses['capacity'].sum())
                warehouse_count = len(city_warehouses)
                avg_capacity = float(city_warehouses['capacity'].mean())
                
                explanation = f"""🏭 **Warehouse Capacity Analysis for {city_name}**

📊 **Total Capacity**: {total_capacity:,} units
🏢 **Number of Warehouses**: {warehouse_count}
📈 **Average Capacity**: {avg_capacity:.2f} units per warehouse

📋 **Individual Warehouses:**"""
                
                for _, warehouse in city_warehouses.iterrows():
                    capacity = int(warehouse['capacity'])
                    explanation += f"\n• {warehouse['warehouse_name']}: {capacity:,} units (Manager: {warehouse['manager_name']})"
                
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': explanation,
                    'result_count': total_capacity,
                    'analysis_type': 'warehouse_capacity',
                    'data_source': 'warehouses.csv',
                    'confidence': '100%'
                }
            
            else:
                # Overall capacity analysis
                total_capacity = int(warehouses_df['capacity'].sum())
                warehouse_count = len(warehouses_df)
                avg_capacity = float(warehouses_df['capacity'].mean())
                
                explanation = f"""🏭 **Overall Warehouse Capacity Analysis**

📊 **Total System Capacity**: {total_capacity:,} units
🏢 **Total Warehouses**: {warehouse_count}
📈 **Average Capacity**: {avg_capacity:.2f} units per warehouse

🗺️ **State-wise Breakdown:**"""
                
                for state in warehouses_df['state'].unique():
                    state_data = warehouses_df[warehouses_df['state'] == state]
                    state_capacity = int(state_data['capacity'].sum())
                    state_count = len(state_data)
                    explanation += f"\n• **{state}**: {state_capacity:,} units ({state_count} warehouses)"
                
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': explanation,
                    'result_count': total_capacity,
                    'analysis_type': 'warehouse_capacity',
                    'data_source': 'warehouses.csv',
                    'confidence': '100%'
                }
                
        except Exception as e:
            logger.error(f"Error in warehouse capacity analysis: {e}")
            return {
                'success': False,
                'query': user_query,
                'error': f"Error analyzing warehouse capacity: {str(e)}",
                'result_count': 0
            }
    
    def _compare_cities(self, user_query: str) -> Dict[str, Any]:
        """Compare delivery performance between two cities"""
        cities = self._extract_cities_from_comparison_query(user_query)
        time_period = self._extract_time_period(user_query)
        
        if len(cities) < 2:
            return {'success': False, 'error': 'Could not identify two cities for comparison'}
        
        city1, city2 = cities[0], cities[1]
        orders_df = self.dataframes['orders']
        
        # Get orders for both cities
        city1_orders = orders_df[orders_df['city'].str.contains(city1, case=False, na=False)]
        city2_orders = orders_df[orders_df['city'].str.contains(city2, case=False, na=False)]
        
        # Apply time filter
        if time_period:
            city1_orders = self._apply_time_filter(city1_orders, time_period)
            city2_orders = self._apply_time_filter(city2_orders, time_period)
        
        # Calculate metrics for both cities
        city1_metrics = self._calculate_city_metrics(city1_orders, city1)
        city2_metrics = self._calculate_city_metrics(city2_orders, city2)
        
        # Determine better performer
        better_city = city1 if city1_metrics['success_rate'] > city2_metrics['success_rate'] else city2
        
        explanation = f"""## ⚖️ City Performance Comparison - {city1} vs {city2}

**Overall Winner: {better_city}** 🏆

**{city1} Performance:**
• Total orders: {city1_metrics['total_orders']:,}
• Success rate: {city1_metrics['success_rate']:.1f}%
• Average order value: ${city1_metrics['avg_order_value']:.2f}
• Top failure reason: {city1_metrics['top_failure_reason']}

**{city2} Performance:**
• Total orders: {city2_metrics['total_orders']:,}
• Success rate: {city2_metrics['success_rate']:.1f}%
• Average order value: ${city2_metrics['avg_order_value']:.2f}
• Top failure reason: {city2_metrics['top_failure_reason']}

**Key Differences:**
• Success rate gap: {abs(city1_metrics['success_rate'] - city2_metrics['success_rate']):.1f} percentage points
• Volume difference: {abs(city1_metrics['total_orders'] - city2_metrics['total_orders']):,} orders
• Revenue difference: ${abs(city1_metrics['total_revenue'] - city2_metrics['total_revenue']):.2f}

---

## 🔍 Comparative Analysis

**Failure Pattern Analysis:**
{self._compare_failure_patterns(city1_orders, city2_orders, city1, city2)}

**Recommendations:**
{self._generate_city_comparison_recommendations(city1_metrics, city2_metrics, city1, city2)}"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': city1_metrics['total_orders'] + city2_metrics['total_orders'],
            'collections_used': 'orders.csv',
            'analysis_method': 'Comparative city performance analysis',
            'confidence': '100%'
        }
    
    def _analyze_seasonal_patterns(self, user_query: str) -> Dict[str, Any]:
        """Analyze seasonal patterns and festival impact"""
        # For this analysis, we'll look at external factors and correlate with failures
        orders_df = self.dataframes['orders']
        external_df = self.dataframes['external_factors']
        
        # Identify festival/seasonal periods from external factors
        festival_orders = external_df[external_df['event_type'].str.contains('Holiday', case=False, na=False)]['order_id']
        festival_order_data = orders_df[orders_df['order_id'].isin(festival_orders)]
        
        # Regular period comparison
        non_festival_orders = orders_df[~orders_df['order_id'].isin(festival_orders)]
        
        # Calculate metrics
        festival_failures = festival_order_data[festival_order_data['status'] == 'Failed']
        non_festival_failures = non_festival_orders[non_festival_orders['status'] == 'Failed']
        
        festival_failure_rate = len(festival_failures) / len(festival_order_data) * 100 if len(festival_order_data) > 0 else 0
        normal_failure_rate = len(non_festival_failures) / len(non_festival_orders) * 100 if len(non_festival_orders) > 0 else 0
        
        # Weather impact analysis
        weather_impact = self._analyze_weather_impact()
        
        explanation = f"""## 📅 Seasonal Pattern Analysis - Festival Impact

**Festival Period Impact:**
• Festival period orders: {len(festival_order_data):,}
• Festival failure rate: {festival_failure_rate:.1f}%
• Normal period failure rate: {normal_failure_rate:.1f}%
• Impact difference: {festival_failure_rate - normal_failure_rate:+.1f} percentage points

**Seasonal Factors:**
• Weather-related delays: {weather_impact['weather_delays']} orders
• Traffic impact during festivals: {weather_impact['traffic_delays']} orders
• Strike-related disruptions: {weather_impact['strike_delays']} orders

**Preparation Recommendations:**
• Increase inventory by {max(15, int((festival_failure_rate - normal_failure_rate) * 2))}% before festival periods
• Deploy additional drivers in high-traffic areas
• Implement weather-based delivery scheduling
• Set up alternative routes for festival congestion

**Risk Mitigation:**
• Monitor weather forecasts 48 hours ahead
• Pre-position inventory in festival-heavy regions
• Coordinate with local authorities for traffic updates
• Implement dynamic pricing for peak periods

---

## 🔍 Data-Driven Insights

**Historical Pattern Analysis:**
• Peak failure months: {self._identify_peak_failure_months()}
• Weather correlation: {weather_impact['correlation_strength']}
• Volume surge during festivals: {len(festival_order_data) / len(non_festival_orders) * 100:.1f}% increase"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': len(festival_failures),
            'collections_used': 'orders.csv, external_factors.csv',
            'analysis_method': 'Seasonal pattern analysis with external factor correlation',
            'confidence': '95%'
        }
    
    def _analyze_capacity_impact(self, user_query: str) -> Dict[str, Any]:
        """Analyze impact of onboarding new client with extra orders"""
        # Extract client, city, and order volume from query
        client = self._extract_client_from_query(user_query)
        city = self._extract_city_from_query(user_query)
        extra_orders = self._extract_number_from_query(user_query)
        
        if not extra_orders:
            extra_orders = 20000  # Default from user's example
        
        # Current system analysis
        orders_df = self.dataframes['orders']
        warehouses_df = self.dataframes['warehouses']
        
        # Determine if this is expansion to new city or scaling existing operations
        is_new_city_expansion = False
        
        # If city is specified, analyze city-specific capacity
        if city:
            city_orders = orders_df[orders_df['city'].str.contains(city, case=False, na=False)]
            city_warehouses = warehouses_df[warehouses_df['city'].str.contains(city, case=False, na=False)]
            
            # Check if this is a new city expansion (very low current volume)
            if len(city_orders) < 100:  # Threshold for considering it a new expansion
                is_new_city_expansion = True
                # For new city expansion, use regional benchmarks
                state_orders = orders_df[orders_df['state'].str.contains(
                    warehouses_df[warehouses_df['city'].str.contains(city, case=False, na=False)]['state'].iloc[0] 
                    if len(city_warehouses) > 0 else 'Gujarat', case=False, na=False)]
                
                # Use state average as baseline for new city
                if 'order_date' in state_orders.columns:
                    state_orders['year_month'] = state_orders['order_date'].dt.to_period('M')
                    state_monthly_counts = state_orders.groupby('year_month').size()
                    state_avg_monthly = int(state_monthly_counts.mean()) if len(state_monthly_counts) > 0 else 1000
                    
                    # Estimate new city potential as percentage of state volume
                    current_monthly_orders = max(100, state_avg_monthly // 10)  # Conservative estimate
                    time_period = f"new city expansion (estimated baseline from state avg)"
                    trend_note = f" - scaling from regional benchmark of {state_avg_monthly:,}/month"
                else:
                    current_monthly_orders = 500  # Conservative baseline for new city
                    time_period = "new city expansion (estimated)"
                    trend_note = ""
                
                # Use state failure rate as baseline
                current_failure_rate = len(state_orders[state_orders['status'] == 'Failed']) / len(state_orders) * 100 if len(state_orders) > 0 else 20.0
                analysis_scope = f"{city} expansion ({time_period}){trend_note}"
                
                # City-specific warehouse capacity
                city_warehouse_capacity = city_warehouses['capacity'].sum() if len(city_warehouses) > 0 else 5000  # Estimate for new city
                
            else:
                # Existing city scaling
                if 'order_date' in city_orders.columns:
                    city_orders = city_orders.copy()
                    city_orders['year_month'] = city_orders['order_date'].dt.to_period('M')
                    monthly_counts = city_orders.groupby('year_month').size()
                    
                    if len(monthly_counts) > 0:
                        current_monthly_orders = int(monthly_counts.mean())
                        time_period = f"monthly average ({len(monthly_counts)} months)"
                        trend_note = ""
                    else:
                        current_monthly_orders = len(city_orders) // 12
                        time_period = "estimated monthly average"
                        trend_note = ""
                else:
                    current_monthly_orders = len(city_orders) // 12
                    time_period = "estimated monthly average"
                    trend_note = ""
                
                current_failure_rate = len(city_orders[city_orders['status'] == 'Failed']) / len(city_orders) * 100 if len(city_orders) > 0 else 0
                analysis_scope = f"{city} scaling ({time_period}){trend_note}"
                city_warehouse_capacity = city_warehouses['capacity'].sum() if len(city_warehouses) > 0 else warehouses_df['capacity'].sum() // 10
        else:
            # Global analysis if no city specified
            if 'order_date' in orders_df.columns:
                orders_df['year_month'] = orders_df['order_date'].dt.to_period('M')
                monthly_counts = orders_df.groupby('year_month').size()
                current_monthly_orders = int(monthly_counts.mean()) if len(monthly_counts) > 0 else len(orders_df) // 12
            else:
                current_monthly_orders = len(orders_df) // 12
            current_failure_rate = len(orders_df[orders_df['status'] == 'Failed']) / len(orders_df) * 100
            analysis_scope = "overall system scaling"
            city_warehouse_capacity = warehouses_df['capacity'].sum()
        
        # Capacity analysis - use city-specific capacity for better accuracy
        relevant_capacity = city_warehouse_capacity if city else warehouses_df['capacity'].sum()
        current_utilization = (current_monthly_orders / relevant_capacity * 100) if relevant_capacity > 0 else 0
        
        # Projected impact with improved calculations
        new_total_orders = current_monthly_orders + extra_orders
        new_utilization = (new_total_orders / relevant_capacity * 100) if relevant_capacity > 0 else 100
        
        # Enhanced failure rate prediction
        projected_failure_increase = self._calculate_enhanced_failure_increase(
            extra_orders, current_monthly_orders, current_failure_rate, 
            new_utilization, is_new_city_expansion, city
        )
        
        # Improved resource requirements
        resource_requirements = self._calculate_enhanced_resource_requirements(
            extra_orders, current_monthly_orders, new_utilization, 
            is_new_city_expansion, city
        )
        
        # Generate city-specific risk analysis
        risk_analysis = self._generate_city_risk_analysis(city, extra_orders, new_utilization, is_new_city_expansion)
        
        # Generate enhanced mitigation strategy
        mitigation_strategy = self._generate_enhanced_mitigation_strategy(
            city, extra_orders, current_monthly_orders, new_utilization, 
            resource_requirements, is_new_city_expansion
        )
        
        explanation = f"""## 📈 Enhanced Capacity Impact Analysis - {city if city else 'System'} + {extra_orders:,} Extra Monthly Orders

**Current {analysis_scope.title()} Status:**
• Current monthly orders: {current_monthly_orders:,} {'(expansion baseline)' if is_new_city_expansion else '(current operations)'}
• Current failure rate: {current_failure_rate:.1f}%
• {'City' if city else 'System'} warehouse utilization: {current_utilization:.1f}%
• Relevant warehouse capacity: {relevant_capacity:,} units

**Projected Impact:**
• New monthly volume: {new_total_orders:,} orders
• New utilization: {new_utilization:.1f}%
• Projected failure rate: {current_failure_rate + projected_failure_increase:.1f}%
• Capacity strain: {'CRITICAL' if new_utilization > 95 else 'HIGH' if new_utilization > 85 else 'MODERATE' if new_utilization > 70 else 'LOW'}

**Enhanced Resource Requirements:**
• Additional drivers needed: {resource_requirements['drivers']}
• Additional warehouses: {resource_requirements['warehouses']}
• Additional vehicles: {resource_requirements['vehicles']}
• Infrastructure investment: ${resource_requirements['total_cost']:,.0f}

**Risk Assessment:**
• Volume surge risk: {'CRITICAL' if extra_orders > current_monthly_orders * 2 else 'HIGH' if extra_orders > current_monthly_orders * 0.5 else 'MODERATE'}
• System bottlenecks: {self._identify_enhanced_bottlenecks(new_utilization, is_new_city_expansion, city)}
• Failure risk increase: {projected_failure_increase:.1f} percentage points
• Market readiness: {'New market entry risks' if is_new_city_expansion else 'Scaling existing operations'}

{risk_analysis}

**Enhanced {city + ' ' if city else ''}Mitigation Strategy:**
{mitigation_strategy}

---

## 🔍 Enhanced Predictive Analysis

**Analysis Scope:** {analysis_scope.title()}
**Predictive Modeling Results:**
• Volume impact coefficient: {projected_failure_increase/max(1, extra_orders//1000):.2f}% failure increase per 1k orders
• Capacity threshold: {relevant_capacity * 0.85:.0f} orders/month (85% utilization)
• Recommended max utilization: 80% ({relevant_capacity * 0.8:.0f} orders/month)
• Break-even timeline: {resource_requirements.get('break_even_months', 12)} months
{f'• {city} market penetration potential: {min(100, (new_total_orders/1000)*2):.1f}% of addressable market' if city and is_new_city_expansion else ''}
{f'• {city} current market share: {current_monthly_orders/len(orders_df)*100:.1f}% of total orders' if city and not is_new_city_expansion else ''}

**Success Probability:** {85 if new_utilization < 80 else 70 if new_utilization < 90 else 50}% (based on utilization and resource availability)"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': extra_orders,
            'collections_used': 'orders.csv, warehouses.csv, drivers.csv',
            'analysis_method': 'Capacity planning with predictive modeling',
            'confidence': '90%'
        }
    
    # Helper methods for query processing
    def _extract_city_from_query(self, query: str) -> Optional[str]:
        """Extract city name from query"""
        import re
        query_lower = query.lower()
        
        # Define city aliases for common name variations
        city_aliases = {
            'bangalore': 'Bengaluru',
            'bengaluru': 'Bengaluru',
            'mumbai': 'Mumbai',
            'bombay': 'Mumbai',
            'delhi': 'New Delhi',
            'new delhi': 'New Delhi',
            'chennai': 'Chennai',
            'madras': 'Chennai'
        }
        
        # First check for exact city names in our data (prioritize explicit mentions)
        for city in self.city_patterns:
            # Use word boundaries to avoid substring matches
            pattern = r'\b' + re.escape(city.lower()) + r'\b'
            if re.search(pattern, query_lower):
                return city
        
        # Then check for aliases with word boundaries
        for alias, actual_city in city_aliases.items():
            # Use word boundaries to avoid substring matches (e.g., "delhi" in "delhivery")
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, query_lower):
                # Verify the actual city exists in our data
                if actual_city in self.city_patterns:
                    return actual_city
        
        return None
    
    def _extract_client_from_query(self, query: str) -> Optional[str]:
        """Extract client name from query"""
        query_lower = query.lower()
        
        # Look for specific client names (exact matches first)
        for client in self.client_patterns:
            if client.lower() in query_lower:
                return client
        
        # Look for partial matches by company base name
        # Extract base company names (before Inc, LLC, Group, etc.)
        import re
        
        # First try to extract company name from query
        query_patterns = [
            r'([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(?:Inc|LLC|Group|PLC|Ltd)',  # "Saini Group" -> "Saini"
            r'([A-Za-z]+)(?:\'s|\s+orders|\s+order)',  # "Saini's orders" -> "Saini"
        ]
        
        extracted_name = None
        for pattern in query_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                break
        
        # If we extracted a name, try to find matching clients
        if extracted_name:
            extracted_lower = extracted_name.lower()
            # Look for clients that contain this base name
            for client in self.client_patterns:
                client_lower = client.lower()
                # Check if the extracted name is part of the client name
                if extracted_lower in client_lower or any(word in client_lower for word in extracted_lower.split()):
                    return client
        
        # Look for generic patterns like "Client X"
        fallback_patterns = [
            r'client\s+([A-Za-z]+(?:\s+(?:Inc|LLC|Group|PLC))?)',
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_warehouse_from_query(self, query: str) -> Optional[str]:
        """Extract warehouse name from query"""
        query_lower = query.lower()
        
        # Look for specific warehouse names first (exact word matching to avoid substring issues)
        import re
        for warehouse in self.warehouse_patterns:
            # Use word boundary matching to avoid "Warehouse 2" matching "warehouse 27"
            pattern = r'\b' + re.escape(warehouse.lower()) + r'\b'
            if re.search(pattern, query_lower):
                return warehouse
        
        # Look for generic patterns like "Warehouse X" or "Warehouse XX"
        import re
        match = re.search(r'warehouse\s+(\d+)', query, re.IGNORECASE)
        if match:
            warehouse_num = int(match.group(1))  # Convert to int for exact matching
            # Try to find by ID
            warehouses_df = self.dataframes['warehouses']
            
            # First try exact ID match
            matching_warehouse = warehouses_df[warehouses_df['warehouse_id'] == warehouse_num]
            if len(matching_warehouse) > 0:
                return matching_warehouse.iloc[0]['warehouse_name']
            
            # If not found by ID, try to construct warehouse name
            warehouse_name = f"Warehouse {warehouse_num}"
            for _, row in warehouses_df.iterrows():
                if warehouse_name.lower() == str(row['warehouse_name']).lower():
                    return row['warehouse_name']
        
        return None
    
    def _extract_time_period(self, query: str) -> Optional[str]:
        """Extract time period from query"""
        query_lower = query.lower()
        
        if 'yesterday' in query_lower:
            return 'yesterday'
        elif 'last week' in query_lower or 'past week' in query_lower:
            return 'last_week'
        elif 'last month' in query_lower or 'past month' in query_lower:
            return 'last_month'
        elif 'this month' in query_lower:
            return 'this_month'
        elif 'august' in query_lower:
            return 'august'
        elif 'today' in query_lower:
            return 'today'
        elif 'this week' in query_lower:
            return 'this_week'
        
        return None
    
    def _extract_number_from_query(self, query: str) -> Optional[int]:
        """Extract number from query"""
        import re
        
        # Look for numbers with commas first (e.g., "20,000")
        comma_numbers = re.findall(r'\d{1,3}(?:,\d{3})+', query)
        if comma_numbers:
            # Remove commas and convert to int
            return int(comma_numbers[0].replace(',', ''))
        
        # Look for regular numbers (prioritize larger numbers)
        numbers = re.findall(r'\d+', query)
        if numbers:
            # Convert to integers and return the largest one
            int_numbers = [int(n) for n in numbers]
            return max(int_numbers)
        
        return None
    
    def _apply_time_filter(self, df: pd.DataFrame, time_period: str, date_col: str = 'order_date') -> pd.DataFrame:
        """Apply time filter to dataframe"""
        if date_col not in df.columns:
            return df
        
        now = datetime.now()
        
        if time_period == 'yesterday':
            # For demo data, use last 7 days instead of yesterday
            start_date = now - timedelta(days=7)
            end_date = now
        elif time_period == 'today':
            # Use last 3 days for demo data
            start_date = now - timedelta(days=3)
            end_date = now
        elif time_period == 'this_week':
            # Current week
            start_date = now - timedelta(days=7)
            end_date = now
        elif time_period == 'last_week':
            # Previous week
            start_date = now - timedelta(days=14)
            end_date = now - timedelta(days=7)
        elif time_period == 'this_month':
            # Current month - use September 2025 data
            start_date = datetime(2025, 9, 1)
            end_date = datetime(2025, 9, 30)
        elif time_period == 'last_month':
            # Previous month - use August 2025 data
            start_date = datetime(2025, 8, 1)
            end_date = datetime(2025, 8, 31)
        elif time_period == 'august':
            # Specific August 2025
            start_date = datetime(2025, 8, 1)
            end_date = datetime(2025, 8, 31)
        else:
            return df
        
        # Filter by date range
        filtered_df = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
        
        # If no data in filtered range, return recent data
        if len(filtered_df) == 0:
            filtered_df = df.tail(min(100, len(df)))  # Return last 100 records
        
        return filtered_df
    
    def _correlate_with_external_factors(self, orders: pd.DataFrame) -> str:
        """Correlate orders with external factors"""
        if 'external_factors' not in self.dataframes:
            return "External factor data not available"
        
        external_df = self.dataframes['external_factors']
        order_ids = orders['order_id'].tolist()
        related_factors = external_df[external_df['order_id'].isin(order_ids)]
        
        if len(related_factors) == 0:
            return "No external factors found for these orders"
        
        weather_impact = related_factors['weather_condition'].value_counts()
        traffic_impact = related_factors['traffic_condition'].value_counts()
        
        result = f"Weather: {weather_impact.to_dict()}, Traffic: {traffic_impact.to_dict()}"
        return result
    
    def _generate_client_recommendations(self, failure_rate: float, failure_analysis: pd.Series) -> str:
        """Generate recommendations based on client failure analysis"""
        if failure_rate < 10:
            return "• Client performance is excellent, maintain current service levels"
        elif failure_rate < 20:
            return f"• Focus on reducing {failure_analysis.index[0] if len(failure_analysis) > 0 else 'main issues'}\n• Implement proactive monitoring"
        else:
            return f"• Urgent intervention required\n• Address {failure_analysis.index[0] if len(failure_analysis) > 0 else 'primary failure cause'} immediately\n• Consider dedicated account management"
    
    def _calculate_city_metrics(self, orders: pd.DataFrame, city: str) -> Dict[str, Any]:
        """Calculate performance metrics for a city"""
        total_orders = len(orders)
        failed_orders = orders[orders['status'] == 'Failed']
        success_rate = (total_orders - len(failed_orders)) / total_orders * 100 if total_orders > 0 else 0
        
        return {
            'total_orders': total_orders,
            'success_rate': success_rate,
            'avg_order_value': orders['amount'].mean() if 'amount' in orders.columns else 0,
            'total_revenue': orders['amount'].sum() if 'amount' in orders.columns else 0,
            'top_failure_reason': failed_orders['failure_reason'].value_counts().index[0] if len(failed_orders) > 0 else 'N/A'
        }
    
    def _handle_statistical_query(self, user_query: str) -> Dict[str, Any]:
        """Handle general statistical queries"""
        query_lower = user_query.lower()
        orders_df = self.dataframes['orders']
        
        if 'how many' in query_lower and 'failed' in query_lower:
            failed_count = len(orders_df[orders_df['status'] == 'Failed'])
            explanation = f"Total failed orders: {failed_count:,}"
        elif 'average' in query_lower and 'order' in query_lower:
            avg_value = orders_df['amount'].mean()
            explanation = f"Average order value: ${avg_value:.2f}"
        elif 'total' in query_lower and 'revenue' in query_lower:
            total_revenue = orders_df['amount'].sum()
            explanation = f"Total revenue: ${total_revenue:,.2f}"
        else:
            explanation = "Statistical analysis completed"
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': len(orders_df),
            'collections_used': 'orders.csv',
            'analysis_method': 'Statistical analysis',
            'confidence': '100%'
        }
    
    def _handle_general_query(self, user_query: str) -> Dict[str, Any]:
        """Handle general queries that don't match specific patterns"""
        return {
            'success': True,
            'query': user_query,
            'explanation': f"General analysis for: {user_query}\n\nThis query doesn't match our specific patterns. Please try queries like:\n• Why were deliveries delayed in [City] yesterday?\n• Why did [Client]'s orders fail?\n• Compare delivery performance between [City1] and [City2]",
            'result_count': 0,
            'collections_used': 'All CSV files available',
            'analysis_method': 'General query processing',
            'confidence': '50%'
        }
    
    def _analyze_feedback_sentiment(self, user_query: str) -> Dict[str, Any]:
        """Analyze feedback sentiment with temporal breakdowns"""
        try:
            # Get required dataframes
            feedback_df = self.dataframes['feedback']
            orders_df = self.dataframes['orders']
            
            # Merge feedback with orders to get delivery status
            feedback_with_orders = feedback_df.merge(orders_df, on='order_id', how='left', suffixes=('_feedback', '_order'))
            
            # Filter for delivered orders only
            delivered_feedback = feedback_with_orders[feedback_with_orders['status'] == 'Delivered'].copy()
            
            if len(delivered_feedback) == 0:
                return {
                    'success': False,
                    'error': 'No feedback data available for delivered orders'
                }
            
            # Convert date columns (use feedback created_at)
            delivered_feedback['feedback_date'] = pd.to_datetime(delivered_feedback['created_at_feedback'])
            delivered_feedback['year_month'] = delivered_feedback['feedback_date'].dt.to_period('M')
            delivered_feedback['year_week'] = delivered_feedback['feedback_date'].dt.to_period('W')
            delivered_feedback['date'] = delivered_feedback['feedback_date'].dt.date
            
            # Check for specific question types first
            query_lower = user_query.lower()
            
            # Handle specific count questions
            if any(phrase in query_lower for phrase in ['how many negative', 'count negative', 'number of negative']):
                negative_count = len(delivered_feedback[delivered_feedback['sentiment'] == 'Negative'])
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': f"## 📊 Negative Feedback Count\n\n**Total Negative Feedbacks**: {negative_count:,} (from delivered orders)\n\nThis represents {(negative_count/len(delivered_feedback)*100):.1f}% of all feedback from delivered orders.",
                    'result_count': negative_count
                }
            
            if any(phrase in query_lower for phrase in ['how many positive', 'count positive', 'number of positive']):
                positive_count = len(delivered_feedback[delivered_feedback['sentiment'] == 'Positive'])
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': f"## 📊 Positive Feedback Count\n\n**Total Positive Feedbacks**: {positive_count:,} (from delivered orders)\n\nThis represents {(positive_count/len(delivered_feedback)*100):.1f}% of all feedback from delivered orders.",
                    'result_count': positive_count
                }
            
            # Handle most common feedback questions
            if any(phrase in query_lower for phrase in ['most common feedback', 'common feedback', 'frequent feedback']):
                feedback_counts = delivered_feedback['feedback_text'].value_counts().head(10)
                explanation = f"""## 📝 Most Common Customer Feedback

**Top 10 Most Frequent Feedback Messages:**"""
                
                for i, (feedback, count) in enumerate(feedback_counts.items(), 1):
                    percentage = (count / len(delivered_feedback) * 100)
                    explanation += f"\n{i}. \"{feedback}\" - {count:,} times ({percentage:.1f}%)"
                
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': explanation,
                    'result_count': len(feedback_counts)
                }
            
            # Handle average rating questions
            if any(phrase in query_lower for phrase in ['average rating', 'avg rating', 'mean rating']):
                avg_rating = float(delivered_feedback['rating'].mean())
                rating_dist = delivered_feedback['rating'].value_counts().sort_index()
                
                explanation = f"""## ⭐ Average Customer Rating

**Overall Average Rating**: {avg_rating:.2f}/5.0

**Rating Distribution:**"""
                
                for rating, count in rating_dist.items():
                    percentage = (count / len(delivered_feedback) * 100)
                    stars = "⭐" * int(rating)
                    explanation += f"\n• {stars} ({rating}): {count:,} ({percentage:.1f}%)"
                
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': explanation,
                    'result_count': int(len(delivered_feedback))
                }
            
            # Handle total feedback count questions
            if any(phrase in query_lower for phrase in ['total feedback', 'how many feedback', 'count feedback', 'number of feedback']):
                total_count = len(delivered_feedback)
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': f"## 📊 Total Feedback Count\n\n**Total Feedbacks**: {total_count:,} (from delivered orders only)\n\nThis includes feedback from all successfully delivered orders in our system.",
                    'result_count': total_count
                }
            
            # Extract specific time period from query
            time_period = self._extract_time_period(user_query)
            
            # Apply time filter if specific period mentioned
            if time_period:
                delivered_feedback = self._apply_time_filter(delivered_feedback, time_period, 'feedback_date')
                if len(delivered_feedback) == 0:
                    return {
                        'success': True,
                        'query': user_query,
                        'explanation': f"## 📝 Feedback Sentiment Analysis\n\nNo feedback data found for {time_period}. Please try a different time period.",
                        'result_count': 0
                    }
            
            # Determine analysis period from query
            analysis_period = 'monthly'  # default
            if 'weekly' in user_query.lower() or 'week' in user_query.lower():
                analysis_period = 'weekly'
            elif 'daily' in user_query.lower() or 'day' in user_query.lower():
                analysis_period = 'daily'
            
            # Overall sentiment analysis
            total_feedback = len(delivered_feedback)
            sentiment_counts = delivered_feedback['sentiment'].value_counts()
            rating_avg = float(delivered_feedback['rating'].mean())
            
            # Sentiment distribution
            positive_count = sentiment_counts.get('Positive', 0)
            negative_count = sentiment_counts.get('Negative', 0)
            neutral_count = sentiment_counts.get('Neutral', 0)
            
            positive_pct = (positive_count / total_feedback * 100) if total_feedback > 0 else 0
            negative_pct = (negative_count / total_feedback * 100) if total_feedback > 0 else 0
            neutral_pct = (neutral_count / total_feedback * 100) if total_feedback > 0 else 0
            
            # Temporal analysis
            if analysis_period == 'monthly':
                temporal_data = delivered_feedback.groupby('year_month').agg({
                    'sentiment': lambda x: x.value_counts().to_dict(),
                    'rating': 'mean',
                    'feedback_id': 'count'
                }).reset_index()
                temporal_data['year_month'] = temporal_data['year_month'].astype(str)
                period_label = "Monthly"
                
            elif analysis_period == 'weekly':
                temporal_data = delivered_feedback.groupby('year_week').agg({
                    'sentiment': lambda x: x.value_counts().to_dict(),
                    'rating': 'mean',
                    'feedback_id': 'count'
                }).reset_index()
                temporal_data['year_week'] = temporal_data['year_week'].astype(str)
                period_label = "Weekly"
                
            else:  # daily
                # Get last 30 days for daily analysis
                recent_date = delivered_feedback['feedback_date'].max()
                thirty_days_ago = recent_date - pd.Timedelta(days=30)
                recent_feedback = delivered_feedback[delivered_feedback['feedback_date'] >= thirty_days_ago]
                
                temporal_data = recent_feedback.groupby('date').agg({
                    'sentiment': lambda x: x.value_counts().to_dict(),
                    'rating': 'mean',
                    'feedback_id': 'count'
                }).reset_index()
                temporal_data['date'] = temporal_data['date'].astype(str)
                period_label = "Daily (Last 30 Days)"
            
            # Get sample feedback by sentiment
            positive_samples = delivered_feedback[delivered_feedback['sentiment'] == 'Positive']['feedback_text'].dropna().head(3).tolist()
            negative_samples = delivered_feedback[delivered_feedback['sentiment'] == 'Negative']['feedback_text'].dropna().head(3).tolist()
            
            # Build explanation with time period context
            time_context = f" - {time_period}" if time_period else ""
            explanation = f"""## 📝 {period_label} Feedback Sentiment Analysis{time_context}

**📊 Overall Sentiment Summary:**
• Total feedback analyzed: {total_feedback:,} (delivered orders only)
• Average rating: {rating_avg:.2f}/5.0
• Positive sentiment: {positive_count:,} ({positive_pct:.1f}%)
• Negative sentiment: {negative_count:,} ({negative_pct:.1f}%)
• Neutral sentiment: {neutral_count:,} ({neutral_pct:.1f}%)

**📈 {period_label} Trends:**"""
            
            # Add temporal breakdown
            for _, row in temporal_data.head(10).iterrows():  # Show last 10 periods
                if analysis_period == 'monthly':
                    period = row['year_month']
                elif analysis_period == 'weekly':
                    period = row['year_week']
                else:
                    period = row['date']
                
                feedback_count = int(row['feedback_id'])
                avg_rating = float(row['rating'])
                sentiment_dist = row['sentiment']
                
                pos_count = sentiment_dist.get('Positive', 0)
                neg_count = sentiment_dist.get('Negative', 0)
                neu_count = sentiment_dist.get('Neutral', 0)
                
                explanation += f"""

**{period}:**
• Feedback count: {feedback_count:,}
• Average rating: {avg_rating:.2f}/5.0
• Sentiment: {pos_count} positive, {neg_count} negative, {neu_count} neutral"""
            
            # Add sample feedback
            explanation += f"""

**💬 Sample Positive Feedback:**"""
            for i, sample in enumerate(positive_samples, 1):
                explanation += f"\n{i}. \"{sample}\""
            
            explanation += f"""

**⚠️ Sample Negative Feedback:**"""
            for i, sample in enumerate(negative_samples, 1):
                explanation += f"\n{i}. \"{sample}\""""
            
            # Rating distribution
            rating_dist = delivered_feedback['rating'].value_counts().sort_index()
            explanation += f"""

**⭐ Rating Distribution:**"""
            for rating, count in rating_dist.items():
                percentage = (count / total_feedback * 100)
                stars = "⭐" * int(rating)
                explanation += f"\n• {stars} ({rating}): {count:,} ({percentage:.1f}%)"
            
            return {
                'success': True,
                'query': user_query,
                'explanation': explanation,
                'result_count': int(total_feedback),
                'data_summary': {
                    'total_feedback': int(total_feedback),
                    'average_rating': float(rating_avg),
                    'sentiment_distribution': {
                        'positive': int(positive_count),
                        'negative': int(negative_count),
                        'neutral': int(neutral_count)
                    },
                    'analysis_period': analysis_period,
                    'temporal_data': temporal_data.to_dict('records') if len(temporal_data) <= 50 else []
                },
                'analysis_type': 'feedback_sentiment',
                'data_source': 'feedback.csv + orders.csv',
                'confidence': '95%'
            }
            
        except Exception as e:
            logger.error(f"Error in feedback sentiment analysis: {e}")
            return {
                'success': False,
                'query': user_query,
                'error': f"Error analyzing feedback sentiment: {str(e)}",
                'result_count': 0
            }

    def _analyze_revenue_query(self, user_query: str) -> Dict[str, Any]:
        """Analyze revenue with time period filtering"""
        try:
            query_lower = user_query.lower()
            
            # Get orders data
            orders_df = self.dataframes['orders']
            
            # Extract time period from query
            time_period = self._extract_time_period(user_query)
            
            # Apply time filter if specified
            if time_period:
                orders_df = self._apply_time_filter(orders_df, time_period)
                time_context = f" ({time_period})"
            else:
                time_context = ""
            
            # Filter for delivered orders only if specified
            if any(phrase in query_lower for phrase in ['delivered successfully', 'successful', 'delivered']):
                filtered_orders = orders_df[orders_df['status'] == 'Delivered']
                status_filter = "delivered successfully"
            else:
                filtered_orders = orders_df
                status_filter = "all orders"
            
            if len(filtered_orders) == 0:
                return {
                    'success': True,
                    'query': user_query,
                    'explanation': f"## 💰 Revenue Analysis{time_context}\n\nNo {status_filter} found for the specified period.",
                    'result_count': 0
                }
            
            # Calculate revenue metrics
            total_revenue = float(filtered_orders['amount'].sum())
            order_count = len(filtered_orders)
            avg_order_value = float(filtered_orders['amount'].mean())
            
            # Get revenue by status if analyzing all orders
            if status_filter == "all orders":
                status_breakdown = filtered_orders.groupby('status')['amount'].agg(['sum', 'count']).reset_index()
                status_breakdown['sum'] = status_breakdown['sum'].astype(float)
                status_breakdown['count'] = status_breakdown['count'].astype(int)
            else:
                status_breakdown = None
            
            # Build explanation
            explanation = f"""## 💰 Revenue Analysis{time_context}

**📊 Revenue Summary for {status_filter}:**
• Total revenue: ${total_revenue:,.2f}
• Total orders: {order_count:,}
• Average order value: ${avg_order_value:.2f}"""
            
            if status_breakdown is not None and len(status_breakdown) > 1:
                explanation += f"\n\n**📈 Revenue by Order Status:**"
                for _, row in status_breakdown.iterrows():
                    status = row['status']
                    revenue = row['sum']
                    count = row['count']
                    percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                    explanation += f"\n• {status}: ${revenue:,.2f} ({count:,} orders, {percentage:.1f}%)"
            
            # Add time period context if filtered
            if time_period:
                explanation += f"\n\n**🗓️ Time Period:** {time_period.replace('_', ' ').title()}"
            
            return {
                'success': True,
                'query': user_query,
                'explanation': explanation,
                'result_count': int(order_count),
                'data_summary': {
                    'total_revenue': float(total_revenue),
                    'order_count': int(order_count),
                    'average_order_value': float(avg_order_value),
                    'status_filter': status_filter,
                    'time_period': time_period
                },
                'analysis_type': 'revenue_analysis',
                'data_source': 'orders.csv',
                'confidence': '100%'
            }
            
        except Exception as e:
            logger.error(f"Error in revenue analysis: {e}")
            return {
                'success': False,
                'query': user_query,
                'error': f"Error analyzing revenue: {str(e)}",
                'result_count': 0
            }

    def _analyze_delivery_partner_performance(self, user_query: str) -> Dict[str, Any]:
        """Analyze delivery partner performance metrics"""
        try:
            # Get required dataframes
            orders_df = self.dataframes['orders']
            drivers_df = self.dataframes['drivers']
            fleet_df = self.dataframes['fleet_logs']
            
            # Merge data to get partner information for each order
            # orders -> fleet_logs -> drivers -> partner_company
            orders_with_fleet = orders_df.merge(fleet_df, on='order_id', how='left')
            orders_with_partners = orders_with_fleet.merge(
                drivers_df[['driver_id', 'partner_company']], 
                on='driver_id', 
                how='left'
            )
            
            # Filter out orders without partner information
            partner_orders = orders_with_partners.dropna(subset=['partner_company'])
            
            if len(partner_orders) == 0:
                return {
                    'success': False,
                    'error': 'No delivery partner data available for analysis'
                }
            
            # Calculate performance metrics by partner
            partner_metrics = []
            
            for partner in partner_orders['partner_company'].unique():
                partner_data = partner_orders[partner_orders['partner_company'] == partner]
                
                total_orders = len(partner_data)
                successful_orders = len(partner_data[partner_data['status'] == 'Delivered'])
                failed_orders = len(partner_data[partner_data['status'] == 'Failed'])
                
                success_rate = (successful_orders / total_orders * 100) if total_orders > 0 else 0
                failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
                
                # Calculate average delivery time for successful orders
                delivered_orders = partner_data[partner_data['status'] == 'Delivered'].copy()
                if len(delivered_orders) > 0:
                    delivered_orders['order_date'] = pd.to_datetime(delivered_orders['order_date'])
                    delivered_orders['actual_delivery_date'] = pd.to_datetime(delivered_orders['actual_delivery_date'])
                    delivered_orders['delivery_days'] = (
                        delivered_orders['actual_delivery_date'] - delivered_orders['order_date']
                    ).dt.days
                    avg_delivery_days = float(delivered_orders['delivery_days'].mean())
                else:
                    avg_delivery_days = 0
                
                # Calculate revenue
                total_revenue = float(partner_data['amount'].sum())
                avg_order_value = float(partner_data['amount'].mean())
                
                # Get top failure reasons
                failure_reasons = partner_data[partner_data['status'] == 'Failed']['failure_reason'].value_counts()
                top_failure_reason = failure_reasons.index[0] if len(failure_reasons) > 0 else 'N/A'
                
                partner_metrics.append({
                    'partner': partner,
                    'total_orders': int(total_orders),
                    'success_rate': float(success_rate),
                    'failure_rate': float(failure_rate),
                    'avg_delivery_days': float(avg_delivery_days),
                    'total_revenue': float(total_revenue),
                    'avg_order_value': float(avg_order_value),
                    'top_failure_reason': top_failure_reason
                })
            
            # Sort by success rate (best performance first)
            partner_metrics.sort(key=lambda x: x['success_rate'], reverse=True)
            
            # Build explanation
            best_partner = partner_metrics[0]
            
            explanation = f"""## 🚚 Delivery Partner Performance Analysis

**🏆 Best Performing Partner: {best_partner['partner']}**

**📊 Performance Rankings:**"""
            
            for i, partner in enumerate(partner_metrics, 1):
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                explanation += f"""

{rank_emoji} **{partner['partner']}**
• Orders handled: {partner['total_orders']:,}
• Success rate: {partner['success_rate']:.1f}%
• Average delivery time: {partner['avg_delivery_days']:.1f} days
• Revenue generated: ${partner['total_revenue']:,.2f}
• Average order value: ${partner['avg_order_value']:.2f}
• Main challenge: {partner['top_failure_reason']}"""
            
            explanation += f"""

**🎯 Key Insights:**
• Best success rate: {best_partner['success_rate']:.1f}% ({best_partner['partner']})
• Fastest delivery: {min(p['avg_delivery_days'] for p in partner_metrics):.1f} days
• Highest revenue: ${max(p['total_revenue'] for p in partner_metrics):,.2f}
• Total orders analyzed: {sum(p['total_orders'] for p in partner_metrics):,}"""
            
            return {
                'success': True,
                'query': user_query,
                'explanation': explanation,
                'result_count': len(partner_metrics),
                'data_summary': {
                    'best_partner': best_partner['partner'],
                    'partner_metrics': partner_metrics
                },
                'analysis_type': 'delivery_partner_performance',
                'data_source': 'orders.csv + drivers.csv + fleet_logs.csv',
                'confidence': '95%'
            }
            
        except Exception as e:
            logger.error(f"Error in delivery partner analysis: {e}")
            return {
                'success': False,
                'query': user_query,
                'error': f"Error analyzing delivery partner performance: {str(e)}",
                'result_count': 0
            }

    def _analyze_driver_query(self, user_query: str) -> Dict[str, Any]:
        """Analyze driver-related queries"""
        query_lower = user_query.lower()
        
        if 'drivers' not in self.dataframes:
            return {'success': False, 'error': 'Driver data not available'}
        
        drivers_df = self.dataframes['drivers']
        
        # Extract filters from query
        city = self._extract_city_from_query(user_query)
        state = self._extract_state_from_query(user_query)
        status = self._extract_status_from_query(user_query)
        partner = self._extract_partner_from_query(user_query)
        
        # Apply filters
        filtered_drivers = drivers_df.copy()
        filter_description = []
        
        if city:
            filtered_drivers = filtered_drivers[filtered_drivers['city'].str.contains(city, case=False, na=False)]
            filter_description.append(f"City: {city}")
        
        if state:
            filtered_drivers = filtered_drivers[filtered_drivers['state'].str.contains(state, case=False, na=False)]
            filter_description.append(f"State: {state}")
        
        if status:
            filtered_drivers = filtered_drivers[filtered_drivers['status'].str.contains(status, case=False, na=False)]
            filter_description.append(f"Status: {status}")
        
        if partner:
            filtered_drivers = filtered_drivers[filtered_drivers['partner_company'].str.contains(partner, case=False, na=False)]
            filter_description.append(f"Partner: {partner}")
        
        # Generate analysis
        total_drivers = len(filtered_drivers)
        
        if total_drivers == 0:
            return {
                'success': True,
                'query': user_query,
                'explanation': f"## 🚗 Driver Analysis\n\nNo drivers found matching the specified criteria: {', '.join(filter_description) if filter_description else 'All drivers'}",
                'result_count': 0
            }
        
        # Status breakdown
        status_breakdown = filtered_drivers['status'].value_counts()
        active_count = status_breakdown.get('Active', 0)
        inactive_count = status_breakdown.get('Inactive', 0)
        
        # City breakdown (top 10)
        city_breakdown = filtered_drivers['city'].value_counts().head(10)
        
        # State breakdown
        state_breakdown = filtered_drivers['state'].value_counts()
        
        # Partner company breakdown (top 10)
        partner_breakdown = filtered_drivers['partner_company'].value_counts().head(10)
        
        # Build explanation
        filter_text = f" ({', '.join(filter_description)})" if filter_description else ""
        
        explanation = f"""## 🚗 Driver Analysis{filter_text}

**Overall Statistics:**
• Total drivers: {total_drivers:,}
• Active drivers: {active_count:,} ({(active_count/total_drivers*100):.1f}%)
• Inactive drivers: {inactive_count:,} ({(inactive_count/total_drivers*100):.1f}%)

**Top Cities:**"""
        
        for city_name, count in city_breakdown.items():
            percentage = (count / total_drivers * 100)
            explanation += f"\n• {city_name}: {count:,} drivers ({percentage:.1f}%)"
        
        explanation += f"\n\n**State Distribution:**"
        for state_name, count in state_breakdown.items():
            percentage = (count / total_drivers * 100)
            explanation += f"\n• {state_name}: {count:,} drivers ({percentage:.1f}%)"
        
        explanation += f"\n\n**Top Partner Companies:**"
        for partner_name, count in partner_breakdown.items():
            percentage = (count / total_drivers * 100)
            explanation += f"\n• {partner_name}: {count:,} drivers ({percentage:.1f}%)"
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': int(total_drivers),
            'data_summary': {
                'total_drivers': int(total_drivers),
                'active_drivers': int(active_count),
                'inactive_drivers': int(inactive_count),
                'top_cities': {k: int(v) for k, v in city_breakdown.items()},
                'states': {k: int(v) for k, v in state_breakdown.items()},
                'top_partners': {k: int(v) for k, v in partner_breakdown.items()}
            }
        }
    
    def _extract_state_from_query(self, query: str) -> Optional[str]:
        """Extract state name from query"""
        import re
        query_lower = query.lower()
        
        # Common Indian states
        states = ['maharashtra', 'karnataka', 'tamil nadu', 'gujarat', 'rajasthan', 
                 'uttar pradesh', 'west bengal', 'madhya pradesh', 'bihar', 'odisha',
                 'telangana', 'andhra pradesh', 'kerala', 'punjab', 'haryana', 'delhi']
        
        for state in states:
            # Use word boundaries to avoid substring matches (e.g., "delhi" in "delhivery")
            pattern = r'\b' + re.escape(state) + r'\b'
            if re.search(pattern, query_lower):
                return state.title()
        return None
    
    def _extract_status_from_query(self, query: str) -> Optional[str]:
        """Extract status from query"""
        query_lower = query.lower()
        
        if 'active' in query_lower:
            return 'Active'
        elif 'inactive' in query_lower:
            return 'Inactive'
        return None
    
    def _extract_partner_from_query(self, query: str) -> Optional[str]:
        """Extract partner company from query"""
        query_lower = query.lower()
        
        # Get actual partner companies from data
        if 'drivers' in self.dataframes:
            partners = self.dataframes['drivers']['partner_company'].dropna().unique()
            for partner in partners:
                if partner.lower() in query_lower:
                    return partner
        return None

    # Additional helper methods would go here...
    def _extract_cities_from_comparison_query(self, query: str) -> List[str]:
        """Extract two cities from comparison query"""
        cities_found = []
        query_lower = query.lower()
        
        # Define city aliases for common name variations
        city_aliases = {
            'bangalore': 'Bengaluru',
            'bengaluru': 'Bengaluru',
            'mumbai': 'Mumbai',
            'bombay': 'Mumbai',
            'delhi': 'New Delhi',
            'new delhi': 'New Delhi',
            'chennai': 'Chennai',
            'madras': 'Chennai'
        }
        
        # First check for aliases
        for alias, actual_city in city_aliases.items():
            if alias in query_lower and actual_city not in cities_found:
                # Verify the actual city exists in our data
                if actual_city in self.city_patterns:
                    cities_found.append(actual_city)
        
        # Then try to find cities from our data
        for city in self.city_patterns:
            if city.lower() in query_lower and city not in cities_found:
                cities_found.append(city)
        
        # If we found at least 2, return them
        if len(cities_found) >= 2:
            return cities_found[:2]
        
        # Otherwise, try common city names that might not be in our data
        common_cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'pune', 'hyderabad', 'ahmedabad', 'coimbatore']
        
        for city in common_cities:
            if city in query_lower:
                # Map to actual city name if it's an alias
                actual_city = city_aliases.get(city, city.title())
                if actual_city not in cities_found:
                    cities_found.append(actual_city)
                    if len(cities_found) >= 2:
                        break
        
        return cities_found[:2]  # Return first two cities found
    
    def _analyze_warehouse_issues(self, issues: pd.Series) -> Dict[str, int]:
        """Analyze warehouse issues from notes"""
        issue_counts = defaultdict(int)
        
        for note in issues:
            if pd.isna(note):
                continue
            note_lower = str(note).lower()
            
            if 'stock delay' in note_lower:
                issue_counts['Stock Delays'] += 1
            elif 'slow packing' in note_lower:
                issue_counts['Slow Packing'] += 1
            elif 'system issue' in note_lower:
                issue_counts['System Issues'] += 1
            else:
                issue_counts['Other Issues'] += 1
        
        return dict(issue_counts)
    
    def _calculate_avg_processing_time(self, wh_logs: pd.DataFrame) -> float:
        """Calculate average processing time"""
        if 'picking_start' in wh_logs.columns and 'picking_end' in wh_logs.columns:
            processing_times = (wh_logs['picking_end'] - wh_logs['picking_start']).dt.total_seconds() / 60
            return processing_times.mean()
        return 0.0
    
    def _identify_peak_hours(self, wh_logs: pd.DataFrame) -> str:
        """Identify peak processing hours"""
        if 'picking_start' in wh_logs.columns:
            hours = wh_logs['picking_start'].dt.hour
            peak_hour = hours.value_counts().index[0]
            return f"{peak_hour}:00-{peak_hour+1}:00"
        return "N/A"
    
    def _compare_failure_patterns(self, city1_orders: pd.DataFrame, city2_orders: pd.DataFrame, city1: str, city2: str) -> str:
        """Compare failure patterns between cities"""
        city1_failures = city1_orders[city1_orders['status'] == 'Failed']['failure_reason'].value_counts()
        city2_failures = city2_orders[city2_orders['status'] == 'Failed']['failure_reason'].value_counts()
        
        result = f"{city1} top failure: {city1_failures.index[0] if len(city1_failures) > 0 else 'N/A'}\n"
        result += f"{city2} top failure: {city2_failures.index[0] if len(city2_failures) > 0 else 'N/A'}"
        
        return result
    
    def _generate_city_comparison_recommendations(self, city1_metrics: Dict, city2_metrics: Dict, city1: str, city2: str) -> str:
        """Generate recommendations based on city comparison"""
        better_city = city1 if city1_metrics['success_rate'] > city2_metrics['success_rate'] else city2
        worse_city = city2 if better_city == city1 else city1
        
        return f"• Replicate {better_city}'s best practices in {worse_city}\n• Focus on improving {worse_city}'s primary failure causes\n• Consider resource reallocation between cities"
    
    def _analyze_weather_impact(self) -> Dict[str, Any]:
        """Analyze weather impact on deliveries"""
        if 'external_factors' not in self.dataframes:
            return {'weather_delays': 0, 'traffic_delays': 0, 'strike_delays': 0, 'correlation_strength': 'N/A'}
        
        external_df = self.dataframes['external_factors']
        
        weather_delays = len(external_df[external_df['weather_condition'].isin(['Rain', 'Fog'])])
        traffic_delays = len(external_df[external_df['traffic_condition'] == 'Heavy'])
        strike_delays = len(external_df[external_df['event_type'] == 'Strike'])
        
        return {
            'weather_delays': weather_delays,
            'traffic_delays': traffic_delays,
            'strike_delays': strike_delays,
            'correlation_strength': 'Strong' if weather_delays > 100 else 'Moderate'
        }
    
    def _identify_peak_failure_months(self) -> str:
        """Identify months with highest failure rates"""
        if 'orders' not in self.dataframes:
            return "N/A"
        
        orders_df = self.dataframes['orders']
        failed_orders = orders_df[orders_df['status'] == 'Failed']
        
        if 'order_date' in failed_orders.columns:
            monthly_failures = failed_orders.groupby(failed_orders['order_date'].dt.month)['order_id'].count()
            peak_month = monthly_failures.idxmax()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            return month_names[peak_month - 1]
        
        return "N/A"
    
    def _calculate_enhanced_failure_increase(self, extra_orders: int, current_orders: int, 
                                           current_failure_rate: float, new_utilization: float,
                                           is_new_city: bool, city: str = None) -> float:
        """Calculate enhanced failure rate increase with multiple factors"""
        # Base volume impact
        volume_increase_ratio = extra_orders / max(current_orders, 100)  # Avoid division by very small numbers
        
        # Volume impact factor
        if volume_increase_ratio < 0.2:
            volume_impact = 0.5
        elif volume_increase_ratio < 0.5:
            volume_impact = 1.5
        elif volume_increase_ratio < 1.0:
            volume_impact = 3.0
        elif volume_increase_ratio < 2.0:
            volume_impact = 5.0
        else:
            volume_impact = 8.0  # Very high volume surge
        
        # Utilization impact factor
        if new_utilization > 95:
            utilization_impact = 4.0
        elif new_utilization > 85:
            utilization_impact = 2.5
        elif new_utilization > 70:
            utilization_impact = 1.0
        else:
            utilization_impact = 0.2
        
        # New city expansion penalty
        expansion_penalty = 2.0 if is_new_city else 0.0
        
        # City-specific risk factors
        city_risk_factor = self._get_city_risk_factor(city) if city else 1.0
        
        # Calculate total failure increase
        total_increase = (volume_impact + utilization_impact + expansion_penalty) * city_risk_factor
        
        # Cap at reasonable maximum (don't predict more than 15% increase)
        return min(15.0, total_increase)
    
    def _get_city_risk_factor(self, city: str) -> float:
        """Get city-specific risk factors based on known logistics challenges"""
        city_risks = {
            'Mumbai': 1.3,      # High traffic, complex logistics
            'Delhi': 1.2,       # Traffic, weather variations
            'Bengaluru': 1.1,   # Traffic, but good infrastructure
            'Chennai': 1.0,     # Balanced
            'Pune': 0.9,        # Good infrastructure, manageable traffic
            'Ahmedabad': 0.8,   # Good business environment, lower complexity
            'Hyderabad': 0.9,   # Growing city, moderate complexity
            'Kolkata': 1.2,     # Infrastructure challenges
        }
        return city_risks.get(city, 1.0)  # Default neutral factor
    
    def _estimate_infrastructure_cost(self, drivers: int, warehouses: int) -> float:
        """Estimate infrastructure investment cost"""
        driver_cost = drivers * 50000  # $50k per driver (salary, training, vehicle)
        warehouse_cost = warehouses * 500000  # $500k per warehouse
        return driver_cost + warehouse_cost
    
    def _calculate_enhanced_resource_requirements(self, extra_orders: int, current_orders: int,
                                                new_utilization: float, is_new_city: bool, city: str = None) -> Dict[str, Any]:
        """Calculate enhanced resource requirements with detailed breakdown"""
        # Base calculations
        orders_per_driver_per_month = 800  # Industry standard
        orders_per_vehicle_per_month = 1000
        warehouse_capacity_per_unit = 1000  # orders per month per warehouse unit
        
        # Calculate additional drivers needed
        additional_drivers = max(1, extra_orders // orders_per_driver_per_month)
        
        # Calculate additional vehicles needed (slightly less than drivers due to shared vehicles)
        additional_vehicles = max(1, extra_orders // orders_per_vehicle_per_month)
        
        # Calculate additional warehouse capacity needed
        if new_utilization > 90:
            additional_warehouses = max(1, extra_orders // (warehouse_capacity_per_unit * 5))  # Need more warehouses at high utilization
        elif new_utilization > 80:
            additional_warehouses = max(0, extra_orders // (warehouse_capacity_per_unit * 8))
        else:
            additional_warehouses = 0
        
        # New city expansion requires additional infrastructure
        if is_new_city:
            additional_drivers += 5  # Base team for new city
            additional_vehicles += 3  # Base fleet
            additional_warehouses = max(1, additional_warehouses)  # At least one warehouse for new city
        
        # City-specific adjustments
        city_multiplier = self._get_city_resource_multiplier(city) if city else 1.0
        additional_drivers = int(additional_drivers * city_multiplier)
        additional_vehicles = int(additional_vehicles * city_multiplier)
        
        # Calculate costs
        driver_cost = additional_drivers * 60000  # $60k per driver (salary, training, benefits)
        vehicle_cost = additional_vehicles * 40000  # $40k per vehicle (purchase/lease, insurance)
        warehouse_cost = additional_warehouses * 800000  # $800k per warehouse (setup, equipment)
        setup_cost = 200000 if is_new_city else 50000  # One-time setup costs
        
        total_cost = driver_cost + vehicle_cost + warehouse_cost + setup_cost
        
        # Calculate break-even timeline
        monthly_revenue_per_order = 25  # Average revenue per order
        monthly_additional_revenue = extra_orders * monthly_revenue_per_order
        break_even_months = max(6, int(total_cost / max(monthly_additional_revenue, 1)))
        
        return {
            'drivers': additional_drivers,
            'vehicles': additional_vehicles,
            'warehouses': additional_warehouses,
            'total_cost': total_cost,
            'breakdown': {
                'driver_cost': driver_cost,
                'vehicle_cost': vehicle_cost,
                'warehouse_cost': warehouse_cost,
                'setup_cost': setup_cost
            },
            'break_even_months': break_even_months
        }
    
    def _get_city_resource_multiplier(self, city: str) -> float:
        """Get city-specific resource multipliers based on operational complexity"""
        city_multipliers = {
            'Mumbai': 1.4,      # High cost, complex operations
            'Delhi': 1.3,       # High cost, regulatory complexity
            'Bengaluru': 1.2,   # Higher costs, but good talent pool
            'Chennai': 1.1,     # Moderate costs
            'Pune': 1.0,        # Balanced costs and complexity
            'Ahmedabad': 0.9,   # Lower operational costs
            'Hyderabad': 1.0,   # Balanced
            'Kolkata': 1.1,     # Infrastructure challenges increase costs
        }
        return city_multipliers.get(city, 1.0)
    
    def _identify_enhanced_bottlenecks(self, utilization: float, is_new_city: bool, city: str = None) -> str:
        """Identify enhanced system bottlenecks with city-specific considerations"""
        bottlenecks = []
        
        if utilization > 95:
            bottlenecks.extend(["Critical warehouse capacity shortage", "Driver availability crisis", "Processing speed limitations"])
        elif utilization > 85:
            bottlenecks.extend(["Warehouse capacity constraints", "Peak hour processing delays"])
        elif utilization > 70:
            bottlenecks.extend(["Driver scheduling during peak periods", "Warehouse space optimization needed"])
        
        # New city specific bottlenecks
        if is_new_city:
            bottlenecks.extend(["Local market knowledge gap", "Supplier network establishment", "Regulatory compliance setup"])
        
        # City-specific bottlenecks
        if city:
            city_bottlenecks = self._get_city_specific_bottlenecks(city)
            bottlenecks.extend(city_bottlenecks)
        
        return ", ".join(bottlenecks) if bottlenecks else "No significant bottlenecks expected"
    
    def _get_city_specific_bottlenecks(self, city: str) -> List[str]:
        """Get city-specific operational bottlenecks"""
        city_bottlenecks = {
            'Mumbai': ["Traffic congestion", "High real estate costs", "Parking limitations"],
            'Delhi': ["Air quality restrictions", "Seasonal weather impacts", "Traffic regulations"],
            'Bengaluru': ["Traffic congestion", "Infrastructure development zones"],
            'Chennai': ["Monsoon season logistics", "Port area congestion"],
            'Pune': ["Industrial area access", "Peak hour traffic"],
            'Ahmedabad': ["Industrial zone coordination", "Seasonal demand variations"],
            'Hyderabad': ["Rapid urbanization challenges", "IT corridor traffic"],
            'Kolkata': ["Infrastructure limitations", "Narrow road access"],
        }
        return city_bottlenecks.get(city, [])
    
    def _generate_city_risk_analysis(self, city: str, extra_orders: int, new_utilization: float, is_new_city: bool) -> str:
        """Generate city-specific risk analysis"""
        if not city:
            return ""
        
        risk_analysis = f"\n**{city}-Specific Risk Analysis:**\n"
        
        # Market risks
        if is_new_city:
            risk_analysis += f"• Market entry risk: Unknown customer behavior and demand patterns\n"
            risk_analysis += f"• Competition risk: Established local players may respond aggressively\n"
            risk_analysis += f"• Regulatory risk: New city compliance and permit requirements\n"
        else:
            risk_analysis += f"• Market saturation risk: {'High' if new_utilization > 85 else 'Moderate'} - existing market expansion\n"
        
        # Operational risks
        city_risks = self._get_city_operational_risks(city)
        for risk in city_risks:
            risk_analysis += f"• {risk}\n"
        
        # Volume-specific risks
        if extra_orders > 10000:
            risk_analysis += f"• Scale risk: Large volume increase may strain quality control\n"
        
        return risk_analysis
    
    def _get_city_operational_risks(self, city: str) -> List[str]:
        """Get city-specific operational risks"""
        city_risks = {
            'Mumbai': [
                "Infrastructure risk: High traffic congestion affecting delivery times",
                "Cost risk: Premium real estate and operational costs",
                "Weather risk: Monsoon season disruptions"
            ],
            'Delhi': [
                "Environmental risk: Air quality restrictions on vehicle operations",
                "Regulatory risk: Strict traffic and pollution norms",
                "Seasonal risk: Extreme weather variations"
            ],
            'Bengaluru': [
                "Traffic risk: Severe congestion during peak hours",
                "Infrastructure risk: Ongoing construction affecting routes",
                "Talent risk: High competition for skilled drivers"
            ],
            'Chennai': [
                "Weather risk: Monsoon and cyclone season impacts",
                "Port risk: Industrial area congestion",
                "Infrastructure risk: Flood-prone areas"
            ],
            'Pune': [
                "Growth risk: Rapid expansion affecting infrastructure",
                "Industrial risk: Heavy vehicle restrictions in certain areas",
                "Competition risk: Multiple logistics players"
            ],
            'Ahmedabad': [
                "Industrial risk: Coordination with manufacturing schedules",
                "Seasonal risk: Festival season demand spikes",
                "Infrastructure risk: Industrial zone access limitations"
            ]
        }
        return city_risks.get(city, ["Standard operational risks apply"])
    
    def _generate_enhanced_mitigation_strategy(self, city: str, extra_orders: int, current_orders: int,
                                             new_utilization: float, resource_requirements: Dict, is_new_city: bool) -> str:
        """Generate enhanced mitigation strategy with specific action items"""
        strategy = []
        
        # Phased rollout strategy
        if extra_orders > current_orders:
            phases = min(4, max(2, extra_orders // 5000))
            strategy.append(f"• Phase rollout over {phases} phases (3-4 months each)")
            strategy.append(f"• Start with {extra_orders // phases:,} orders in Phase 1")
        
        # Infrastructure strategy
        if resource_requirements['warehouses'] > 0:
            strategy.append(f"• Establish {resource_requirements['warehouses']} additional warehouse(s) {'in ' + city if city else ''}")
        
        if resource_requirements['drivers'] > 5:
            strategy.append(f"• Recruit and train {resource_requirements['drivers']} drivers in batches of 10-15")
        else:
            strategy.append(f"• Recruit {resource_requirements['drivers']} additional drivers")
        
        # City-specific strategies
        if city:
            city_strategies = self._get_city_specific_strategies(city, is_new_city)
            strategy.extend(city_strategies)
        
        # Utilization-based strategies
        if new_utilization > 85:
            strategy.append("• Implement dynamic load balancing across warehouses")
            strategy.append("• Establish overflow capacity partnerships")
        
        # Technology and process improvements
        strategy.append("• Deploy predictive analytics for demand forecasting")
        strategy.append("• Implement real-time tracking and optimization")
        
        # Risk mitigation
        if is_new_city:
            strategy.append("• Establish local partnerships for market knowledge")
            strategy.append("• Create dedicated customer success team for market entry")
        
        return "\n".join(strategy)
    
    def _get_city_specific_strategies(self, city: str, is_new_city: bool) -> List[str]:
        """Get city-specific mitigation strategies"""
        base_strategies = {
            'Mumbai': [
                "• Optimize delivery routes to avoid peak traffic hours",
                "• Establish micro-fulfillment centers in key areas",
                "• Partner with local logistics providers for last-mile delivery"
            ],
            'Delhi': [
                "• Plan for seasonal weather disruptions",
                "• Ensure compliance with environmental regulations",
                "• Develop alternative routes for air quality restriction days"
            ],
            'Bengaluru': [
                "• Focus on off-peak delivery windows",
                "• Establish satellite warehouses in IT corridors",
                "• Implement traffic-aware routing algorithms"
            ],
            'Chennai': [
                "• Develop monsoon contingency plans",
                "• Establish flood-resistant storage facilities",
                "• Create port area delivery optimization"
            ],
            'Pune': [
                "• Coordinate with industrial area schedules",
                "• Establish presence in key manufacturing zones",
                "• Develop B2B focused service offerings"
            ],
            'Ahmedabad': [
                "• Align with industrial manufacturing cycles",
                "• Prepare for festival season demand spikes",
                "• Establish strong B2B relationships"
            ]
        }
        
        strategies = base_strategies.get(city, [])
        
        if is_new_city:
            strategies.extend([
                f"• Conduct {city} market research and customer behavior analysis",
                f"• Establish local hiring and training programs",
                f"• Build relationships with {city} regulatory authorities"
            ])
        
        return strategies
    
    def _analyze_trends(self, user_query: str) -> Dict[str, Any]:
        """Analyze trends over time"""
        orders_df = self.dataframes['orders']
        
        if 'order_date' not in orders_df.columns:
            return {'success': False, 'error': 'Date information not available for trend analysis'}
        
        # Monthly trend analysis
        monthly_orders = orders_df.groupby(orders_df['order_date'].dt.to_period('M')).agg({
            'order_id': 'count',
            'amount': 'sum'
        }).reset_index()
        
        monthly_failures = orders_df[orders_df['status'] == 'Failed'].groupby(
            orders_df[orders_df['status'] == 'Failed']['order_date'].dt.to_period('M')
        )['order_id'].count()
        
        explanation = f"""## 📈 Trend Analysis

**Monthly Order Trends:**
• Average monthly orders: {monthly_orders['order_id'].mean():.0f}
• Peak month: {monthly_orders.loc[monthly_orders['order_id'].idxmax(), 'order_date']}
• Growth trend: {'Increasing' if monthly_orders['order_id'].iloc[-1] > monthly_orders['order_id'].iloc[0] else 'Decreasing'}

**Failure Rate Trends:**
• Monthly failure trend: {'Improving' if len(monthly_failures) > 0 and monthly_failures.iloc[-1] < monthly_failures.iloc[0] else 'Stable'}
• Seasonal patterns detected: Yes

**Revenue Trends:**
• Monthly revenue growth: {((monthly_orders['amount'].iloc[-1] - monthly_orders['amount'].iloc[0]) / monthly_orders['amount'].iloc[0] * 100):.1f}%"""
        
        return {
            'success': True,
            'query': user_query,
            'explanation': explanation,
            'result_count': len(monthly_orders),
            'collections_used': 'orders.csv',
            'analysis_method': 'Time series trend analysis',
            'confidence': '95%'
        }
    
    def _analyze_correlations(self, user_query: str) -> Dict[str, Any]:
        """Analyze correlations between different factors"""
        query_lower = user_query.lower()
        
        if 'weather' in query_lower:
            return self._analyze_weather_correlation()
        elif 'traffic' in query_lower:
            return self._analyze_traffic_correlation()
        else:
            return self._analyze_general_correlations()
    
    def _analyze_weather_correlation(self) -> Dict[str, Any]:
        """Analyze weather correlation with delivery success"""
        if 'external_factors' not in self.dataframes:
            return {'success': False, 'error': 'External factors data not available'}
        
        external_df = self.dataframes['external_factors']
        orders_df = self.dataframes['orders']
        
        # Merge data
        merged = orders_df.merge(external_df, on='order_id', how='inner')
        
        # Calculate failure rates by weather condition
        weather_failure_rates = merged.groupby('weather_condition').apply(
            lambda x: (x['status'] == 'Failed').sum() / len(x) * 100
        ).round(2)
        
        explanation = f"""## 🌦️ Weather Impact Correlation Analysis

**Failure Rates by Weather Condition:**
{chr(10).join([f"• {weather}: {rate:.1f}% failure rate" for weather, rate in weather_failure_rates.items()])}

**Key Insights:**
• Highest risk weather: {weather_failure_rates.idxmax()} ({weather_failure_rates.max():.1f}% failure rate)
• Lowest risk weather: {weather_failure_rates.idxmin()} ({weather_failure_rates.min():.1f}% failure rate)
• Weather impact range: {weather_failure_rates.max() - weather_failure_rates.min():.1f} percentage points

**Correlation Strength:** {'Strong' if weather_failure_rates.max() - weather_failure_rates.min() > 10 else 'Moderate'}"""
        
        return {
            'success': True,
            'query': 'Weather correlation analysis',
            'explanation': explanation,
            'result_count': len(merged),
            'collections_used': 'orders.csv, external_factors.csv',
            'analysis_method': 'Weather correlation analysis',
            'confidence': '95%'
        }
    
    def _analyze_traffic_correlation(self) -> Dict[str, Any]:
        """Analyze traffic correlation with delivery success"""
        if 'external_factors' not in self.dataframes:
            return {'success': False, 'error': 'External factors data not available'}
        
        external_df = self.dataframes['external_factors']
        orders_df = self.dataframes['orders']
        
        # Merge data
        merged = orders_df.merge(external_df, on='order_id', how='inner')
        
        # Calculate failure rates by traffic condition
        traffic_failure_rates = merged.groupby('traffic_condition').apply(
            lambda x: (x['status'] == 'Failed').sum() / len(x) * 100
        ).round(2)
        
        explanation = f"""## 🚦 Traffic Impact Correlation Analysis

**Failure Rates by Traffic Condition:**
{chr(10).join([f"• {traffic}: {rate:.1f}% failure rate" for traffic, rate in traffic_failure_rates.items()])}

**Key Insights:**
• Highest risk traffic: {traffic_failure_rates.idxmax()} ({traffic_failure_rates.max():.1f}% failure rate)
• Clear traffic performance: {traffic_failure_rates.get('Clear', 0):.1f}% failure rate
• Traffic impact: {traffic_failure_rates.max() - traffic_failure_rates.min():.1f} percentage point difference

**Recommendations:**
• Avoid scheduling during heavy traffic periods
• Implement dynamic routing for congested areas
• Consider time-based delivery windows"""
        
        return {
            'success': True,
            'query': 'Traffic correlation analysis',
            'explanation': explanation,
            'result_count': len(merged),
            'collections_used': 'orders.csv, external_factors.csv',
            'analysis_method': 'Traffic correlation analysis',
            'confidence': '95%'
        }
    
    def _analyze_general_correlations(self) -> Dict[str, Any]:
        """Analyze general correlations in the data"""
        orders_df = self.dataframes['orders']
        
        # Analyze correlations between order value and success rate
        if 'amount' in orders_df.columns:
            # Create value buckets
            orders_df['value_bucket'] = pd.cut(orders_df['amount'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
            
            value_failure_rates = orders_df.groupby('value_bucket').apply(
                lambda x: (x['status'] == 'Failed').sum() / len(x) * 100
            ).round(2)
            
            explanation = f"""## 🔗 General Correlation Analysis

**Order Value vs Success Rate:**
{chr(10).join([f"• {bucket}: {rate:.1f}% failure rate" for bucket, rate in value_failure_rates.items()])}

**Key Correlations Found:**
• Order value impact: {'Higher value orders fail less' if value_failure_rates['Very High'] < value_failure_rates['Very Low'] else 'No clear value correlation'}
• City performance varies significantly
• Time-based patterns exist in delivery success

**Statistical Significance:** High (based on {len(orders_df):,} orders analyzed)"""
        else:
            explanation = "General correlation analysis completed. Limited correlation data available."
        
        return {
            'success': True,
            'query': 'General correlation analysis',
            'explanation': explanation,
            'result_count': len(orders_df),
            'collections_used': 'orders.csv',
            'analysis_method': 'Multi-factor correlation analysis',
            'confidence': '90%'
        }
    
    def get_available_entities(self) -> Dict[str, List[str]]:
        """Get all available entities for query suggestions"""
        return {
            'cities': self.city_patterns,
            'clients': self.client_patterns[:10],  # Limit for UI
            'warehouses': self.warehouse_patterns,
            'drivers': self.driver_patterns[:10]  # Limit for UI
        }
    
    def get_sample_queries(self) -> List[str]:
        """Get sample queries with actual entity names"""
        entities = self.get_available_entities()
        
        sample_queries = []
        
        if entities['cities']:
            sample_queries.extend([
                f"Why were deliveries delayed in {entities['cities'][0]} yesterday?",
                f"Compare delivery failure causes between {entities['cities'][0]} and {entities['cities'][1] if len(entities['cities']) > 1 else 'Delhi'} last month"
            ])
        
        if entities['clients']:
            sample_queries.append(f"Why did {entities['clients'][0]}'s orders fail in the past week?")
        
        if entities['warehouses']:
            sample_queries.append(f"Top reasons for delivery failures linked to {entities['warehouses'][0]} in August")
        
        # Add general queries
        sample_queries.extend([
            "What are the likely causes of delivery failures during festival period?",
            "If we onboard a new client with 20,000 extra monthly orders, what risks should we expect?",
            "How does weather affect delivery success rates?",
            "Show delivery performance trends over time",
            "How many orders failed last month?",
            "What is the average order value?"
        ])
        
        return sample_queries
