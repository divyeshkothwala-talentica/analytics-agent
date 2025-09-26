"""
Data correlation engine for analyzing relationships across collections
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class DataCorrelator:
    """Analyze correlations and relationships across different data collections"""
    
    def __init__(self, db_client):
        """Initialize correlator with database client
        
        Args:
            db_client: MongoDB database client
        """
        self.db = db_client
        self.correlation_cache = {}
        
        # Correlation thresholds
        self.correlation_thresholds = {
            'strong': 0.7,
            'moderate': 0.4,
            'weak': 0.2
        }
        
        logger.info("DataCorrelator initialized")
    
    def analyze_temporal_correlations(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze temporal correlations between events and outcomes
        
        Args:
            time_window_hours: Time window for correlation analysis
            
        Returns:
            Dict with temporal correlation analysis
        """
        logger.info(f"Analyzing temporal correlations with {time_window_hours}h window")
        
        # Get delivery delays and external factors
        delays = self._get_delivery_delays()
        external_factors = self._get_external_factors()
        
        correlations = {
            'weather_delays': self._correlate_weather_delays(delays, external_factors, time_window_hours),
            'traffic_delays': self._correlate_traffic_delays(delays, external_factors, time_window_hours),
            'event_delays': self._correlate_event_delays(delays, external_factors, time_window_hours),
            'time_patterns': self._analyze_time_patterns(delays)
        }
        
        return correlations
    
    def analyze_geographical_correlations(self) -> Dict[str, Any]:
        """Analyze geographical correlations and location-based patterns
        
        Returns:
            Dict with geographical correlation analysis
        """
        logger.info("Analyzing geographical correlations")
        
        # Get location-based data
        city_performance = self._get_city_performance()
        warehouse_efficiency = self._get_warehouse_efficiency()
        route_analysis = self._get_route_analysis()
        
        correlations = {
            'city_failure_rates': self._analyze_city_failure_patterns(city_performance),
            'warehouse_performance': self._analyze_warehouse_correlations(warehouse_efficiency),
            'route_efficiency': self._analyze_route_correlations(route_analysis),
            'location_clusters': self._identify_problem_locations()
        }
        
        return correlations
    
    def analyze_operational_correlations(self) -> Dict[str, Any]:
        """Analyze operational correlations between different processes
        
        Returns:
            Dict with operational correlation analysis
        """
        logger.info("Analyzing operational correlations")
        
        # Get operational data
        warehouse_ops = self._get_warehouse_operations()
        delivery_performance = self._get_delivery_performance()
        driver_metrics = self._get_driver_metrics()
        
        correlations = {
            'warehouse_delivery_correlation': self._correlate_warehouse_delivery(warehouse_ops, delivery_performance),
            'driver_performance_factors': self._analyze_driver_performance(driver_metrics),
            'processing_time_impact': self._analyze_processing_time_impact(warehouse_ops, delivery_performance),
            'capacity_utilization': self._analyze_capacity_correlations()
        }
        
        return correlations
    
    def analyze_customer_correlations(self) -> Dict[str, Any]:
        """Analyze customer-related correlations and satisfaction patterns
        
        Returns:
            Dict with customer correlation analysis
        """
        logger.info("Analyzing customer correlations")
        
        # Get customer data
        feedback_data = self._get_customer_feedback()
        order_patterns = self._get_customer_order_patterns()
        delivery_history = self._get_customer_delivery_history()
        
        correlations = {
            'satisfaction_delivery_correlation': self._correlate_satisfaction_delivery(feedback_data, delivery_history),
            'client_type_performance': self._analyze_client_type_patterns(order_patterns),
            'repeat_customer_patterns': self._analyze_repeat_customer_behavior(order_patterns),
            'feedback_prediction_factors': self._identify_satisfaction_predictors(feedback_data, delivery_history)
        }
        
        return correlations
    
    def find_root_causes(self, issue_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find root causes for specific issues using correlation analysis
        
        Args:
            issue_type: Type of issue (delays, failures, cancellations)
            filters: Additional filters for analysis
            
        Returns:
            Dict with root cause analysis
        """
        logger.info(f"Finding root causes for: {issue_type}")
        
        if issue_type == 'delays':
            return self._analyze_delay_root_causes(filters)
        elif issue_type == 'failures':
            return self._analyze_failure_root_causes(filters)
        elif issue_type == 'cancellations':
            return self._analyze_cancellation_root_causes(filters)
        else:
            return self._analyze_general_root_causes(issue_type, filters)
    
    def _get_delivery_delays(self) -> List[Dict[str, Any]]:
        """Get delivery delay data from fleet logs"""
        pipeline = [
            {
                '$match': {
                    'status': 'delayed',
                    'delay_minutes': {'$gt': 0}
                }
            },
            {
                '$lookup': {
                    'from': 'orders',
                    'localField': 'order_id',
                    'foreignField': 'order_id',
                    'as': 'order_info'
                }
            },
            {
                '$unwind': '$order_info'
            },
            {
                '$project': {
                    'order_id': 1,
                    'timestamp': 1,
                    'delay_minutes': 1,
                    'location': 1,
                    'client_id': '$order_info.client_id',
                    'warehouse_id': '$order_info.warehouse_id'
                }
            }
        ]
        
        return list(self.db.fleet_logs.aggregate(pipeline))
    
    def _get_external_factors(self) -> List[Dict[str, Any]]:
        """Get external factors data"""
        pipeline = [
            {
                '$match': {
                    'date': {
                        '$gte': (datetime.now() - timedelta(days=30)).isoformat()
                    }
                }
            },
            {
                '$sort': {'date': -1}
            }
        ]
        
        return list(self.db.external_factors.aggregate(pipeline))
    
    def _correlate_weather_delays(self, delays: List[Dict], factors: List[Dict], time_window: int) -> Dict[str, Any]:
        """Correlate weather conditions with delivery delays"""
        weather_factors = [f for f in factors if f['factor_type'] == 'weather']
        
        correlation_data = []
        for delay in delays:
            delay_time = datetime.fromisoformat(delay['timestamp'])
            
            # Find weather factors within time window
            relevant_weather = []
            for weather in weather_factors:
                weather_time = datetime.fromisoformat(weather['date'])
                time_diff = abs((delay_time - weather_time).total_seconds() / 3600)
                
                if time_diff <= time_window:
                    relevant_weather.append(weather)
            
            if relevant_weather:
                # Calculate severity impact
                max_severity = max([self._severity_to_numeric(w['severity']) for w in relevant_weather])
                correlation_data.append({
                    'delay_minutes': delay['delay_minutes'],
                    'weather_severity': max_severity,
                    'weather_types': [w['factor_type'] for w in relevant_weather]
                })
        
        if len(correlation_data) < 2:
            return {'correlation': 0, 'significance': 'insufficient_data', 'sample_size': len(correlation_data)}
        
        # Calculate correlation
        delays_list = [d['delay_minutes'] for d in correlation_data]
        severity_list = [d['weather_severity'] for d in correlation_data]
        
        correlation = self._calculate_correlation(delays_list, severity_list)
        
        return {
            'correlation': correlation,
            'significance': self._interpret_correlation(correlation),
            'sample_size': len(correlation_data),
            'average_delay_with_weather': statistics.mean(delays_list),
            'weather_types_frequency': Counter([wt for d in correlation_data for wt in d['weather_types']])
        }
    
    def _correlate_traffic_delays(self, delays: List[Dict], factors: List[Dict], time_window: int) -> Dict[str, Any]:
        """Correlate traffic conditions with delivery delays"""
        traffic_factors = [f for f in factors if f['factor_type'] == 'traffic']
        
        correlation_data = []
        for delay in delays:
            delay_time = datetime.fromisoformat(delay['timestamp'])
            
            # Find traffic factors within time window and location
            relevant_traffic = []
            for traffic in traffic_factors:
                traffic_time = datetime.fromisoformat(traffic['date'])
                time_diff = abs((delay_time - traffic_time).total_seconds() / 3600)
                
                if time_diff <= time_window and self._locations_match(delay.get('location'), traffic.get('location')):
                    relevant_traffic.append(traffic)
            
            if relevant_traffic:
                max_severity = max([self._severity_to_numeric(t['severity']) for t in relevant_traffic])
                correlation_data.append({
                    'delay_minutes': delay['delay_minutes'],
                    'traffic_severity': max_severity
                })
        
        if len(correlation_data) < 2:
            return {'correlation': 0, 'significance': 'insufficient_data', 'sample_size': len(correlation_data)}
        
        delays_list = [d['delay_minutes'] for d in correlation_data]
        severity_list = [d['traffic_severity'] for d in correlation_data]
        
        correlation = self._calculate_correlation(delays_list, severity_list)
        
        return {
            'correlation': correlation,
            'significance': self._interpret_correlation(correlation),
            'sample_size': len(correlation_data),
            'average_delay_with_traffic': statistics.mean(delays_list)
        }
    
    def _correlate_event_delays(self, delays: List[Dict], factors: List[Dict], time_window: int) -> Dict[str, Any]:
        """Correlate special events with delivery delays"""
        event_factors = [f for f in factors if f['factor_type'] in ['event', 'holiday', 'strike']]
        
        delays_with_events = 0
        delays_without_events = 0
        total_delay_with_events = 0
        total_delay_without_events = 0
        
        for delay in delays:
            delay_time = datetime.fromisoformat(delay['timestamp'])
            has_event = False
            
            for event in event_factors:
                event_time = datetime.fromisoformat(event['date'])
                time_diff = abs((delay_time - event_time).total_seconds() / 3600)
                
                if time_diff <= time_window:
                    has_event = True
                    break
            
            if has_event:
                delays_with_events += 1
                total_delay_with_events += delay['delay_minutes']
            else:
                delays_without_events += 1
                total_delay_without_events += delay['delay_minutes']
        
        avg_delay_with_events = total_delay_with_events / delays_with_events if delays_with_events > 0 else 0
        avg_delay_without_events = total_delay_without_events / delays_without_events if delays_without_events > 0 else 0
        
        return {
            'delays_with_events': delays_with_events,
            'delays_without_events': delays_without_events,
            'avg_delay_with_events': avg_delay_with_events,
            'avg_delay_without_events': avg_delay_without_events,
            'impact_factor': avg_delay_with_events / avg_delay_without_events if avg_delay_without_events > 0 else 0
        }
    
    def _analyze_time_patterns(self, delays: List[Dict]) -> Dict[str, Any]:
        """Analyze time-based patterns in delays"""
        hourly_delays = defaultdict(list)
        daily_delays = defaultdict(list)
        
        for delay in delays:
            delay_time = datetime.fromisoformat(delay['timestamp'])
            hour = delay_time.hour
            day = delay_time.strftime('%A')
            
            hourly_delays[hour].append(delay['delay_minutes'])
            daily_delays[day].append(delay['delay_minutes'])
        
        # Calculate averages
        hourly_avg = {hour: statistics.mean(delays) for hour, delays in hourly_delays.items()}
        daily_avg = {day: statistics.mean(delays) for day, delays in daily_delays.items()}
        
        # Find peak hours and days
        peak_hour = max(hourly_avg.items(), key=lambda x: x[1]) if hourly_avg else (None, 0)
        peak_day = max(daily_avg.items(), key=lambda x: x[1]) if daily_avg else (None, 0)
        
        return {
            'hourly_patterns': hourly_avg,
            'daily_patterns': daily_avg,
            'peak_hour': {'hour': peak_hour[0], 'avg_delay': peak_hour[1]},
            'peak_day': {'day': peak_day[0], 'avg_delay': peak_day[1]}
        }
    
    def _get_city_performance(self) -> Dict[str, Any]:
        """Get performance metrics by city"""
        # This would need to be implemented based on how location data is stored
        # For now, return mock structure
        return {}
    
    def _get_warehouse_efficiency(self) -> List[Dict[str, Any]]:
        """Get warehouse efficiency metrics"""
        pipeline = [
            {
                '$group': {
                    '_id': '$warehouse_id',
                    'avg_processing_time': {'$avg': '$processing_time_minutes'},
                    'success_rate': {
                        '$avg': {
                            '$cond': [{'$eq': ['$status', 'success']}, 1, 0]
                        }
                    },
                    'total_operations': {'$sum': 1}
                }
            }
        ]
        
        return list(self.db.warehouse_logs.aggregate(pipeline))
    
    def _analyze_delay_root_causes(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze root causes of delays"""
        match_conditions = {'status': 'delayed'}
        if filters:
            match_conditions.update(filters)
        
        pipeline = [
            {'$match': match_conditions},
            {
                '$lookup': {
                    'from': 'external_factors',
                    'let': {'order_date': '$timestamp'},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        {'$gte': ['$$order_date', '$date']},
                                        {'$lte': ['$$order_date', {'$add': ['$date', 86400000]}]}  # 24 hours
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'external_factors'
                }
            },
            {
                '$group': {
                    '_id': {
                        'event_type': '$event_type',
                        'has_external_factors': {'$gt': [{'$size': '$external_factors'}, 0]}
                    },
                    'count': {'$sum': 1},
                    'avg_delay': {'$avg': '$delay_minutes'},
                    'external_factor_types': {'$push': '$external_factors.factor_type'}
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        results = list(self.db.fleet_logs.aggregate(pipeline))
        
        # Analyze patterns
        root_causes = {
            'primary_causes': results[:5],
            'external_factor_impact': self._calculate_external_factor_impact(results),
            'recommendations': self._generate_delay_recommendations(results)
        }
        
        return root_causes
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Convert severity string to numeric value"""
        severity_map = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return severity_map.get(severity.lower(), 1)
    
    def _locations_match(self, loc1: Any, loc2: Any) -> bool:
        """Check if two locations match (simplified)"""
        if not loc1 or not loc2:
            return False
        
        # Simple string matching for now
        if isinstance(loc1, str) and isinstance(loc2, str):
            return loc1.lower() == loc2.lower()
        
        # For coordinate-based matching, implement distance calculation
        return False
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi ** 2 for xi in x)
            sum_y2 = sum(yi ** 2 for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            if denominator == 0:
                return 0
            
            return numerator / denominator
        except Exception as e:
            logger.warning(f"Error calculating correlation: {e}")
            return 0
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        
        if abs_corr >= self.correlation_thresholds['strong']:
            return 'strong'
        elif abs_corr >= self.correlation_thresholds['moderate']:
            return 'moderate'
        elif abs_corr >= self.correlation_thresholds['weak']:
            return 'weak'
        else:
            return 'negligible'
    
    def _calculate_external_factor_impact(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate impact of external factors on delays"""
        with_factors = [r for r in results if r['_id']['has_external_factors']]
        without_factors = [r for r in results if not r['_id']['has_external_factors']]
        
        avg_delay_with = statistics.mean([r['avg_delay'] for r in with_factors]) if with_factors else 0
        avg_delay_without = statistics.mean([r['avg_delay'] for r in without_factors]) if without_factors else 0
        
        return {
            'avg_delay_with_external_factors': avg_delay_with,
            'avg_delay_without_external_factors': avg_delay_without,
            'impact_multiplier': avg_delay_with / avg_delay_without if avg_delay_without > 0 else 0
        }
    
    def _generate_delay_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate recommendations based on delay analysis"""
        recommendations = []
        
        # Analyze top causes
        if results:
            top_cause = results[0]
            if top_cause['_id']['has_external_factors']:
                recommendations.append("Implement better external factor monitoring and contingency planning")
            
            if top_cause['avg_delay'] > 60:  # More than 1 hour average delay
                recommendations.append("Review and optimize routing algorithms for high-delay scenarios")
        
        return recommendations
    
    # Placeholder methods for other correlation types
    def _get_route_analysis(self) -> List[Dict]: return []
    def _identify_problem_locations(self) -> Dict: return {}
    def _analyze_city_failure_patterns(self, data) -> Dict: return {}
    def _analyze_warehouse_correlations(self, data) -> Dict: return {}
    def _analyze_route_correlations(self, data) -> Dict: return {}
    def _get_warehouse_operations(self) -> List[Dict]: return []
    def _get_delivery_performance(self) -> List[Dict]: return []
    def _get_driver_metrics(self) -> List[Dict]: return []
    def _correlate_warehouse_delivery(self, ops, perf) -> Dict: return {}
    def _analyze_driver_performance(self, metrics) -> Dict: return {}
    def _analyze_processing_time_impact(self, ops, perf) -> Dict: return {}
    def _analyze_capacity_correlations(self) -> Dict: return {}
    def _get_customer_feedback(self) -> List[Dict]: return []
    def _get_customer_order_patterns(self) -> List[Dict]: return []
    def _get_customer_delivery_history(self) -> List[Dict]: return []
    def _correlate_satisfaction_delivery(self, feedback, history) -> Dict: return {}
    def _analyze_client_type_patterns(self, patterns) -> Dict: return {}
    def _analyze_repeat_customer_behavior(self, patterns) -> Dict: return {}
    def _identify_satisfaction_predictors(self, feedback, history) -> Dict: return {}
    def _analyze_failure_root_causes(self, filters) -> Dict: return {}
    def _analyze_cancellation_root_causes(self, filters) -> Dict: return {}
    def _analyze_general_root_causes(self, issue_type, filters) -> Dict: return {}
