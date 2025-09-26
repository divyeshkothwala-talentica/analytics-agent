"""
Main AI Query Engine that integrates all components
"""

import logging
from typing import Dict, List, Optional, Any
from .openai_client import OpenAIClient
from .query_parser import QueryParser
from .query_generator import QueryGenerator
from .correlator import DataCorrelator
from .optimizer import QueryOptimizer
from .query_handlers import QueryHandlers
from ..config.database import get_db
from ..models.schemas import COLLECTION_SCHEMAS

logger = logging.getLogger(__name__)


class AIQueryEngine:
    """Main AI Query Engine for natural language analytics"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the AI Query Engine
        
        Args:
            openai_api_key: OpenAI API key (optional, reads from env if not provided)
        """
        # Initialize database connection
        self.db = get_db()
        
        # Initialize AI components
        self.openai_client = OpenAIClient(openai_api_key)
        self.query_parser = QueryParser()
        self.query_generator = QueryGenerator()
        self.correlator = DataCorrelator(self.db)
        self.optimizer = QueryOptimizer(self.db)
        self.query_handlers = QueryHandlers(self.db, self.openai_client)
        
        # Available collections
        self.available_collections = list(COLLECTION_SCHEMAS.keys())
        
        logger.info("AIQueryEngine initialized successfully")
    
    def process_natural_language_query(self, user_query: str, 
                                     use_ai_parsing: bool = True) -> Dict[str, Any]:
        """Process a natural language query and return results
        
        Args:
            user_query: Natural language query from user
            use_ai_parsing: Whether to use AI for query parsing (vs rule-based)
            
        Returns:
            Dict with query results and metadata
        """
        logger.info(f"Processing query: {user_query}")
        
        try:
            # Step 1: Parse the natural language query
            if use_ai_parsing:
                parsed_query = self.openai_client.parse_natural_language_query(
                    user_query, self.available_collections
                )
            else:
                parsed_query = self.query_parser.parse_query(user_query)
            
            logger.debug(f"Parsed query: {parsed_query}")
            
            # Step 2: Check if this matches a specific use case handler
            handler_result = self._try_specific_handlers(user_query, parsed_query)
            if handler_result:
                return handler_result
            
            # Step 3: Generate MongoDB aggregation pipeline
            collection_schemas = {name: schema.__annotations__ for name, schema in COLLECTION_SCHEMAS.items()}
            
            if use_ai_parsing:
                pipeline = self.openai_client.generate_mongodb_query(parsed_query, collection_schemas)
            else:
                pipeline = self.query_generator.generate_pipeline(parsed_query)
            
            logger.debug(f"Generated pipeline: {pipeline}")
            
            # Step 4: Determine primary collection
            primary_collection = self._determine_primary_collection(parsed_query)
            
            # Step 5: Execute optimized query
            results, execution_metadata = self.optimizer.execute_optimized_query(
                primary_collection, pipeline
            )
            
            # Step 6: Perform correlation analysis if needed
            correlations = None
            if parsed_query.get('intent') in ['why', 'correlation'] or parsed_query.get('aggregation_type') == 'correlation':
                correlations = self._perform_correlation_analysis(parsed_query, results)
            
            # Step 7: Generate natural language explanation
            context = {
                'parsed_query': parsed_query,
                'execution_metadata': execution_metadata,
                'correlations': correlations
            }
            
            explanation = self.openai_client.explain_results(user_query, results, context)
            
            # Step 8: Return comprehensive results
            return {
                'success': True,
                'query': user_query,
                'parsed_query': parsed_query,
                'results': results,
                'result_count': len(results),
                'correlations': correlations,
                'explanation': explanation,
                'metadata': {
                    'execution_metadata': execution_metadata,
                    'primary_collection': primary_collection,
                    'pipeline': pipeline,
                    'processing_time_ms': execution_metadata.get('execution_time_ms', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'query': user_query,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _try_specific_handlers(self, user_query: str, parsed_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to match query with specific use case handlers
        
        Args:
            user_query: Original user query
            parsed_query: Parsed query components
            
        Returns:
            Handler result if matched, None otherwise
        """
        query_lower = user_query.lower()
        
        # City delays handler
        if 'city' in query_lower and 'delay' in query_lower:
            # Extract city name
            locations = parsed_query.get('location_filters', [])
            city = locations[0] if locations else 'unknown'
            
            # Extract date if mentioned
            time_range = parsed_query.get('time_range', {})
            date = time_range.get('start_date')
            
            result = self.query_handlers.handle_city_delays(city, date)
            result['success'] = True
            result['explanation'] = self._generate_handler_explanation(result)
            return result
        
        # Client failures handler
        if 'client' in query_lower and ('fail' in query_lower or 'problem' in query_lower):
            entity_focus = parsed_query.get('entity_focus', {})
            client_id = entity_focus.get('id') or entity_focus.get('name', 'unknown')
            
            # Extract time period
            time_range = parsed_query.get('time_range', {})
            days = 7  # Default
            if 'week' in time_range.get('value', ''):
                days = 7
            elif 'month' in time_range.get('value', ''):
                days = 30
            
            result = self.query_handlers.handle_client_failures(client_id, days)
            result['success'] = True
            result['explanation'] = self._generate_handler_explanation(result)
            return result
        
        # Warehouse efficiency handler
        if 'warehouse' in query_lower and ('efficiency' in query_lower or 'performance' in query_lower):
            entity_focus = parsed_query.get('entity_focus', {})
            warehouse_id = entity_focus.get('id') or entity_focus.get('name', 'unknown')
            
            time_range = parsed_query.get('time_range', {})
            period = 'week'
            if 'month' in time_range.get('value', ''):
                period = 'month'
            
            result = self.query_handlers.handle_warehouse_efficiency(warehouse_id, period)
            result['success'] = True
            result['explanation'] = self._generate_handler_explanation(result)
            return result
        
        # Delivery trends handler
        if 'trend' in query_lower or 'performance' in query_lower:
            time_range = parsed_query.get('time_range', {})
            period = 'month'
            if 'week' in time_range.get('value', ''):
                period = 'week'
            
            result = self.query_handlers.handle_delivery_performance_trends(period)
            result['success'] = True
            result['explanation'] = self._generate_handler_explanation(result)
            return result
        
        # Customer satisfaction handler
        if 'satisfaction' in query_lower or 'feedback' in query_lower:
            result = self.query_handlers.handle_customer_satisfaction_correlation()
            result['success'] = True
            result['explanation'] = self._generate_handler_explanation(result)
            return result
        
        # Peak failure analysis handler
        if 'when' in query_lower and ('fail' in query_lower or 'problem' in query_lower):
            failure_type = 'all'
            if 'delay' in query_lower:
                failure_type = 'delays'
            elif 'cancel' in query_lower:
                failure_type = 'cancellations'
            
            result = self.query_handlers.handle_peak_failure_analysis(failure_type)
            result['success'] = True
            result['explanation'] = self._generate_handler_explanation(result)
            return result
        
        return None
    
    def _determine_primary_collection(self, parsed_query: Dict[str, Any]) -> str:
        """Determine the primary collection for the query"""
        collections_needed = parsed_query.get('collections_needed', ['orders'])
        
        # Priority order for collection selection
        priority_order = ['orders', 'fleet_logs', 'warehouse_logs', 'feedback', 'external_factors']
        
        for collection in priority_order:
            if collection in collections_needed:
                return collection
        
        return collections_needed[0] if collections_needed else 'orders'
    
    def _perform_correlation_analysis(self, parsed_query: Dict[str, Any], 
                                    results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform correlation analysis based on query intent"""
        intent = parsed_query.get('intent', 'general')
        
        if intent == 'why':
            # Analyze root causes
            issue_type = 'delays'
            if 'fail' in parsed_query.get('original_query', '').lower():
                issue_type = 'failures'
            elif 'cancel' in parsed_query.get('original_query', '').lower():
                issue_type = 'cancellations'
            
            return self.correlator.find_root_causes(issue_type)
        
        elif intent == 'correlation':
            # Perform general correlation analysis
            return {
                'temporal': self.correlator.analyze_temporal_correlations(),
                'geographical': self.correlator.analyze_geographical_correlations(),
                'operational': self.correlator.analyze_operational_correlations()
            }
        
        return None
    
    def _generate_handler_explanation(self, handler_result: Dict[str, Any]) -> str:
        """Generate explanation for handler results"""
        query_type = handler_result.get('query_type', 'unknown')
        
        if query_type == 'city_delays':
            insights = handler_result.get('insights', [])
            return ' '.join(insights) if insights else "Analysis completed for city delays."
        
        elif query_type == 'client_failures':
            breakdown = handler_result.get('failure_breakdown', [])
            if breakdown:
                total_failures = sum(item['failure_count'] for item in breakdown)
                return f"Found {total_failures} failures for the client with detailed breakdown by failure stage."
            return "No significant failures found for the specified client."
        
        elif query_type == 'warehouse_efficiency':
            analysis = handler_result.get('efficiency_analysis', {})
            score = analysis.get('efficiency_score', 0)
            ranking = analysis.get('ranking', 'unknown')
            return f"Warehouse efficiency score: {score:.1f}/100, ranking: {ranking}"
        
        elif query_type == 'delivery_performance_trends':
            trend_analysis = handler_result.get('trend_analysis', {})
            trend = trend_analysis.get('trend', 'unknown')
            rate = trend_analysis.get('current_on_time_rate', 0)
            return f"Delivery performance is {trend} with current on-time rate of {rate*100:.1f}%"
        
        elif query_type == 'customer_satisfaction_correlation':
            correlation = handler_result.get('correlation_analysis', {})
            strength = correlation.get('correlation_strength', 'unknown')
            return f"Found {strength} correlation between delivery performance and customer satisfaction"
        
        elif query_type == 'peak_failure_analysis':
            patterns = handler_result.get('peak_analysis', {}).get('patterns', [])
            return ' '.join(patterns) if patterns else "Peak failure analysis completed."
        
        return "Analysis completed successfully."
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the query engine"""
        return {
            'optimizer_stats': self.optimizer.get_performance_stats(),
            'openai_usage': self.openai_client.get_usage_stats(),
            'available_collections': self.available_collections
        }
    
    def clear_cache(self):
        """Clear all caches"""
        self.optimizer.clear_cache()
        logger.info("All caches cleared")
    
    def validate_query(self, user_query: str) -> Dict[str, Any]:
        """Validate a query without executing it
        
        Args:
            user_query: Natural language query
            
        Returns:
            Validation results
        """
        try:
            # Parse query
            parsed_query = self.query_parser.parse_query(user_query)
            
            # Validate parsed query
            is_valid, issues = self.query_parser.validate_parsed_query(parsed_query)
            
            # Generate pipeline for validation
            pipeline = self.query_generator.generate_pipeline(parsed_query)
            
            # Validate pipeline
            pipeline_valid, pipeline_issues = self.query_generator.validate_pipeline(pipeline)
            
            return {
                'valid': is_valid and pipeline_valid,
                'confidence': parsed_query.get('confidence', 0),
                'issues': issues + pipeline_issues,
                'parsed_query': parsed_query,
                'estimated_performance': self.optimizer.analyze_query_performance(pipeline)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'issues': [f"Validation error: {e}"]
            }
