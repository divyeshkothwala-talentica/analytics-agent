"""
Result Processor for statistical analysis and pattern detection
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import statistics
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StatisticalSummary:
    """Statistical summary of numerical data"""
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentiles: Dict[int, float]  # 25th, 50th, 75th, 90th, 95th


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    direction: str  # increasing, decreasing, stable
    change_percentage: float
    confidence: float
    period_comparison: Dict[str, Any]
    seasonal_patterns: List[Dict[str, Any]]


@dataclass
class AnomalyDetection:
    """Anomaly detection results"""
    anomalies: List[Dict[str, Any]]
    threshold_method: str
    confidence_level: float
    total_anomalies: int


class ResultProcessor:
    """Process MongoDB aggregation results for insight generation"""
    
    def __init__(self):
        """Initialize the result processor"""
        self.logger = logging.getLogger(__name__)
    
    def calculate_statistics(self, data: List[Dict[str, Any]], 
                           numeric_field: str) -> Optional[StatisticalSummary]:
        """Calculate comprehensive statistics for a numeric field
        
        Args:
            data: List of result documents
            numeric_field: Field name to analyze
            
        Returns:
            StatisticalSummary object or None if insufficient data
        """
        try:
            # Extract numeric values
            values = []
            for item in data:
                value = self._extract_nested_value(item, numeric_field)
                if value is not None and isinstance(value, (int, float)):
                    values.append(float(value))
            
            if len(values) < 2:
                self.logger.warning(f"Insufficient data for statistics on {numeric_field}")
                return None
            
            # Calculate statistics
            count = len(values)
            mean = statistics.mean(values)
            median = statistics.median(values)
            std_dev = statistics.stdev(values) if count > 1 else 0.0
            min_value = min(values)
            max_value = max(values)
            
            # Calculate percentiles
            percentiles = {}
            for p in [25, 50, 75, 90, 95]:
                percentiles[p] = self._calculate_percentile(values, p)
            
            return StatisticalSummary(
                count=count,
                mean=mean,
                median=median,
                std_dev=std_dev,
                min_value=min_value,
                max_value=max_value,
                percentiles=percentiles
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")
            return None
    
    def detect_patterns(self, data: List[Dict[str, Any]], 
                       group_field: str, 
                       value_field: str) -> Dict[str, Any]:
        """Detect recurring patterns in the data
        
        Args:
            data: List of result documents
            group_field: Field to group by (e.g., 'failure_reason', 'time_period')
            value_field: Field to analyze values for
            
        Returns:
            Dict with pattern analysis results
        """
        try:
            patterns = defaultdict(list)
            
            # Group data by the specified field
            for item in data:
                group_key = self._extract_nested_value(item, group_field)
                value = self._extract_nested_value(item, value_field)
                
                if group_key is not None and value is not None:
                    patterns[str(group_key)].append(value)
            
            # Analyze patterns
            pattern_analysis = {}
            total_count = sum(len(values) for values in patterns.values())
            
            for pattern, values in patterns.items():
                count = len(values)
                percentage = (count / total_count * 100) if total_count > 0 else 0
                
                # Calculate statistics for this pattern
                if isinstance(values[0], (int, float)):
                    avg_value = statistics.mean(values)
                    pattern_stats = {
                        'average': avg_value,
                        'min': min(values),
                        'max': max(values)
                    }
                else:
                    pattern_stats = {'most_common': Counter(values).most_common(3)}
                
                pattern_analysis[pattern] = {
                    'count': count,
                    'percentage': round(percentage, 2),
                    'statistics': pattern_stats
                }
            
            # Sort by frequency
            sorted_patterns = dict(sorted(
                pattern_analysis.items(), 
                key=lambda x: x[1]['count'], 
                reverse=True
            ))
            
            return {
                'patterns': sorted_patterns,
                'total_groups': len(patterns),
                'total_items': total_count,
                'top_pattern': max(sorted_patterns.keys(), key=lambda k: sorted_patterns[k]['count']) if sorted_patterns else None
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting patterns: {e}")
            return {'patterns': {}, 'total_groups': 0, 'total_items': 0, 'top_pattern': None}
    
    def detect_anomalies(self, data: List[Dict[str, Any]], 
                        numeric_field: str,
                        method: str = 'iqr',
                        confidence: float = 0.95) -> AnomalyDetection:
        """Detect anomalies in numeric data
        
        Args:
            data: List of result documents
            numeric_field: Field to analyze for anomalies
            method: Detection method ('iqr', 'zscore', 'modified_zscore')
            confidence: Confidence level for detection
            
        Returns:
            AnomalyDetection object
        """
        try:
            # Extract numeric values with context
            values_with_context = []
            for i, item in enumerate(data):
                value = self._extract_nested_value(item, numeric_field)
                if value is not None and isinstance(value, (int, float)):
                    values_with_context.append({
                        'index': i,
                        'value': float(value),
                        'context': item
                    })
            
            if len(values_with_context) < 3:
                return AnomalyDetection([], method, confidence, 0)
            
            values = [item['value'] for item in values_with_context]
            anomalies = []
            
            if method == 'iqr':
                anomalies = self._detect_iqr_anomalies(values_with_context, values)
            elif method == 'zscore':
                anomalies = self._detect_zscore_anomalies(values_with_context, values)
            elif method == 'modified_zscore':
                anomalies = self._detect_modified_zscore_anomalies(values_with_context, values)
            
            return AnomalyDetection(
                anomalies=anomalies,
                threshold_method=method,
                confidence_level=confidence,
                total_anomalies=len(anomalies)
            )
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return AnomalyDetection([], method, confidence, 0)
    
    def analyze_trends(self, data: List[Dict[str, Any]], 
                      time_field: str, 
                      value_field: str,
                      period_days: int = 7) -> TrendAnalysis:
        """Analyze trends over time
        
        Args:
            data: List of result documents with time series data
            time_field: Field containing timestamp/date
            value_field: Field containing values to analyze
            period_days: Number of days for period comparison
            
        Returns:
            TrendAnalysis object
        """
        try:
            # Extract and sort time series data
            time_series = []
            for item in data:
                time_value = self._extract_nested_value(item, time_field)
                data_value = self._extract_nested_value(item, value_field)
                
                if time_value and data_value is not None:
                    # Convert time to datetime if needed
                    if isinstance(time_value, str):
                        try:
                            time_value = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    time_series.append({
                        'time': time_value,
                        'value': float(data_value) if isinstance(data_value, (int, float)) else data_value
                    })
            
            if len(time_series) < 2:
                return TrendAnalysis('stable', 0.0, 0.0, {}, [])
            
            # Sort by time
            time_series.sort(key=lambda x: x['time'])
            
            # Calculate trend direction and change
            values = [item['value'] for item in time_series if isinstance(item['value'], (int, float))]
            if len(values) < 2:
                return TrendAnalysis('stable', 0.0, 0.0, {}, [])
            
            # Simple linear trend calculation
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            change_percentage = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0
            
            # Determine direction
            if abs(change_percentage) < 5:
                direction = 'stable'
            elif change_percentage > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            # Calculate confidence based on consistency
            confidence = self._calculate_trend_confidence(values)
            
            # Period comparison
            cutoff_date = datetime.now() - timedelta(days=period_days)
            recent_data = [item for item in time_series if item['time'] >= cutoff_date]
            older_data = [item for item in time_series if item['time'] < cutoff_date]
            
            period_comparison = self._compare_periods(recent_data, older_data, value_field)
            
            # Detect seasonal patterns (simplified)
            seasonal_patterns = self._detect_seasonal_patterns(time_series)
            
            return TrendAnalysis(
                direction=direction,
                change_percentage=round(change_percentage, 2),
                confidence=confidence,
                period_comparison=period_comparison,
                seasonal_patterns=seasonal_patterns
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return TrendAnalysis('stable', 0.0, 0.0, {}, [])
    
    def rank_items(self, data: List[Dict[str, Any]], 
                   rank_field: str, 
                   value_field: str,
                   limit: int = 10) -> List[Dict[str, Any]]:
        """Rank items by a specific metric
        
        Args:
            data: List of result documents
            rank_field: Field to rank by (e.g., 'warehouse_id', 'failure_reason')
            value_field: Field containing values to rank by
            limit: Maximum number of items to return
            
        Returns:
            List of ranked items with statistics
        """
        try:
            # Group and aggregate data
            groups = defaultdict(list)
            
            for item in data:
                rank_key = self._extract_nested_value(item, rank_field)
                value = self._extract_nested_value(item, value_field)
                
                if rank_key is not None and value is not None:
                    groups[str(rank_key)].append(value)
            
            # Calculate rankings
            rankings = []
            for group_key, values in groups.items():
                if isinstance(values[0], (int, float)):
                    # Numeric values
                    total = sum(values)
                    average = statistics.mean(values)
                    count = len(values)
                    
                    rankings.append({
                        'item': group_key,
                        'total': total,
                        'average': round(average, 2),
                        'count': count,
                        'min': min(values),
                        'max': max(values)
                    })
                else:
                    # Non-numeric values (count frequency)
                    count = len(values)
                    rankings.append({
                        'item': group_key,
                        'count': count,
                        'percentage': 0  # Will be calculated after sorting
                    })
            
            # Sort by total/count (descending)
            sort_key = 'total' if 'total' in rankings[0] else 'count'
            rankings.sort(key=lambda x: x[sort_key], reverse=True)
            
            # Calculate percentages for non-numeric data
            if 'percentage' in rankings[0]:
                total_count = sum(item['count'] for item in rankings)
                for item in rankings:
                    item['percentage'] = round((item['count'] / total_count * 100), 2) if total_count > 0 else 0
            
            return rankings[:limit]
            
        except Exception as e:
            self.logger.error(f"Error ranking items: {e}")
            return []
    
    def _extract_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Extract value from nested dictionary using dot notation"""
        try:
            keys = field_path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        except:
            return None
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _detect_iqr_anomalies(self, values_with_context: List[Dict], values: List[float]) -> List[Dict]:
        """Detect anomalies using Interquartile Range method"""
        q1 = self._calculate_percentile(values, 25)
        q3 = self._calculate_percentile(values, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        anomalies = []
        for item in values_with_context:
            if item['value'] < lower_bound or item['value'] > upper_bound:
                anomalies.append({
                    'value': item['value'],
                    'type': 'low' if item['value'] < lower_bound else 'high',
                    'severity': abs(item['value'] - (q1 if item['value'] < lower_bound else q3)) / iqr,
                    'context': item['context']
                })
        
        return anomalies
    
    def _detect_zscore_anomalies(self, values_with_context: List[Dict], values: List[float]) -> List[Dict]:
        """Detect anomalies using Z-score method"""
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_dev == 0:
            return []
        
        threshold = 2.5  # Standard threshold for Z-score
        anomalies = []
        
        for item in values_with_context:
            z_score = abs(item['value'] - mean) / std_dev
            if z_score > threshold:
                anomalies.append({
                    'value': item['value'],
                    'z_score': z_score,
                    'type': 'high' if item['value'] > mean else 'low',
                    'severity': z_score / threshold,
                    'context': item['context']
                })
        
        return anomalies
    
    def _detect_modified_zscore_anomalies(self, values_with_context: List[Dict], values: List[float]) -> List[Dict]:
        """Detect anomalies using Modified Z-score method"""
        median = statistics.median(values)
        mad = statistics.median([abs(x - median) for x in values])
        
        if mad == 0:
            return []
        
        threshold = 3.5  # Standard threshold for Modified Z-score
        anomalies = []
        
        for item in values_with_context:
            modified_z_score = 0.6745 * (item['value'] - median) / mad
            if abs(modified_z_score) > threshold:
                anomalies.append({
                    'value': item['value'],
                    'modified_z_score': abs(modified_z_score),
                    'type': 'high' if item['value'] > median else 'low',
                    'severity': abs(modified_z_score) / threshold,
                    'context': item['context']
                })
        
        return anomalies
    
    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend direction based on consistency"""
        if len(values) < 3:
            return 0.0
        
        # Calculate moving averages to smooth out noise
        window_size = max(3, len(values) // 4)
        moving_averages = []
        
        for i in range(len(values) - window_size + 1):
            avg = statistics.mean(values[i:i + window_size])
            moving_averages.append(avg)
        
        if len(moving_averages) < 2:
            return 0.0
        
        # Count consistent direction changes
        consistent_changes = 0
        total_changes = len(moving_averages) - 1
        
        for i in range(1, len(moving_averages)):
            if i == 1:
                continue
            
            prev_change = moving_averages[i-1] - moving_averages[i-2]
            curr_change = moving_averages[i] - moving_averages[i-1]
            
            if (prev_change > 0 and curr_change > 0) or (prev_change < 0 and curr_change < 0):
                consistent_changes += 1
        
        confidence = consistent_changes / max(1, total_changes - 1)
        return round(confidence, 2)
    
    def _compare_periods(self, recent_data: List[Dict], older_data: List[Dict], value_field: str) -> Dict[str, Any]:
        """Compare two time periods"""
        try:
            recent_values = [self._extract_nested_value(item, value_field) 
                           for item in recent_data 
                           if isinstance(self._extract_nested_value(item, value_field), (int, float))]
            
            older_values = [self._extract_nested_value(item, value_field) 
                          for item in older_data 
                          if isinstance(self._extract_nested_value(item, value_field), (int, float))]
            
            if not recent_values or not older_values:
                return {'comparison': 'insufficient_data'}
            
            recent_avg = statistics.mean(recent_values)
            older_avg = statistics.mean(older_values)
            
            change = ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0
            
            return {
                'recent_period': {
                    'count': len(recent_values),
                    'average': round(recent_avg, 2)
                },
                'previous_period': {
                    'count': len(older_values),
                    'average': round(older_avg, 2)
                },
                'change_percentage': round(change, 2),
                'direction': 'improved' if change > 0 else 'declined' if change < 0 else 'stable'
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing periods: {e}")
            return {'comparison': 'error'}
    
    def _detect_seasonal_patterns(self, time_series: List[Dict]) -> List[Dict[str, Any]]:
        """Detect basic seasonal patterns (simplified implementation)"""
        try:
            # Group by hour of day
            hourly_patterns = defaultdict(list)
            daily_patterns = defaultdict(list)
            
            for item in time_series:
                if isinstance(item['value'], (int, float)):
                    time_obj = item['time']
                    hour = time_obj.hour
                    day_of_week = time_obj.weekday()  # 0=Monday, 6=Sunday
                    
                    hourly_patterns[hour].append(item['value'])
                    daily_patterns[day_of_week].append(item['value'])
            
            patterns = []
            
            # Analyze hourly patterns
            if hourly_patterns:
                hourly_avgs = {hour: statistics.mean(values) for hour, values in hourly_patterns.items()}
                peak_hour = max(hourly_avgs.keys(), key=lambda k: hourly_avgs[k])
                low_hour = min(hourly_avgs.keys(), key=lambda k: hourly_avgs[k])
                
                patterns.append({
                    'type': 'hourly',
                    'peak_time': f"{peak_hour}:00",
                    'low_time': f"{low_hour}:00",
                    'peak_value': round(hourly_avgs[peak_hour], 2),
                    'low_value': round(hourly_avgs[low_hour], 2)
                })
            
            # Analyze daily patterns
            if daily_patterns:
                daily_avgs = {day: statistics.mean(values) for day, values in daily_patterns.items()}
                peak_day = max(daily_avgs.keys(), key=lambda k: daily_avgs[k])
                low_day = min(daily_avgs.keys(), key=lambda k: daily_avgs[k])
                
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                patterns.append({
                    'type': 'daily',
                    'peak_day': day_names[peak_day],
                    'low_day': day_names[low_day],
                    'peak_value': round(daily_avgs[peak_day], 2),
                    'low_value': round(daily_avgs[low_day], 2)
                })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting seasonal patterns: {e}")
            return []
