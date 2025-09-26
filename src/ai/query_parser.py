"""
Natural language query parser for extracting structured information
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class QueryParser:
    """Parse natural language queries to extract structured information"""
    
    def __init__(self):
        """Initialize query parser with pattern definitions"""
        
        # Time-related patterns
        self.time_patterns = {
            'yesterday': lambda: (datetime.now() - timedelta(days=1)).date(),
            'today': lambda: datetime.now().date(),
            'last week': lambda: (datetime.now() - timedelta(weeks=1)).date(),
            'this week': lambda: datetime.now().date(),
            'last month': lambda: (datetime.now() - relativedelta(months=1)).date(),
            'this month': lambda: datetime.now().date(),
            'last year': lambda: (datetime.now() - relativedelta(years=1)).date(),
        }
        
        # Intent patterns
        self.intent_patterns = {
            'why': ['why', 'reason', 'cause', 'explain', 'what caused'],
            'compare': ['compare', 'vs', 'versus', 'difference', 'better', 'worse'],
            'predict': ['predict', 'forecast', 'future', 'will', 'expect'],
            'trend': ['trend', 'pattern', 'over time', 'increasing', 'decreasing'],
            'top_reasons': ['top', 'main', 'primary', 'biggest', 'most common'],
            'correlation': ['correlate', 'relationship', 'impact', 'affect', 'influence']
        }
        
        # Metric patterns
        self.metric_patterns = {
            'delays': ['delay', 'late', 'behind schedule', 'overdue'],
            'failures': ['fail', 'failed', 'failure', 'unsuccessful', 'error'],
            'cancellations': ['cancel', 'cancelled', 'cancellation', 'abort'],
            'ratings': ['rating', 'score', 'feedback', 'satisfaction'],
            'efficiency': ['efficiency', 'performance', 'productivity'],
            'costs': ['cost', 'expense', 'price', 'budget'],
            'revenue': ['revenue', 'income', 'profit', 'earnings']
        }
        
        # Location patterns
        self.location_patterns = [
            r'in\s+([A-Za-z\s]+?)(?:\s|$|,)',
            r'city\s+([A-Za-z\s]+?)(?:\s|$|,)',
            r'warehouse\s+([A-Za-z0-9\s]+?)(?:\s|$|,)',
            r'location\s+([A-Za-z\s]+?)(?:\s|$|,)'
        ]
        
        # Entity patterns
        self.entity_patterns = {
            'client': [r'client\s+([A-Za-z0-9\s]+?)(?:\s|$|,)', r'customer\s+([A-Za-z0-9\s]+?)(?:\s|$|,)'],
            'driver': [r'driver\s+([A-Za-z0-9\s]+?)(?:\s|$|,)'],
            'order': [r'order\s+([A-Za-z0-9\s]+?)(?:\s|$|,)'],
            'warehouse': [r'warehouse\s+([A-Za-z0-9\s]+?)(?:\s|$|,)']
        }
        
        logger.info("QueryParser initialized with pattern definitions")
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured components
        
        Args:
            query: Natural language query string
            
        Returns:
            Dict with parsed query components
        """
        query_lower = query.lower()
        
        parsed = {
            'original_query': query,
            'intent': self._extract_intent(query_lower),
            'time_range': self._extract_time_range(query_lower),
            'location_filters': self._extract_locations(query_lower),
            'entity_focus': self._extract_entities(query_lower),
            'metrics': self._extract_metrics(query_lower),
            'collections_needed': self._determine_collections(query_lower),
            'filters': self._extract_filters(query_lower),
            'aggregation_type': self._determine_aggregation_type(query_lower),
            'confidence': self._calculate_confidence(query_lower)
        }
        
        logger.info(f"Parsed query with confidence: {parsed['confidence']:.2f}")
        return parsed
    
    def _extract_intent(self, query: str) -> str:
        """Extract the main intent from the query
        
        Args:
            query: Lowercase query string
            
        Returns:
            Intent type string
        """
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return intent
        
        # Default intent based on question words
        if any(word in query for word in ['what', 'which', 'how many']):
            return 'analysis'
        elif any(word in query for word in ['when', 'how long']):
            return 'temporal'
        else:
            return 'general'
    
    def _extract_time_range(self, query: str) -> Dict[str, Any]:
        """Extract time range information from query
        
        Args:
            query: Lowercase query string
            
        Returns:
            Dict with time range information
        """
        time_range = {
            'type': 'none',
            'value': None,
            'start_date': None,
            'end_date': None
        }
        
        # Check for relative time patterns
        for pattern, date_func in self.time_patterns.items():
            if pattern in query:
                time_range['type'] = 'relative'
                time_range['value'] = pattern
                
                if 'last' in pattern:
                    time_range['end_date'] = date_func().isoformat()
                    if 'week' in pattern:
                        time_range['start_date'] = (date_func() - timedelta(days=7)).isoformat()
                    elif 'month' in pattern:
                        time_range['start_date'] = (date_func() - timedelta(days=30)).isoformat()
                    elif 'year' in pattern:
                        time_range['start_date'] = (date_func() - timedelta(days=365)).isoformat()
                else:
                    time_range['start_date'] = date_func().isoformat()
                    time_range['end_date'] = date_func().isoformat()
                break
        
        # Check for specific dates
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query)
            if matches:
                try:
                    parsed_date = parse_date(matches[0]).date()
                    time_range['type'] = 'absolute'
                    time_range['value'] = matches[0]
                    time_range['start_date'] = parsed_date.isoformat()
                    time_range['end_date'] = parsed_date.isoformat()
                    break
                except Exception as e:
                    logger.warning(f"Failed to parse date {matches[0]}: {e}")
        
        return time_range
    
    def _extract_locations(self, query: str) -> List[str]:
        """Extract location information from query
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of location strings
        """
        locations = []
        
        for pattern in self.location_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                location = match.strip()
                if location and location not in locations:
                    locations.append(location)
        
        return locations
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entity focus from query
        
        Args:
            query: Lowercase query string
            
        Returns:
            Dict with entity information
        """
        entity_focus = {
            'type': 'general',
            'id': None,
            'name': None
        }
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                if matches:
                    entity_focus['type'] = entity_type
                    entity_focus['name'] = matches[0].strip()
                    # Try to extract ID if it looks like one
                    if re.match(r'^[A-Z0-9_-]+$', matches[0].strip()):
                        entity_focus['id'] = matches[0].strip()
                    return entity_focus
        
        return entity_focus
    
    def _extract_metrics(self, query: str) -> List[str]:
        """Extract metrics mentioned in query
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of metric strings
        """
        metrics = []
        
        for metric, patterns in self.metric_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    if metric not in metrics:
                        metrics.append(metric)
                    break
        
        return metrics
    
    def _determine_collections(self, query: str) -> List[str]:
        """Determine which collections are needed for the query
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of collection names
        """
        collections = set()
        
        # Collection keywords mapping
        collection_keywords = {
            'orders': ['order', 'delivery', 'shipment', 'purchase'],
            'warehouse_logs': ['warehouse', 'inventory', 'stock', 'pick', 'pack'],
            'fleet_logs': ['driver', 'vehicle', 'fleet', 'route', 'delivery'],
            'external_factors': ['weather', 'traffic', 'holiday', 'event', 'strike'],
            'feedback': ['feedback', 'rating', 'review', 'satisfaction', 'complaint'],
            'clients': ['client', 'customer', 'company'],
            'warehouses': ['warehouse', 'facility', 'location'],
            'drivers': ['driver', 'operator', 'personnel']
        }
        
        for collection, keywords in collection_keywords.items():
            if any(keyword in query for keyword in keywords):
                collections.add(collection)
        
        # Always include orders as it's central to most queries
        if not collections:
            collections.add('orders')
        
        return list(collections)
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filter conditions from query
        
        Args:
            query: Lowercase query string
            
        Returns:
            Dict with filter conditions
        """
        filters = {
            'status': [],
            'priority': [],
            'other': {}
        }
        
        # Status filters
        status_keywords = {
            'failed': ['failed', 'failure', 'unsuccessful'],
            'delayed': ['delayed', 'late', 'overdue'],
            'cancelled': ['cancelled', 'canceled', 'aborted'],
            'completed': ['completed', 'successful', 'delivered'],
            'pending': ['pending', 'waiting', 'in progress']
        }
        
        for status, keywords in status_keywords.items():
            if any(keyword in query for keyword in keywords):
                filters['status'].append(status)
        
        # Priority filters
        priority_keywords = {
            'high': ['high priority', 'urgent', 'critical'],
            'medium': ['medium priority', 'normal'],
            'low': ['low priority', 'routine']
        }
        
        for priority, keywords in priority_keywords.items():
            if any(keyword in query for keyword in keywords):
                filters['priority'].append(priority)
        
        return filters
    
    def _determine_aggregation_type(self, query: str) -> str:
        """Determine the type of aggregation needed
        
        Args:
            query: Lowercase query string
            
        Returns:
            Aggregation type string
        """
        if any(word in query for word in ['count', 'how many', 'number of']):
            return 'count'
        elif any(word in query for word in ['average', 'avg', 'mean']):
            return 'average'
        elif any(word in query for word in ['total', 'sum']):
            return 'sum'
        elif any(word in query for word in ['group', 'by', 'breakdown']):
            return 'group_by'
        elif any(word in query for word in ['correlate', 'relationship', 'impact']):
            return 'correlation'
        elif any(word in query for word in ['top', 'bottom', 'best', 'worst']):
            return 'ranking'
        else:
            return 'analysis'
    
    def _calculate_confidence(self, query: str) -> float:
        """Calculate confidence score for the parsing
        
        Args:
            query: Lowercase query string
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence for clear patterns
        if any(pattern in query for patterns in self.intent_patterns.values() for pattern in patterns):
            confidence += 0.2
        
        if any(pattern in query for pattern in self.time_patterns.keys()):
            confidence += 0.15
        
        if any(keyword in query for keywords in self.metric_patterns.values() for keyword in keywords):
            confidence += 0.15
        
        # Decrease confidence for very short or unclear queries
        if len(query.split()) < 3:
            confidence -= 0.2
        
        if '?' not in query and not any(word in query for word in ['why', 'what', 'how', 'when', 'where']):
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def validate_parsed_query(self, parsed_query: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate parsed query for completeness and correctness
        
        Args:
            parsed_query: Parsed query dict
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        required_fields = ['intent', 'collections_needed', 'aggregation_type']
        for field in required_fields:
            if not parsed_query.get(field):
                issues.append(f"Missing or empty field: {field}")
        
        # Check confidence threshold
        if parsed_query.get('confidence', 0) < 0.3:
            issues.append("Low confidence in query parsing")
        
        # Check if collections are valid
        valid_collections = ['orders', 'warehouse_logs', 'fleet_logs', 'external_factors', 
                           'feedback', 'clients', 'warehouses', 'drivers']
        
        for collection in parsed_query.get('collections_needed', []):
            if collection not in valid_collections:
                issues.append(f"Invalid collection: {collection}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
