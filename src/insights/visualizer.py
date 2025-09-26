"""
Visualization data preparation module for charts and graphs
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class VisualizationDataPrep:
    """Prepare data for various visualization types"""
    
    def __init__(self):
        """Initialize visualization data preparation"""
        self.logger = logging.getLogger(__name__)
    
    def prepare_time_series_data(self, data: List[Dict[str, Any]], 
                                time_field: str, 
                                value_field: str,
                                aggregation: str = 'sum',
                                interval: str = 'daily') -> Dict[str, Any]:
        """Prepare time series data for line charts
        
        Args:
            data: Raw data with time and value fields
            time_field: Field containing timestamp/date
            value_field: Field containing values to plot
            aggregation: How to aggregate values (sum, avg, count, min, max)
            interval: Time interval for grouping (hourly, daily, weekly, monthly)
            
        Returns:
            Dict with time series data ready for visualization
        """
        try:
            # Extract and parse time series data
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
                        'timestamp': time_value,
                        'value': float(data_value) if isinstance(data_value, (int, float)) else 1
                    })
            
            if not time_series:
                return {'labels': [], 'values': [], 'metadata': {'total_points': 0}}
            
            # Group by time interval
            grouped_data = self._group_by_time_interval(time_series, interval)
            
            # Aggregate values
            aggregated_data = self._aggregate_time_series(grouped_data, aggregation)
            
            # Sort by time
            sorted_data = sorted(aggregated_data.items())
            
            # Format for visualization
            labels = [self._format_time_label(timestamp, interval) for timestamp, _ in sorted_data]
            values = [value for _, value in sorted_data]
            
            # Calculate metadata
            metadata = {
                'total_points': len(values),
                'date_range': {
                    'start': min(timestamp for timestamp, _ in sorted_data).isoformat() if sorted_data else None,
                    'end': max(timestamp for timestamp, _ in sorted_data).isoformat() if sorted_data else None
                },
                'aggregation': aggregation,
                'interval': interval,
                'statistics': {
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0,
                    'avg': statistics.mean(values) if values else 0,
                    'total': sum(values) if values else 0
                }
            }
            
            return {
                'labels': labels,
                'values': values,
                'metadata': metadata,
                'chart_type': 'line',
                'title': f'{value_field.replace("_", " ").title()} Over Time',
                'x_axis_label': 'Time',
                'y_axis_label': value_field.replace('_', ' ').title()
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing time series data: {e}")
            return {'labels': [], 'values': [], 'metadata': {'error': str(e)}}
    
    def prepare_pie_chart_data(self, data: List[Dict[str, Any]], 
                              category_field: str,
                              value_field: Optional[str] = None,
                              top_n: int = 10) -> Dict[str, Any]:
        """Prepare data for pie charts
        
        Args:
            data: Raw data
            category_field: Field to use for pie slices
            value_field: Field to sum for slice sizes (if None, counts occurrences)
            top_n: Maximum number of slices to show
            
        Returns:
            Dict with pie chart data
        """
        try:
            # Group data by category
            category_data = defaultdict(list)
            
            for item in data:
                category = self._extract_nested_value(item, category_field)
                if category is not None:
                    if value_field:
                        value = self._extract_nested_value(item, value_field)
                        if value is not None and isinstance(value, (int, float)):
                            category_data[str(category)].append(float(value))
                    else:
                        category_data[str(category)].append(1)
            
            # Calculate totals for each category
            category_totals = {}
            for category, values in category_data.items():
                category_totals[category] = sum(values)
            
            # Sort by total and take top N
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            top_categories = sorted_categories[:top_n]
            
            # Handle "Others" category if there are more than top_n categories
            if len(sorted_categories) > top_n:
                others_total = sum(total for _, total in sorted_categories[top_n:])
                top_categories.append(('Others', others_total))
            
            # Calculate percentages
            total_value = sum(total for _, total in top_categories)
            
            labels = []
            values = []
            percentages = []
            
            for category, total in top_categories:
                percentage = (total / total_value * 100) if total_value > 0 else 0
                labels.append(category)
                values.append(total)
                percentages.append(round(percentage, 1))
            
            metadata = {
                'total_categories': len(category_data),
                'total_value': total_value,
                'showing_top_n': min(top_n, len(category_data)),
                'has_others': len(sorted_categories) > top_n
            }
            
            return {
                'labels': labels,
                'values': values,
                'percentages': percentages,
                'metadata': metadata,
                'chart_type': 'pie',
                'title': f'{category_field.replace("_", " ").title()} Distribution',
                'value_label': value_field.replace('_', ' ').title() if value_field else 'Count'
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing pie chart data: {e}")
            return {'labels': [], 'values': [], 'percentages': [], 'metadata': {'error': str(e)}}
    
    def prepare_bar_chart_data(self, data: List[Dict[str, Any]], 
                              category_field: str,
                              value_field: str,
                              aggregation: str = 'sum',
                              sort_by: str = 'value',
                              top_n: int = 15) -> Dict[str, Any]:
        """Prepare data for bar charts
        
        Args:
            data: Raw data
            category_field: Field for x-axis categories
            value_field: Field for y-axis values
            aggregation: How to aggregate values (sum, avg, count, min, max)
            sort_by: How to sort bars ('value', 'category', 'count')
            top_n: Maximum number of bars to show
            
        Returns:
            Dict with bar chart data
        """
        try:
            # Group data by category
            category_data = defaultdict(list)
            
            for item in data:
                category = self._extract_nested_value(item, category_field)
                value = self._extract_nested_value(item, value_field)
                
                if category is not None and value is not None:
                    if isinstance(value, (int, float)):
                        category_data[str(category)].append(float(value))
                    else:
                        category_data[str(category)].append(1)  # Count mode
            
            # Aggregate values for each category
            category_results = {}
            for category, values in category_data.items():
                if aggregation == 'sum':
                    result = sum(values)
                elif aggregation == 'avg':
                    result = statistics.mean(values)
                elif aggregation == 'count':
                    result = len(values)
                elif aggregation == 'min':
                    result = min(values)
                elif aggregation == 'max':
                    result = max(values)
                else:
                    result = sum(values)  # Default to sum
                
                category_results[category] = {
                    'value': result,
                    'count': len(values),
                    'raw_values': values
                }
            
            # Sort categories
            if sort_by == 'value':
                sorted_categories = sorted(category_results.items(), 
                                         key=lambda x: x[1]['value'], reverse=True)
            elif sort_by == 'count':
                sorted_categories = sorted(category_results.items(), 
                                         key=lambda x: x[1]['count'], reverse=True)
            else:  # sort by category name
                sorted_categories = sorted(category_results.items(), key=lambda x: x[0])
            
            # Take top N
            top_categories = sorted_categories[:top_n]
            
            # Prepare chart data
            labels = [category for category, _ in top_categories]
            values = [data['value'] for _, data in top_categories]
            counts = [data['count'] for _, data in top_categories]
            
            metadata = {
                'total_categories': len(category_results),
                'aggregation': aggregation,
                'sort_by': sort_by,
                'showing_top_n': len(top_categories),
                'statistics': {
                    'min_value': min(values) if values else 0,
                    'max_value': max(values) if values else 0,
                    'avg_value': statistics.mean(values) if values else 0,
                    'total_value': sum(values) if values else 0
                }
            }
            
            return {
                'labels': labels,
                'values': values,
                'counts': counts,
                'metadata': metadata,
                'chart_type': 'bar',
                'title': f'{value_field.replace("_", " ").title()} by {category_field.replace("_", " ").title()}',
                'x_axis_label': category_field.replace('_', ' ').title(),
                'y_axis_label': f'{aggregation.title()} of {value_field.replace("_", " ").title()}'
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing bar chart data: {e}")
            return {'labels': [], 'values': [], 'metadata': {'error': str(e)}}
    
    def prepare_heatmap_data(self, data: List[Dict[str, Any]], 
                            x_field: str,
                            y_field: str,
                            value_field: str,
                            aggregation: str = 'sum') -> Dict[str, Any]:
        """Prepare data for heatmaps
        
        Args:
            data: Raw data
            x_field: Field for x-axis (e.g., hour of day)
            y_field: Field for y-axis (e.g., day of week)
            value_field: Field for heat intensity
            aggregation: How to aggregate values
            
        Returns:
            Dict with heatmap data
        """
        try:
            # Group data by x and y coordinates
            heatmap_data = defaultdict(lambda: defaultdict(list))
            
            for item in data:
                x_value = self._extract_nested_value(item, x_field)
                y_value = self._extract_nested_value(item, y_field)
                heat_value = self._extract_nested_value(item, value_field)
                
                if x_value is not None and y_value is not None and heat_value is not None:
                    if isinstance(heat_value, (int, float)):
                        heatmap_data[str(y_value)][str(x_value)].append(float(heat_value))
                    else:
                        heatmap_data[str(y_value)][str(x_value)].append(1)
            
            # Get all unique x and y values
            all_x_values = set()
            all_y_values = set()
            
            for y_val, x_dict in heatmap_data.items():
                all_y_values.add(y_val)
                for x_val in x_dict.keys():
                    all_x_values.add(x_val)
            
            # Sort values (try numeric sort first, then string sort)
            try:
                x_labels = sorted(all_x_values, key=lambda x: float(x))
            except:
                x_labels = sorted(all_x_values)
            
            try:
                y_labels = sorted(all_y_values, key=lambda x: float(x))
            except:
                y_labels = sorted(all_y_values)
            
            # Create matrix data
            matrix = []
            for y_val in y_labels:
                row = []
                for x_val in x_labels:
                    values = heatmap_data[y_val][x_val]
                    if values:
                        if aggregation == 'sum':
                            cell_value = sum(values)
                        elif aggregation == 'avg':
                            cell_value = statistics.mean(values)
                        elif aggregation == 'count':
                            cell_value = len(values)
                        elif aggregation == 'min':
                            cell_value = min(values)
                        elif aggregation == 'max':
                            cell_value = max(values)
                        else:
                            cell_value = sum(values)
                    else:
                        cell_value = 0
                    row.append(cell_value)
                matrix.append(row)
            
            # Calculate statistics
            all_values = [val for row in matrix for val in row if val > 0]
            
            metadata = {
                'dimensions': {
                    'x_size': len(x_labels),
                    'y_size': len(y_labels)
                },
                'aggregation': aggregation,
                'statistics': {
                    'min_value': min(all_values) if all_values else 0,
                    'max_value': max(all_values) if all_values else 0,
                    'avg_value': statistics.mean(all_values) if all_values else 0,
                    'total_cells': len(x_labels) * len(y_labels),
                    'non_zero_cells': len(all_values)
                }
            }
            
            return {
                'matrix': matrix,
                'x_labels': x_labels,
                'y_labels': y_labels,
                'metadata': metadata,
                'chart_type': 'heatmap',
                'title': f'{value_field.replace("_", " ").title()} Heatmap',
                'x_axis_label': x_field.replace('_', ' ').title(),
                'y_axis_label': y_field.replace('_', ' ').title(),
                'value_label': f'{aggregation.title()} of {value_field.replace("_", " ").title()}'
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing heatmap data: {e}")
            return {'matrix': [], 'x_labels': [], 'y_labels': [], 'metadata': {'error': str(e)}}
    
    def prepare_scatter_plot_data(self, data: List[Dict[str, Any]], 
                                 x_field: str,
                                 y_field: str,
                                 size_field: Optional[str] = None,
                                 color_field: Optional[str] = None,
                                 limit: int = 1000) -> Dict[str, Any]:
        """Prepare data for scatter plots
        
        Args:
            data: Raw data
            x_field: Field for x-axis values
            y_field: Field for y-axis values
            size_field: Optional field for point sizes
            color_field: Optional field for point colors/categories
            limit: Maximum number of points to include
            
        Returns:
            Dict with scatter plot data
        """
        try:
            scatter_points = []
            
            for item in data:
                x_value = self._extract_nested_value(item, x_field)
                y_value = self._extract_nested_value(item, y_field)
                
                if (x_value is not None and y_value is not None and 
                    isinstance(x_value, (int, float)) and isinstance(y_value, (int, float))):
                    
                    point = {
                        'x': float(x_value),
                        'y': float(y_value)
                    }
                    
                    # Add size if specified
                    if size_field:
                        size_value = self._extract_nested_value(item, size_field)
                        if size_value is not None and isinstance(size_value, (int, float)):
                            point['size'] = float(size_value)
                    
                    # Add color/category if specified
                    if color_field:
                        color_value = self._extract_nested_value(item, color_field)
                        if color_value is not None:
                            point['category'] = str(color_value)
                    
                    scatter_points.append(point)
            
            # Limit number of points for performance
            if len(scatter_points) > limit:
                # Sample points to maintain distribution
                step = len(scatter_points) // limit
                scatter_points = scatter_points[::step][:limit]
            
            # Extract data arrays
            x_values = [point['x'] for point in scatter_points]
            y_values = [point['y'] for point in scatter_points]
            
            # Calculate correlation if we have enough points
            correlation = None
            if len(x_values) > 2:
                try:
                    correlation = self._calculate_correlation(x_values, y_values)
                except:
                    correlation = None
            
            # Get unique categories if color_field is used
            categories = []
            if color_field and scatter_points:
                categories = list(set(point.get('category', 'default') for point in scatter_points))
            
            metadata = {
                'total_points': len(scatter_points),
                'correlation': correlation,
                'x_range': {
                    'min': min(x_values) if x_values else 0,
                    'max': max(x_values) if x_values else 0
                },
                'y_range': {
                    'min': min(y_values) if y_values else 0,
                    'max': max(y_values) if y_values else 0
                },
                'categories': categories,
                'has_size_data': size_field is not None,
                'has_color_data': color_field is not None
            }
            
            return {
                'points': scatter_points,
                'metadata': metadata,
                'chart_type': 'scatter',
                'title': f'{y_field.replace("_", " ").title()} vs {x_field.replace("_", " ").title()}',
                'x_axis_label': x_field.replace('_', ' ').title(),
                'y_axis_label': y_field.replace('_', ' ').title()
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing scatter plot data: {e}")
            return {'points': [], 'metadata': {'error': str(e)}}
    
    def prepare_multi_series_data(self, data: List[Dict[str, Any]], 
                                 time_field: str,
                                 series_field: str,
                                 value_field: str,
                                 aggregation: str = 'sum',
                                 interval: str = 'daily') -> Dict[str, Any]:
        """Prepare data for multi-series line charts
        
        Args:
            data: Raw data
            time_field: Field containing timestamp/date
            series_field: Field to separate series by
            value_field: Field containing values to plot
            aggregation: How to aggregate values
            interval: Time interval for grouping
            
        Returns:
            Dict with multi-series data
        """
        try:
            # Group data by series
            series_data = defaultdict(list)
            
            for item in data:
                time_value = self._extract_nested_value(item, time_field)
                series_value = self._extract_nested_value(item, series_field)
                data_value = self._extract_nested_value(item, value_field)
                
                if time_value and series_value is not None and data_value is not None:
                    # Convert time to datetime if needed
                    if isinstance(time_value, str):
                        try:
                            time_value = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    series_data[str(series_value)].append({
                        'timestamp': time_value,
                        'value': float(data_value) if isinstance(data_value, (int, float)) else 1
                    })
            
            # Process each series
            processed_series = {}
            all_timestamps = set()
            
            for series_name, series_points in series_data.items():
                # Group by time interval
                grouped_data = self._group_by_time_interval(series_points, interval)
                
                # Aggregate values
                aggregated_data = self._aggregate_time_series(grouped_data, aggregation)
                
                processed_series[series_name] = aggregated_data
                all_timestamps.update(aggregated_data.keys())
            
            # Create common time axis
            sorted_timestamps = sorted(all_timestamps)
            time_labels = [self._format_time_label(ts, interval) for ts in sorted_timestamps]
            
            # Create series data arrays
            series_list = []
            for series_name, series_data_dict in processed_series.items():
                values = [series_data_dict.get(ts, 0) for ts in sorted_timestamps]
                series_list.append({
                    'name': series_name,
                    'values': values,
                    'statistics': {
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0,
                        'avg': statistics.mean(values) if values else 0,
                        'total': sum(values) if values else 0
                    }
                })
            
            metadata = {
                'total_series': len(series_list),
                'total_points': len(time_labels),
                'date_range': {
                    'start': sorted_timestamps[0].isoformat() if sorted_timestamps else None,
                    'end': sorted_timestamps[-1].isoformat() if sorted_timestamps else None
                },
                'aggregation': aggregation,
                'interval': interval
            }
            
            return {
                'labels': time_labels,
                'series': series_list,
                'metadata': metadata,
                'chart_type': 'multi_line',
                'title': f'{value_field.replace("_", " ").title()} by {series_field.replace("_", " ").title()}',
                'x_axis_label': 'Time',
                'y_axis_label': value_field.replace('_', ' ').title()
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing multi-series data: {e}")
            return {'labels': [], 'series': [], 'metadata': {'error': str(e)}}
    
    # Helper methods
    
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
    
    def _group_by_time_interval(self, time_series: List[Dict], interval: str) -> Dict[datetime, List[float]]:
        """Group time series data by specified interval"""
        grouped = defaultdict(list)
        
        for point in time_series:
            timestamp = point['timestamp']
            value = point['value']
            
            # Round timestamp to interval
            if interval == 'hourly':
                rounded_time = timestamp.replace(minute=0, second=0, microsecond=0)
            elif interval == 'daily':
                rounded_time = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            elif interval == 'weekly':
                days_since_monday = timestamp.weekday()
                rounded_time = (timestamp - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif interval == 'monthly':
                rounded_time = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                rounded_time = timestamp  # No rounding
            
            grouped[rounded_time].append(value)
        
        return grouped
    
    def _aggregate_time_series(self, grouped_data: Dict[datetime, List[float]], aggregation: str) -> Dict[datetime, float]:
        """Aggregate grouped time series data"""
        aggregated = {}
        
        for timestamp, values in grouped_data.items():
            if aggregation == 'sum':
                aggregated[timestamp] = sum(values)
            elif aggregation == 'avg':
                aggregated[timestamp] = statistics.mean(values)
            elif aggregation == 'count':
                aggregated[timestamp] = len(values)
            elif aggregation == 'min':
                aggregated[timestamp] = min(values)
            elif aggregation == 'max':
                aggregated[timestamp] = max(values)
            else:
                aggregated[timestamp] = sum(values)  # Default to sum
        
        return aggregated
    
    def _format_time_label(self, timestamp: datetime, interval: str) -> str:
        """Format timestamp for chart labels"""
        if interval == 'hourly':
            return timestamp.strftime('%H:%M')
        elif interval == 'daily':
            return timestamp.strftime('%Y-%m-%d')
        elif interval == 'weekly':
            return f"Week of {timestamp.strftime('%Y-%m-%d')}"
        elif interval == 'monthly':
            return timestamp.strftime('%Y-%m')
        else:
            return timestamp.strftime('%Y-%m-%d %H:%M')
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        correlation = (n * sum_xy - sum_x * sum_y) / denominator
        return round(correlation, 3)
