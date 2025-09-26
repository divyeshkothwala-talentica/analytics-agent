"""
Performance Monitor for tracking system performance during demo
"""

import time
import logging
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    timestamp: datetime
    query: str
    duration_seconds: float
    success: bool
    result_count: int
    memory_usage_mb: float
    cpu_usage_percent: float
    error_message: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]


class PerformanceMonitor:
    """Monitor system performance and query metrics"""
    
    def __init__(self, max_history: int = 1000):
        """Initialize the performance monitor
        
        Args:
            max_history: Maximum number of metrics to keep in memory
        """
        self.max_history = max_history
        self.query_metrics: deque = deque(maxlen=max_history)
        self.system_metrics: deque = deque(maxlen=max_history)
        
        # Current session tracking
        self.session_start = datetime.now()
        self.current_query_start: Optional[datetime] = None
        self.current_query: Optional[str] = None
        
        # Aggregated statistics
        self.total_queries = 0
        self.successful_queries = 0
        self.total_query_time = 0.0
        self.openai_api_calls = 0
        self.openai_tokens_used = 0
        self.openai_cost_usd = 0.0
        
        # System monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 5.0  # seconds
        
        # Performance thresholds
        self.thresholds = {
            'query_timeout_seconds': 30.0,
            'memory_warning_mb': 1000,
            'cpu_warning_percent': 80.0,
            'success_rate_warning': 0.8
        }
        
        logger.info("Performance monitor initialized")
    
    def start_monitoring(self):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        logger.info("System monitoring stopped")
    
    def start_query(self, query: str):
        """Start monitoring a new query
        
        Args:
            query: The query being executed
        """
        self.current_query_start = datetime.now()
        self.current_query = query
        self.total_queries += 1
        
        logger.debug(f"Started monitoring query: {query[:50]}...")
    
    def end_query(self, success: bool, duration: Optional[float] = None, 
                  result_count: int = 0, error_message: Optional[str] = None):
        """End monitoring current query
        
        Args:
            success: Whether the query was successful
            duration: Query duration in seconds (calculated if not provided)
            result_count: Number of results returned
            error_message: Error message if query failed
        """
        if not self.current_query_start or not self.current_query:
            logger.warning("end_query called without start_query")
            return
        
        # Calculate duration if not provided
        if duration is None:
            duration = (datetime.now() - self.current_query_start).total_seconds()
        
        # Get current system metrics
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()
        
        # Create query metrics
        metrics = QueryMetrics(
            timestamp=self.current_query_start,
            query=self.current_query,
            duration_seconds=duration,
            success=success,
            result_count=result_count,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            error_message=error_message
        )
        
        # Store metrics
        self.query_metrics.append(metrics)
        
        # Update aggregated stats
        if success:
            self.successful_queries += 1
        self.total_query_time += duration
        
        # Check for performance issues
        self._check_performance_warnings(metrics)
        
        # Reset current query tracking
        self.current_query_start = None
        self.current_query = None
        
        logger.debug(f"Query completed in {duration:.2f}s, success: {success}")
    
    def record_openai_usage(self, tokens_used: int, cost_usd: float):
        """Record OpenAI API usage
        
        Args:
            tokens_used: Number of tokens used in the API call
            cost_usd: Cost of the API call in USD
        """
        self.openai_api_calls += 1
        self.openai_tokens_used += tokens_used
        self.openai_cost_usd += cost_usd
        
        logger.debug(f"OpenAI usage: {tokens_used} tokens, ${cost_usd:.4f}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics
        
        Returns:
            Dict with session performance statistics
        """
        session_duration = (datetime.now() - self.session_start).total_seconds()
        success_rate = (self.successful_queries / self.total_queries) if self.total_queries > 0 else 0
        avg_query_time = (self.total_query_time / self.total_queries) if self.total_queries > 0 else 0
        
        # Recent query performance (last 10 queries)
        recent_queries = list(self.query_metrics)[-10:]
        recent_success_rate = sum(1 for q in recent_queries if q.success) / len(recent_queries) if recent_queries else 0
        recent_avg_time = sum(q.duration_seconds for q in recent_queries) / len(recent_queries) if recent_queries else 0
        
        return {
            'session_duration': session_duration,
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'success_rate': success_rate * 100,
            'avg_query_time_seconds': avg_query_time,
            'recent_success_rate': recent_success_rate * 100,
            'recent_avg_time_seconds': recent_avg_time,
            'openai_api_calls': self.openai_api_calls,
            'openai_tokens_used': self.openai_tokens_used,
            'openai_cost_usd': self.openai_cost_usd,
            'queries_per_minute': (self.total_queries / (session_duration / 60)) if session_duration > 0 else 0
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary
        
        Returns:
            Dict with detailed performance analysis
        """
        stats = self.get_session_stats()
        
        # Query performance analysis
        query_times = [q.duration_seconds for q in self.query_metrics]
        if query_times:
            stats['query_performance'] = {
                'min_time': min(query_times),
                'max_time': max(query_times),
                'median_time': sorted(query_times)[len(query_times)//2],
                'p95_time': sorted(query_times)[int(len(query_times) * 0.95)] if len(query_times) > 20 else max(query_times),
                'slow_queries_count': sum(1 for t in query_times if t > self.thresholds['query_timeout_seconds'])
            }
        
        # Error analysis
        errors = [q for q in self.query_metrics if not q.success]
        if errors:
            error_types = defaultdict(int)
            for error in errors:
                error_type = error.error_message.split(':')[0] if error.error_message else 'Unknown'
                error_types[error_type] += 1
            
            stats['error_analysis'] = {
                'total_errors': len(errors),
                'error_types': dict(error_types),
                'most_common_error': max(error_types.keys(), key=error_types.get) if error_types else None
            }
        
        # System resource usage
        if self.system_metrics:
            recent_system = list(self.system_metrics)[-10:]  # Last 10 measurements
            stats['system_performance'] = {
                'avg_cpu_usage': sum(s.cpu_usage_percent for s in recent_system) / len(recent_system),
                'avg_memory_usage_mb': sum(s.memory_usage_mb for s in recent_system) / len(recent_system),
                'avg_memory_usage_percent': sum(s.memory_usage_percent for s in recent_system) / len(recent_system),
                'peak_memory_mb': max(s.memory_usage_mb for s in recent_system),
                'peak_cpu_percent': max(s.cpu_usage_percent for s in recent_system)
            }
        
        # Performance warnings
        warnings = self._generate_performance_warnings(stats)
        if warnings:
            stats['warnings'] = warnings
        
        return stats
    
    def get_query_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent query history
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of query metrics as dictionaries
        """
        recent_queries = list(self.query_metrics)[-limit:]
        return [asdict(q) for q in recent_queries]
    
    def export_metrics(self, filepath: str):
        """Export all metrics to a file
        
        Args:
            filepath: Path to save the metrics file
        """
        try:
            import json
            
            export_data = {
                'session_info': {
                    'start_time': self.session_start.isoformat(),
                    'export_time': datetime.now().isoformat(),
                    'duration_seconds': (datetime.now() - self.session_start).total_seconds()
                },
                'session_stats': self.get_session_stats(),
                'performance_summary': self.get_performance_summary(),
                'query_history': self.get_query_history(),
                'system_metrics': [asdict(s) for s in list(self.system_metrics)[-100:]]  # Last 100 system measurements
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def _monitor_system(self):
        """Background thread for system monitoring"""
        logger.info("System monitoring thread started")
        
        while self.monitoring_active:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Network I/O (if available)
                try:
                    network = psutil.net_io_counters()
                    network_io = {
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv
                    }
                except:
                    network_io = {'bytes_sent': 0, 'bytes_recv': 0}
                
                # Create system metrics
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_usage_percent=cpu_percent,
                    memory_usage_mb=memory.used / (1024 * 1024),
                    memory_usage_percent=memory.percent,
                    disk_usage_percent=disk.percent,
                    network_io_bytes=network_io
                )
                
                self.system_metrics.append(metrics)
                
                # Sleep until next measurement
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(self.monitoring_interval)
        
        logger.info("System monitoring thread stopped")
    
    def _check_performance_warnings(self, metrics: QueryMetrics):
        """Check for performance warnings based on query metrics"""
        warnings = []
        
        # Check query duration
        if metrics.duration_seconds > self.thresholds['query_timeout_seconds']:
            warnings.append(f"Slow query detected: {metrics.duration_seconds:.1f}s")
        
        # Check memory usage
        if metrics.memory_usage_mb > self.thresholds['memory_warning_mb']:
            warnings.append(f"High memory usage: {metrics.memory_usage_mb:.1f}MB")
        
        # Check CPU usage
        if metrics.cpu_usage_percent > self.thresholds['cpu_warning_percent']:
            warnings.append(f"High CPU usage: {metrics.cpu_usage_percent:.1f}%")
        
        # Log warnings
        for warning in warnings:
            logger.warning(warning)
    
    def _generate_performance_warnings(self, stats: Dict[str, Any]) -> List[str]:
        """Generate performance warnings based on session statistics"""
        warnings = []
        
        # Check success rate
        success_rate = stats.get('success_rate', 100) / 100
        if success_rate < self.thresholds['success_rate_warning']:
            warnings.append(f"Low success rate: {success_rate*100:.1f}%")
        
        # Check average query time
        avg_time = stats.get('avg_query_time_seconds', 0)
        if avg_time > self.thresholds['query_timeout_seconds'] / 2:
            warnings.append(f"High average query time: {avg_time:.1f}s")
        
        # Check system resources
        system_perf = stats.get('system_performance', {})
        if system_perf.get('avg_memory_usage_percent', 0) > 80:
            warnings.append("High memory usage detected")
        
        if system_perf.get('avg_cpu_usage', 0) > self.thresholds['cpu_warning_percent']:
            warnings.append("High CPU usage detected")
        
        # Check OpenAI costs
        if stats.get('openai_cost_usd', 0) > 1.0:  # $1 threshold
            warnings.append(f"High OpenAI costs: ${stats['openai_cost_usd']:.2f}")
        
        return warnings
    
    def reset_session(self):
        """Reset all session statistics"""
        self.session_start = datetime.now()
        self.total_queries = 0
        self.successful_queries = 0
        self.total_query_time = 0.0
        self.openai_api_calls = 0
        self.openai_tokens_used = 0
        self.openai_cost_usd = 0.0
        
        # Clear metrics but keep some for comparison
        self.query_metrics.clear()
        self.system_metrics.clear()
        
        logger.info("Session statistics reset")
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics for live monitoring
        
        Returns:
            Dict with current system state and recent performance
        """
        # Current system state
        try:
            current_cpu = psutil.cpu_percent()
            current_memory = psutil.virtual_memory()
            
            system_state = {
                'cpu_percent': current_cpu,
                'memory_percent': current_memory.percent,
                'memory_mb': current_memory.used / (1024 * 1024),
                'available_memory_mb': current_memory.available / (1024 * 1024)
            }
        except:
            system_state = {'error': 'Unable to get system metrics'}
        
        # Recent query performance (last 5 queries)
        recent_queries = list(self.query_metrics)[-5:]
        recent_performance = {
            'recent_queries_count': len(recent_queries),
            'recent_success_rate': (sum(1 for q in recent_queries if q.success) / len(recent_queries) * 100) if recent_queries else 0,
            'recent_avg_time': (sum(q.duration_seconds for q in recent_queries) / len(recent_queries)) if recent_queries else 0
        }
        
        # Current query status
        query_status = {
            'query_in_progress': self.current_query is not None,
            'current_query': self.current_query[:50] + "..." if self.current_query and len(self.current_query) > 50 else self.current_query,
            'query_duration': (datetime.now() - self.current_query_start).total_seconds() if self.current_query_start else 0
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_state': system_state,
            'recent_performance': recent_performance,
            'query_status': query_status,
            'session_totals': {
                'total_queries': self.total_queries,
                'successful_queries': self.successful_queries,
                'session_duration': (datetime.now() - self.session_start).total_seconds()
            }
        }
