"""
MongoDB query generator for converting parsed queries into aggregation pipelines
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dateutil.parser import parse as parse_date

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generate MongoDB aggregation pipelines from parsed natural language queries"""
    
    def __init__(self):
        """Initialize query generator with collection schemas and patterns"""
        
        # Collection field mappings
        self.field_mappings = {
            'orders': {
                'id': 'order_id',
                'client': 'client_id',
                'warehouse': 'warehouse_id',
                'driver': 'driver_id',
                'date': 'order_date',
                'delivery_date': 'delivery_date',
                'status': 'status',
                'amount': 'total_amount',
                'priority': 'priority'
            },
            'warehouse_logs': {
                'id': 'log_id',
                'warehouse': 'warehouse_id',
                'order': 'order_id',
                'operation': 'operation_type',
                'timestamp': 'timestamp',
                'operator': 'operator_id',
                'status': 'status',
                'processing_time': 'processing_time_minutes'
            },
            'fleet_logs': {
                'id': 'log_id',
                'driver': 'driver_id',
                'order': 'order_id',
                'vehicle': 'vehicle_id',
                'timestamp': 'timestamp',
                'event': 'event_type',
                'location': 'location',
                'status': 'status',
                'delay': 'delay_minutes'
            },
            'external_factors': {
                'id': 'factor_id',
                'date': 'date',
                'location': 'location',
                'type': 'factor_type',
                'severity': 'severity',
                'description': 'description',
                'impact': 'impact_areas'
            },
            'feedback': {
                'id': 'feedback_id',
                'order': 'order_id',
                'client': 'client_id',
                'date': 'feedback_date',
                'rating': 'rating',
                'category': 'category',
                'comments': 'comments'
            }
        }
        
        # Status mappings
        self.status_mappings = {
            'failed': ['failed', 'failure', 'unsuccessful'],
            'delayed': ['delayed', 'late'],
            'cancelled': ['cancelled', 'canceled', 'aborted'],
            'completed': ['completed', 'delivered', 'successful'],
            'pending': ['pending', 'processing', 'in_progress']
        }
        
        logger.info("QueryGenerator initialized with field mappings")
    
    def generate_pipeline(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate MongoDB aggregation pipeline from parsed query
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            List of aggregation pipeline stages
        """
        pipeline = []
        
        # Determine primary collection
        primary_collection = self._get_primary_collection(parsed_query)
        
        # Add initial match stage for filters
        match_stage = self._build_match_stage(parsed_query, primary_collection)
        if match_stage:
            pipeline.append(match_stage)
        
        # Add lookup stages for cross-collection queries
        lookup_stages = self._build_lookup_stages(parsed_query, primary_collection)
        pipeline.extend(lookup_stages)
        
        # Add aggregation stages based on intent
        agg_stages = self._build_aggregation_stages(parsed_query)
        pipeline.extend(agg_stages)
        
        # Add sorting and limiting
        sort_limit_stages = self._build_sort_limit_stages(parsed_query)
        pipeline.extend(sort_limit_stages)
        
        # Add final projection
        project_stage = self._build_project_stage(parsed_query)
        if project_stage:
            pipeline.append(project_stage)
        
        logger.info(f"Generated pipeline with {len(pipeline)} stages for collection: {primary_collection}")
        return pipeline
    
    def _get_primary_collection(self, parsed_query: Dict[str, Any]) -> str:
        """Determine the primary collection for the query
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            Primary collection name
        """
        collections_needed = parsed_query.get('collections_needed', ['orders'])
        
        # Priority order for primary collection selection
        priority_order = ['orders', 'fleet_logs', 'warehouse_logs', 'feedback', 'external_factors']
        
        for collection in priority_order:
            if collection in collections_needed:
                return collection
        
        return collections_needed[0] if collections_needed else 'orders'
    
    def _build_match_stage(self, parsed_query: Dict[str, Any], collection: str) -> Optional[Dict[str, Any]]:
        """Build the initial $match stage for filtering
        
        Args:
            parsed_query: Parsed query components
            collection: Primary collection name
            
        Returns:
            Match stage dict or None
        """
        match_conditions = {}
        
        # Time range filters
        time_range = parsed_query.get('time_range', {})
        if time_range.get('start_date') or time_range.get('end_date'):
            date_field = self._get_date_field(collection)
            date_filter = {}
            
            if time_range.get('start_date'):
                date_filter['$gte'] = time_range['start_date']
            if time_range.get('end_date'):
                date_filter['$lte'] = time_range['end_date']
            
            if date_filter:
                match_conditions[date_field] = date_filter
        
        # Status filters
        filters = parsed_query.get('filters', {})
        if filters.get('status'):
            status_values = []
            for status in filters['status']:
                status_values.extend(self.status_mappings.get(status, [status]))
            
            if status_values:
                match_conditions['status'] = {'$in': status_values}
        
        # Priority filters
        if filters.get('priority'):
            match_conditions['priority'] = {'$in': filters['priority']}
        
        # Entity filters
        entity_focus = parsed_query.get('entity_focus', {})
        if entity_focus.get('type') != 'general' and entity_focus.get('id'):
            entity_field = self._get_entity_field(collection, entity_focus['type'])
            if entity_field:
                match_conditions[entity_field] = entity_focus['id']
        
        # Location filters
        location_filters = parsed_query.get('location_filters', [])
        if location_filters and collection in ['orders', 'external_factors']:
            # For orders, we might need to join with warehouses for location
            # For external_factors, we can filter directly
            if collection == 'external_factors':
                match_conditions['location'] = {'$in': location_filters}
        
        return {'$match': match_conditions} if match_conditions else None
    
    def _build_lookup_stages(self, parsed_query: Dict[str, Any], primary_collection: str) -> List[Dict[str, Any]]:
        """Build $lookup stages for cross-collection queries
        
        Args:
            parsed_query: Parsed query components
            primary_collection: Primary collection name
            
        Returns:
            List of lookup stages
        """
        lookup_stages = []
        collections_needed = parsed_query.get('collections_needed', [])
        
        # Define lookup relationships
        lookup_relationships = {
            'orders': {
                'warehouse_logs': {'localField': 'order_id', 'foreignField': 'order_id'},
                'fleet_logs': {'localField': 'order_id', 'foreignField': 'order_id'},
                'feedback': {'localField': 'order_id', 'foreignField': 'order_id'},
                'clients': {'localField': 'client_id', 'foreignField': 'client_id'},
                'warehouses': {'localField': 'warehouse_id', 'foreignField': 'warehouse_id'},
                'drivers': {'localField': 'driver_id', 'foreignField': 'driver_id'}
            },
            'warehouse_logs': {
                'orders': {'localField': 'order_id', 'foreignField': 'order_id'},
                'warehouses': {'localField': 'warehouse_id', 'foreignField': 'warehouse_id'}
            },
            'fleet_logs': {
                'orders': {'localField': 'order_id', 'foreignField': 'order_id'},
                'drivers': {'localField': 'driver_id', 'foreignField': 'driver_id'}
            },
            'feedback': {
                'orders': {'localField': 'order_id', 'foreignField': 'order_id'},
                'clients': {'localField': 'client_id', 'foreignField': 'client_id'}
            }
        }
        
        # Add external factors lookup based on date/location correlation
        if 'external_factors' in collections_needed and primary_collection != 'external_factors':
            lookup_stages.append({
                '$lookup': {
                    'from': 'external_factors',
                    'let': {'order_date': f'${self._get_date_field(primary_collection)}'},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        {'$gte': ['$$order_date', '$date']},
                                        {'$lte': ['$$order_date', {'$add': ['$date', {'$multiply': ['$duration_hours', 3600000]}]}]}
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'external_factors'
                }
            })
        
        # Add standard lookups
        if primary_collection in lookup_relationships:
            for collection in collections_needed:
                if collection != primary_collection and collection in lookup_relationships[primary_collection]:
                    relationship = lookup_relationships[primary_collection][collection]
                    lookup_stages.append({
                        '$lookup': {
                            'from': collection,
                            'localField': relationship['localField'],
                            'foreignField': relationship['foreignField'],
                            'as': collection
                        }
                    })
        
        return lookup_stages
    
    def _build_aggregation_stages(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build aggregation stages based on query intent
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            List of aggregation stages
        """
        stages = []
        aggregation_type = parsed_query.get('aggregation_type', 'analysis')
        intent = parsed_query.get('intent', 'general')
        
        if aggregation_type == 'count':
            stages.append({
                '$group': {
                    '_id': None,
                    'total_count': {'$sum': 1}
                }
            })
        
        elif aggregation_type == 'group_by':
            group_field = self._determine_group_field(parsed_query)
            stages.append({
                '$group': {
                    '_id': f'${group_field}',
                    'count': {'$sum': 1},
                    'avg_amount': {'$avg': '$total_amount'}
                }
            })
        
        elif aggregation_type == 'average':
            metric_field = self._determine_metric_field(parsed_query)
            stages.append({
                '$group': {
                    '_id': None,
                    'average_value': {'$avg': f'${metric_field}'}
                }
            })
        
        elif aggregation_type == 'sum':
            metric_field = self._determine_metric_field(parsed_query)
            stages.append({
                '$group': {
                    '_id': None,
                    'total_value': {'$sum': f'${metric_field}'}
                }
            })
        
        elif aggregation_type == 'ranking':
            group_field = self._determine_group_field(parsed_query)
            stages.extend([
                {
                    '$group': {
                        '_id': f'${group_field}',
                        'count': {'$sum': 1},
                        'total_amount': {'$sum': '$total_amount'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ])
        
        elif intent == 'why' or aggregation_type == 'correlation':
            # For "why" questions, group by potential causes
            stages.extend([
                {
                    '$group': {
                        '_id': {
                            'status': '$status',
                            'priority': '$priority'
                        },
                        'count': {'$sum': 1},
                        'avg_delay': {'$avg': '$fleet_logs.delay_minutes'},
                        'external_factors': {'$push': '$external_factors'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ])
        
        return stages
    
    def _build_sort_limit_stages(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build sorting and limiting stages
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            List of sort/limit stages
        """
        stages = []
        
        # Default sorting based on aggregation type
        aggregation_type = parsed_query.get('aggregation_type', 'analysis')
        
        if aggregation_type in ['ranking', 'group_by']:
            # Already added sorting in aggregation stages
            pass
        elif aggregation_type == 'analysis':
            # Sort by date for general analysis
            date_field = self._get_date_field(self._get_primary_collection(parsed_query))
            stages.append({'$sort': {date_field: -1}})
        
        # Add limit for performance
        limit = 100  # Default limit
        if 'top' in parsed_query.get('original_query', '').lower():
            # Extract number if mentioned (e.g., "top 10")
            import re
            numbers = re.findall(r'\btop\s+(\d+)', parsed_query.get('original_query', '').lower())
            if numbers:
                limit = min(int(numbers[0]), 100)
            else:
                limit = 10
        
        stages.append({'$limit': limit})
        
        return stages
    
    def _build_project_stage(self, parsed_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build final projection stage
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            Project stage dict or None
        """
        # Build projection based on what information is most relevant
        intent = parsed_query.get('intent', 'general')
        metrics = parsed_query.get('metrics', [])
        
        projection = {}
        
        if intent == 'why':
            projection = {
                '_id': 1,
                'count': 1,
                'avg_delay': 1,
                'external_factors': 1
            }
        elif 'delays' in metrics:
            projection = {
                'order_id': 1,
                'status': 1,
                'delay_minutes': '$fleet_logs.delay_minutes',
                'delivery_date': 1,
                'external_factors': 1
            }
        elif 'failures' in metrics:
            projection = {
                'order_id': 1,
                'status': 1,
                'failure_reason': 1,
                'warehouse_logs': 1,
                'fleet_logs': 1
            }
        
        return {'$project': projection} if projection else None
    
    def _get_date_field(self, collection: str) -> str:
        """Get the primary date field for a collection
        
        Args:
            collection: Collection name
            
        Returns:
            Date field name
        """
        date_fields = {
            'orders': 'order_date',
            'warehouse_logs': 'timestamp',
            'fleet_logs': 'timestamp',
            'external_factors': 'date',
            'feedback': 'feedback_date'
        }
        
        return date_fields.get(collection, 'created_at')
    
    def _get_entity_field(self, collection: str, entity_type: str) -> Optional[str]:
        """Get the field name for an entity type in a collection
        
        Args:
            collection: Collection name
            entity_type: Type of entity (client, driver, etc.)
            
        Returns:
            Field name or None
        """
        if collection in self.field_mappings and entity_type in self.field_mappings[collection]:
            return self.field_mappings[collection][entity_type]
        return None
    
    def _determine_group_field(self, parsed_query: Dict[str, Any]) -> str:
        """Determine the field to group by based on query
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            Field name for grouping
        """
        entity_focus = parsed_query.get('entity_focus', {})
        
        if entity_focus.get('type') == 'client':
            return 'client_id'
        elif entity_focus.get('type') == 'driver':
            return 'driver_id'
        elif entity_focus.get('type') == 'warehouse':
            return 'warehouse_id'
        elif 'failures' in parsed_query.get('metrics', []):
            return 'status'
        else:
            return 'status'  # Default grouping
    
    def _determine_metric_field(self, parsed_query: Dict[str, Any]) -> str:
        """Determine the metric field based on query
        
        Args:
            parsed_query: Parsed query components
            
        Returns:
            Field name for metrics
        """
        metrics = parsed_query.get('metrics', [])
        
        if 'costs' in metrics:
            return 'total_amount'
        elif 'delays' in metrics:
            return 'fleet_logs.delay_minutes'
        elif 'efficiency' in metrics:
            return 'warehouse_logs.processing_time_minutes'
        elif 'ratings' in metrics:
            return 'feedback.rating'
        else:
            return 'total_amount'  # Default metric
    
    def validate_pipeline(self, pipeline: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """Validate the generated pipeline
        
        Args:
            pipeline: Generated aggregation pipeline
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not pipeline:
            issues.append("Empty pipeline generated")
            return False, issues
        
        # Check for required stages
        stage_types = [list(stage.keys())[0] for stage in pipeline]
        
        # Validate stage order
        if '$match' in stage_types and '$lookup' in stage_types:
            match_index = stage_types.index('$match')
            lookup_indices = [i for i, stage in enumerate(stage_types) if stage == '$lookup']
            if lookup_indices and match_index > min(lookup_indices):
                issues.append("$match stage should come before $lookup stages for better performance")
        
        # Check for potential performance issues
        if len(pipeline) > 10:
            issues.append("Pipeline has many stages, consider optimization")
        
        # Validate stage structure
        for i, stage in enumerate(pipeline):
            if not isinstance(stage, dict) or len(stage) != 1:
                issues.append(f"Invalid stage structure at index {i}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
