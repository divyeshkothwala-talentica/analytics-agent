"""
Query optimizer with caching and performance monitoring
"""

import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Optimize MongoDB queries with caching and performance monitoring"""
    
    def __init__(self, db_client, cache_ttl_minutes: int = 30, max_cache_size: int = 1000):
        """Initialize query optimizer
        
        Args:
            db_client: MongoDB database client
            cache_ttl_minutes: Cache time-to-live in minutes
            max_cache_size: Maximum number of cached queries
        """
        self.db = db_client
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.max_cache_size = max_cache_size
        
        # Query cache: {query_hash: {result, timestamp, access_count}}
        self.query_cache = {}
        
        # Performance metrics
        self.performance_metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_execution_time': 0,
            'slow_queries': [],
            'query_patterns': defaultdict(int)
        }
        
        # Query optimization rules
        self.optimization_rules = {
            'match_first': True,
            'limit_early': True,
            'index_hints': True,
            'projection_optimization': True
        }
        
        logger.info(f"QueryOptimizer initialized with {cache_ttl_minutes}min cache TTL")
    
    def execute_optimized_query(self, collection_name: str, pipeline: List[Dict[str, Any]], 
                               cache_key: Optional[str] = None) -> Tuple[List[Dict], Dict[str, Any]]:
        """Execute query with optimization and caching
        
        Args:
            collection_name: Name of the collection to query
            pipeline: MongoDB aggregation pipeline
            cache_key: Optional custom cache key
            
        Returns:
            Tuple of (results, execution_metadata)
        """
        start_time = time.time()
        
        # Generate cache key
        if not cache_key:
            cache_key = self._generate_cache_key(collection_name, pipeline)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.performance_metrics['cache_hits'] += 1
            execution_time = time.time() - start_time
            
            metadata = {
                'execution_time_ms': execution_time * 1000,
                'cache_hit': True,
                'optimized_pipeline': pipeline,
                'collection': collection_name
            }
            
            logger.debug(f"Cache hit for query: {cache_key[:16]}...")
            return cached_result, metadata
        
        # Cache miss - optimize and execute query
        self.performance_metrics['cache_misses'] += 1
        optimized_pipeline = self.optimize_pipeline(pipeline)
        
        try:
            # Execute query
            collection = self.db[collection_name]
            results = list(collection.aggregate(optimized_pipeline))
            
            execution_time = time.time() - start_time
            
            # Cache the results
            self._cache_result(cache_key, results)
            
            # Update performance metrics
            self._update_performance_metrics(execution_time, pipeline, results)
            
            metadata = {
                'execution_time_ms': execution_time * 1000,
                'cache_hit': False,
                'optimized_pipeline': optimized_pipeline,
                'original_pipeline': pipeline,
                'result_count': len(results),
                'collection': collection_name
            }
            
            logger.info(f"Query executed in {execution_time*1000:.2f}ms, {len(results)} results")
            return results, metadata
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed after {execution_time*1000:.2f}ms: {e}")
            raise
    
    def optimize_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize MongoDB aggregation pipeline
        
        Args:
            pipeline: Original aggregation pipeline
            
        Returns:
            Optimized pipeline
        """
        if not pipeline:
            return pipeline
        
        optimized = pipeline.copy()
        
        # Apply optimization rules
        if self.optimization_rules['match_first']:
            optimized = self._move_match_stages_early(optimized)
        
        if self.optimization_rules['limit_early']:
            optimized = self._add_early_limits(optimized)
        
        if self.optimization_rules['projection_optimization']:
            optimized = self._optimize_projections(optimized)
        
        # Add performance hints
        optimized = self._add_performance_hints(optimized)
        
        return optimized
    
    def _move_match_stages_early(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Move $match stages as early as possible in the pipeline"""
        optimized = []
        match_stages = []
        other_stages = []
        
        for stage in pipeline:
            if '$match' in stage:
                match_stages.append(stage)
            else:
                other_stages.append(stage)
        
        # Add match stages first, then other stages
        optimized.extend(match_stages)
        optimized.extend(other_stages)
        
        return optimized
    
    def _add_early_limits(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add early $limit stages to reduce data processing"""
        optimized = []
        has_limit = any('$limit' in stage for stage in pipeline)
        has_sort = any('$sort' in stage for stage in pipeline)
        
        for i, stage in enumerate(pipeline):
            optimized.append(stage)
            
            # Add limit after match and before expensive operations
            if ('$match' in stage and not has_limit and 
                i < len(pipeline) - 1 and 
                any(op in pipeline[i+1] for op in ['$lookup', '$group', '$unwind'])):
                
                # Add a reasonable limit to prevent processing too much data
                optimized.append({'$limit': 10000})
        
        return optimized
    
    def _optimize_projections(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize $project stages to reduce data transfer"""
        optimized = []
        
        for stage in pipeline:
            if '$project' in stage:
                # Remove unnecessary fields from projection
                project_stage = stage.copy()
                projection = project_stage['$project']
                
                # Remove fields that are set to 1 but not used later
                # This is a simplified optimization
                optimized_projection = {k: v for k, v in projection.items() 
                                      if v != 0}  # Keep non-exclusion fields
                
                if optimized_projection:
                    project_stage['$project'] = optimized_projection
                    optimized.append(project_stage)
            else:
                optimized.append(stage)
        
        return optimized
    
    def _add_performance_hints(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add performance hints to the pipeline"""
        # Add allowDiskUse for large aggregations
        if len(pipeline) > 5 or any('$group' in stage for stage in pipeline):
            # This would be added to the aggregation options, not the pipeline itself
            pass
        
        return pipeline
    
    def _generate_cache_key(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> str:
        """Generate a unique cache key for the query"""
        query_string = f"{collection_name}:{json.dumps(pipeline, sort_keys=True)}"
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached result if available and not expired"""
        if cache_key not in self.query_cache:
            return None
        
        cached_entry = self.query_cache[cache_key]
        
        # Check if cache entry is expired
        if datetime.now() - cached_entry['timestamp'] > self.cache_ttl:
            del self.query_cache[cache_key]
            return None
        
        # Update access count
        cached_entry['access_count'] += 1
        
        return cached_entry['result']
    
    def _cache_result(self, cache_key: str, results: List[Dict]):
        """Cache query results"""
        # Implement LRU eviction if cache is full
        if len(self.query_cache) >= self.max_cache_size:
            self._evict_least_used()
        
        self.query_cache[cache_key] = {
            'result': results,
            'timestamp': datetime.now(),
            'access_count': 1
        }
    
    def _evict_least_used(self):
        """Evict least recently used cache entries"""
        if not self.query_cache:
            return
        
        # Find entries to evict (oldest and least accessed)
        entries_by_usage = sorted(
            self.query_cache.items(),
            key=lambda x: (x[1]['access_count'], x[1]['timestamp'])
        )
        
        # Remove 20% of cache entries
        num_to_remove = max(1, len(entries_by_usage) // 5)
        
        for i in range(num_to_remove):
            cache_key = entries_by_usage[i][0]
            del self.query_cache[cache_key]
        
        logger.info(f"Evicted {num_to_remove} cache entries")
    
    def _update_performance_metrics(self, execution_time: float, pipeline: List[Dict], results: List[Dict]):
        """Update performance metrics"""
        self.performance_metrics['total_queries'] += 1
        
        # Update average execution time
        total_time = (self.performance_metrics['avg_execution_time'] * 
                     (self.performance_metrics['total_queries'] - 1) + execution_time)
        self.performance_metrics['avg_execution_time'] = total_time / self.performance_metrics['total_queries']
        
        # Track slow queries (> 5 seconds)
        if execution_time > 5.0:
            slow_query = {
                'pipeline': pipeline,
                'execution_time': execution_time,
                'result_count': len(results),
                'timestamp': datetime.now().isoformat()
            }
            self.performance_metrics['slow_queries'].append(slow_query)
            
            # Keep only last 50 slow queries
            if len(self.performance_metrics['slow_queries']) > 50:
                self.performance_metrics['slow_queries'] = self.performance_metrics['slow_queries'][-50:]
        
        # Track query patterns
        pattern = self._extract_query_pattern(pipeline)
        self.performance_metrics['query_patterns'][pattern] += 1
    
    def _extract_query_pattern(self, pipeline: List[Dict[str, Any]]) -> str:
        """Extract a pattern signature from the pipeline"""
        if not pipeline:
            return 'empty'
        
        # Create a pattern based on stage types
        stages = []
        for stage in pipeline:
            stage_type = list(stage.keys())[0] if stage else 'unknown'
            stages.append(stage_type)
        
        return ' -> '.join(stages)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        cache_hit_rate = (self.performance_metrics['cache_hits'] / 
                         max(1, self.performance_metrics['total_queries'])) * 100
        
        return {
            'total_queries': self.performance_metrics['total_queries'],
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_hits': self.performance_metrics['cache_hits'],
            'cache_misses': self.performance_metrics['cache_misses'],
            'avg_execution_time_ms': round(self.performance_metrics['avg_execution_time'] * 1000, 2),
            'slow_queries_count': len(self.performance_metrics['slow_queries']),
            'cache_size': len(self.query_cache),
            'top_query_patterns': dict(sorted(
                self.performance_metrics['query_patterns'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
        }
    
    def clear_cache(self):
        """Clear the query cache"""
        self.query_cache.clear()
        logger.info("Query cache cleared")
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries for analysis"""
        return sorted(
            self.performance_metrics['slow_queries'],
            key=lambda x: x['execution_time'],
            reverse=True
        )[:limit]
    
    def optimize_collection_indexes(self, collection_name: str, 
                                  recent_queries: List[List[Dict[str, Any]]]) -> List[str]:
        """Suggest indexes based on recent query patterns
        
        Args:
            collection_name: Name of the collection
            recent_queries: List of recent query pipelines
            
        Returns:
            List of suggested index creation commands
        """
        index_suggestions = []
        field_usage = defaultdict(int)
        
        # Analyze field usage in match stages
        for pipeline in recent_queries:
            for stage in pipeline:
                if '$match' in stage:
                    match_conditions = stage['$match']
                    for field in self._extract_fields_from_match(match_conditions):
                        field_usage[field] += 1
        
        # Suggest indexes for frequently used fields
        for field, usage_count in field_usage.items():
            if usage_count >= 3:  # Used in at least 3 queries
                index_suggestions.append(f"db.{collection_name}.createIndex({{\"{field}\": 1}})")
        
        return index_suggestions
    
    def _extract_fields_from_match(self, match_conditions: Dict[str, Any]) -> List[str]:
        """Extract field names from match conditions"""
        fields = []
        
        for key, value in match_conditions.items():
            if key.startswith('$'):
                # Handle operators like $and, $or
                if isinstance(value, list):
                    for condition in value:
                        if isinstance(condition, dict):
                            fields.extend(self._extract_fields_from_match(condition))
            else:
                fields.append(key)
        
        return fields
    
    def reset_performance_metrics(self):
        """Reset performance metrics"""
        self.performance_metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_execution_time': 0,
            'slow_queries': [],
            'query_patterns': defaultdict(int)
        }
        logger.info("Performance metrics reset")
    
    def set_optimization_rules(self, rules: Dict[str, bool]):
        """Update optimization rules
        
        Args:
            rules: Dict of rule names and their enabled status
        """
        self.optimization_rules.update(rules)
        logger.info(f"Optimization rules updated: {rules}")
    
    def analyze_query_performance(self, pipeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze potential performance issues in a query pipeline
        
        Args:
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            Dict with performance analysis
        """
        issues = []
        recommendations = []
        complexity_score = 0
        
        # Analyze pipeline stages
        has_match = False
        match_position = -1
        has_sort_without_limit = False
        lookup_count = 0
        
        for i, stage in enumerate(pipeline):
            stage_type = list(stage.keys())[0]
            
            if stage_type == '$match':
                has_match = True
                match_position = i
            elif stage_type == '$sort':
                # Check if there's a limit after sort
                has_limit_after = any('$limit' in pipeline[j] for j in range(i+1, len(pipeline)))
                if not has_limit_after:
                    has_sort_without_limit = True
            elif stage_type == '$lookup':
                lookup_count += 1
                complexity_score += 2
            elif stage_type == '$group':
                complexity_score += 1
            elif stage_type == '$unwind':
                complexity_score += 1
        
        # Generate issues and recommendations
        if not has_match:
            issues.append("No $match stage found - query may process unnecessary data")
            recommendations.append("Add $match stage early in pipeline to filter data")
        elif match_position > 2:
            issues.append("$match stage appears late in pipeline")
            recommendations.append("Move $match stages earlier for better performance")
        
        if has_sort_without_limit:
            issues.append("$sort without $limit may cause memory issues")
            recommendations.append("Add $limit after $sort operations")
        
        if lookup_count > 3:
            issues.append(f"Many $lookup stages ({lookup_count}) may impact performance")
            recommendations.append("Consider denormalizing data or using fewer lookups")
        
        if complexity_score > 10:
            issues.append("High complexity pipeline may be slow")
            recommendations.append("Consider breaking into multiple simpler queries")
        
        return {
            'complexity_score': complexity_score,
            'issues': issues,
            'recommendations': recommendations,
            'estimated_performance': 'good' if complexity_score < 5 else 'moderate' if complexity_score < 10 else 'poor'
        }
