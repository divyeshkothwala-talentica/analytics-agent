"""
Query handlers for the 6 sample use cases
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .openai_client import OpenAIClient
from .query_parser import QueryParser
from .query_generator import QueryGenerator
from .correlator import DataCorrelator
from .optimizer import QueryOptimizer

logger = logging.getLogger(__name__)


class QueryHandlers:
    """Handlers for specific use case queries"""
    
    def __init__(self, db_client, openai_client: OpenAIClient):
        """Initialize query handlers
        
        Args:
            db_client: MongoDB database client
            openai_client: OpenAI client instance
        """
        self.db = db_client
        self.openai_client = openai_client
        self.query_parser = QueryParser()
        self.query_generator = QueryGenerator()
        self.correlator = DataCorrelator(db_client)
        self.optimizer = QueryOptimizer(db_client)
        
        logger.info("QueryHandlers initialized")
    
    def handle_city_delays(self, city: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Handle: "Why were deliveries delayed in city X yesterday?"
        
        Args:
            city: City name to analyze
            date: Specific date (defaults to yesterday)
            
        Returns:
            Analysis results with delay reasons and correlations
        """
        logger.info(f"Analyzing city delays for {city} on {date or 'yesterday'}")
        
        # Set date to yesterday if not provided
        if not date:
            target_date = (datetime.now() - timedelta(days=1)).date().isoformat()
        else:
            target_date = date
        
        # Build aggregation pipeline for city delays
        pipeline = [
            {
                '$match': {
                    'status': 'delayed',
                    'timestamp': {
                        '$gte': target_date,
                        '$lt': (datetime.fromisoformat(target_date) + timedelta(days=1)).isoformat()
                    }
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
                '$lookup': {
                    'from': 'warehouses',
                    'localField': 'order_info.warehouse_id',
                    'foreignField': 'warehouse_id',
                    'as': 'warehouse_info'
                }
            },
            {
                '$unwind': '$warehouse_info'
            },
            {
                '$match': {
                    'warehouse_info.location': {'$regex': city, '$options': 'i'}
                }
            },
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
                                        {'$lte': ['$$order_date', {'$add': ['$date', 86400000]}]},
                                        {'$regex': ['$location', city, 'i']}
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
                        'delay_reason': '$notes'
                    },
                    'delay_count': {'$sum': 1},
                    'avg_delay_minutes': {'$avg': '$delay_minutes'},
                    'total_delay_minutes': {'$sum': '$delay_minutes'},
                    'external_factors': {'$push': '$external_factors'},
                    'affected_orders': {'$push': '$order_id'}
                }
            },
            {
                '$sort': {'delay_count': -1}
            },
            {
                '$limit': 10
            }
        ]
        
        # Execute optimized query
        results, metadata = self.optimizer.execute_optimized_query('fleet_logs', pipeline)
        
        # Analyze external factor correlations
        external_correlations = self._analyze_external_factor_impact(results, target_date, city)
        
        # Generate insights
        insights = self._generate_city_delay_insights(results, external_correlations, city, target_date)
        
        return {
            'query_type': 'city_delays',
            'city': city,
            'date': target_date,
            'delay_breakdown': results,
            'external_correlations': external_correlations,
            'insights': insights,
            'metadata': metadata
        }
    
    def handle_client_failures(self, client_id: str, days: int = 7) -> Dict[str, Any]:
        """Handle: "Why did Client X's orders fail in the past week?"
        
        Args:
            client_id: Client ID to analyze
            days: Number of days to look back
            
        Returns:
            Analysis results with failure reasons and patterns
        """
        logger.info(f"Analyzing client failures for {client_id} over {days} days")
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Build aggregation pipeline for client failures
        pipeline = [
            {
                '$match': {
                    'client_id': client_id,
                    'status': {'$in': ['failed', 'cancelled']},
                    'order_date': {
                        '$gte': start_date.isoformat(),
                        '$lte': end_date.isoformat()
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'warehouse_logs',
                    'localField': 'order_id',
                    'foreignField': 'order_id',
                    'as': 'warehouse_logs'
                }
            },
            {
                '$lookup': {
                    'from': 'fleet_logs',
                    'localField': 'order_id',
                    'foreignField': 'order_id',
                    'as': 'fleet_logs'
                }
            },
            {
                '$addFields': {
                    'failure_stage': {
                        '$cond': [
                            {'$gt': [{'$size': '$fleet_logs'}, 0]}, 'delivery',
                            {'$cond': [
                                {'$gt': [{'$size': '$warehouse_logs'}, 0]}, 'warehouse',
                                'order_processing'
                            ]}
                        ]
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'status': '$status',
                        'failure_stage': '$failure_stage',
                        'priority': '$priority'
                    },
                    'failure_count': {'$sum': 1},
                    'total_amount_lost': {'$sum': '$total_amount'},
                    'failed_orders': {'$push': '$order_id'},
                    'warehouse_issues': {'$push': '$warehouse_logs.status'},
                    'delivery_issues': {'$push': '$fleet_logs.event_type'}
                }
            },
            {
                '$sort': {'failure_count': -1}
            }
        ]
        
        # Execute optimized query
        results, metadata = self.optimizer.execute_optimized_query('orders', pipeline)
        
        # Analyze failure patterns
        failure_patterns = self._analyze_failure_patterns(results, client_id)
        
        # Get client-specific recommendations
        recommendations = self._generate_client_recommendations(results, failure_patterns, client_id)
        
        return {
            'query_type': 'client_failures',
            'client_id': client_id,
            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'failure_breakdown': results,
            'failure_patterns': failure_patterns,
            'recommendations': recommendations,
            'metadata': metadata
        }
    
    def handle_warehouse_efficiency(self, warehouse_id: str, time_period: str = 'week') -> Dict[str, Any]:
        """Handle: "How efficient is warehouse X compared to others?"
        
        Args:
            warehouse_id: Warehouse ID to analyze
            time_period: Time period for analysis (week, month)
            
        Returns:
            Efficiency analysis and comparison
        """
        logger.info(f"Analyzing warehouse efficiency for {warehouse_id} over {time_period}")
        
        # Calculate date range
        if time_period == 'week':
            days_back = 7
        elif time_period == 'month':
            days_back = 30
        else:
            days_back = 7
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Pipeline for specific warehouse
        warehouse_pipeline = [
            {
                '$match': {
                    'warehouse_id': warehouse_id,
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': '$warehouse_id',
                    'total_operations': {'$sum': 1},
                    'avg_processing_time': {'$avg': '$processing_time_minutes'},
                    'success_rate': {
                        '$avg': {'$cond': [{'$eq': ['$status', 'success']}, 1, 0]}
                    },
                    'operations_by_type': {
                        '$push': {
                            'type': '$operation_type',
                            'time': '$processing_time_minutes',
                            'status': '$status'
                        }
                    }
                }
            }
        ]
        
        # Pipeline for all warehouses comparison
        comparison_pipeline = [
            {
                '$match': {
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': '$warehouse_id',
                    'total_operations': {'$sum': 1},
                    'avg_processing_time': {'$avg': '$processing_time_minutes'},
                    'success_rate': {
                        '$avg': {'$cond': [{'$eq': ['$status', 'success']}, 1, 0]}
                    }
                }
            },
            {
                '$sort': {'avg_processing_time': 1}
            }
        ]
        
        # Execute both queries
        warehouse_results, warehouse_metadata = self.optimizer.execute_optimized_query(
            'warehouse_logs', warehouse_pipeline
        )
        comparison_results, comparison_metadata = self.optimizer.execute_optimized_query(
            'warehouse_logs', comparison_pipeline
        )
        
        # Calculate efficiency metrics
        efficiency_analysis = self._calculate_warehouse_efficiency(
            warehouse_results, comparison_results, warehouse_id
        )
        
        return {
            'query_type': 'warehouse_efficiency',
            'warehouse_id': warehouse_id,
            'time_period': time_period,
            'warehouse_metrics': warehouse_results[0] if warehouse_results else {},
            'comparison_data': comparison_results,
            'efficiency_analysis': efficiency_analysis,
            'metadata': {
                'warehouse_query': warehouse_metadata,
                'comparison_query': comparison_metadata
            }
        }
    
    def handle_delivery_performance_trends(self, time_period: str = 'month') -> Dict[str, Any]:
        """Handle: "What are the delivery performance trends?"
        
        Args:
            time_period: Time period for trend analysis
            
        Returns:
            Trend analysis results
        """
        logger.info(f"Analyzing delivery performance trends over {time_period}")
        
        # Calculate date range
        if time_period == 'week':
            days_back = 7
            group_by = {'$dayOfWeek': '$timestamp'}
        elif time_period == 'month':
            days_back = 30
            group_by = {'$dayOfMonth': '$timestamp'}
        else:
            days_back = 30
            group_by = {'$dayOfMonth': '$timestamp'}
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Pipeline for delivery trends
        pipeline = [
            {
                '$match': {
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$addFields': {
                    'date_group': group_by
                }
            },
            {
                '$group': {
                    '_id': '$date_group',
                    'total_deliveries': {'$sum': 1},
                    'on_time_deliveries': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'on_time']}, 1, 0]}
                    },
                    'delayed_deliveries': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'delayed']}, 1, 0]}
                    },
                    'failed_deliveries': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'failed']}, 1, 0]}
                    },
                    'avg_delay_minutes': {
                        '$avg': {'$cond': [{'$gt': ['$delay_minutes', 0]}, '$delay_minutes', null]}
                    }
                }
            },
            {
                '$addFields': {
                    'on_time_rate': {
                        '$divide': ['$on_time_deliveries', '$total_deliveries']
                    },
                    'delay_rate': {
                        '$divide': ['$delayed_deliveries', '$total_deliveries']
                    }
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]
        
        # Execute query
        results, metadata = self.optimizer.execute_optimized_query('fleet_logs', pipeline)
        
        # Calculate trend analysis
        trend_analysis = self._calculate_performance_trends(results, time_period)
        
        return {
            'query_type': 'delivery_performance_trends',
            'time_period': time_period,
            'trend_data': results,
            'trend_analysis': trend_analysis,
            'metadata': metadata
        }
    
    def handle_customer_satisfaction_correlation(self, rating_threshold: int = 3) -> Dict[str, Any]:
        """Handle: "How does delivery performance correlate with customer satisfaction?"
        
        Args:
            rating_threshold: Minimum rating to consider as satisfied
            
        Returns:
            Correlation analysis results
        """
        logger.info(f"Analyzing customer satisfaction correlation with rating threshold {rating_threshold}")
        
        # Pipeline to correlate delivery performance with feedback
        pipeline = [
            {
                '$lookup': {
                    'from': 'fleet_logs',
                    'localField': 'order_id',
                    'foreignField': 'order_id',
                    'as': 'delivery_info'
                }
            },
            {
                '$unwind': '$delivery_info'
            },
            {
                '$addFields': {
                    'is_satisfied': {'$gte': ['$rating', rating_threshold]},
                    'was_delayed': {'$eq': ['$delivery_info.status', 'delayed']},
                    'was_on_time': {'$eq': ['$delivery_info.status', 'on_time']}
                }
            },
            {
                '$group': {
                    '_id': {
                        'delivery_status': '$delivery_info.status',
                        'is_satisfied': '$is_satisfied'
                    },
                    'count': {'$sum': 1},
                    'avg_rating': {'$avg': '$rating'},
                    'avg_delay_minutes': {'$avg': '$delivery_info.delay_minutes'}
                }
            },
            {
                '$sort': {'_id.delivery_status': 1, '_id.is_satisfied': -1}
            }
        ]
        
        # Execute query
        results, metadata = self.optimizer.execute_optimized_query('feedback', pipeline)
        
        # Calculate correlation metrics
        correlation_analysis = self._calculate_satisfaction_correlation(results, rating_threshold)
        
        return {
            'query_type': 'customer_satisfaction_correlation',
            'rating_threshold': rating_threshold,
            'correlation_data': results,
            'correlation_analysis': correlation_analysis,
            'metadata': metadata
        }
    
    def handle_peak_failure_analysis(self, failure_type: str = 'all') -> Dict[str, Any]:
        """Handle: "When do most failures occur and why?"
        
        Args:
            failure_type: Type of failure to analyze (all, delays, cancellations)
            
        Returns:
            Peak failure analysis results
        """
        logger.info(f"Analyzing peak failure patterns for {failure_type}")
        
        # Build match conditions based on failure type
        if failure_type == 'delays':
            match_condition = {'status': 'delayed'}
            collection = 'fleet_logs'
            time_field = 'timestamp'
        elif failure_type == 'cancellations':
            match_condition = {'status': 'cancelled'}
            collection = 'orders'
            time_field = 'order_date'
        else:
            match_condition = {'status': {'$in': ['failed', 'delayed', 'cancelled']}}
            collection = 'orders'
            time_field = 'order_date'
        
        # Pipeline for temporal analysis
        pipeline = [
            {'$match': match_condition},
            {
                '$addFields': {
                    'hour_of_day': {'$hour': f'${time_field}'},
                    'day_of_week': {'$dayOfWeek': f'${time_field}'},
                    'day_of_month': {'$dayOfMonth': f'${time_field}'}
                }
            },
            {
                '$group': {
                    '_id': {
                        'hour': '$hour_of_day',
                        'day_of_week': '$day_of_week'
                    },
                    'failure_count': {'$sum': 1},
                    'failure_types': {'$push': '$status'}
                }
            },
            {
                '$sort': {'failure_count': -1}
            },
            {
                '$limit': 20
            }
        ]
        
        # Execute query
        results, metadata = self.optimizer.execute_optimized_query(collection, pipeline)
        
        # Analyze peak patterns
        peak_analysis = self._analyze_peak_failure_patterns(results, failure_type)
        
        return {
            'query_type': 'peak_failure_analysis',
            'failure_type': failure_type,
            'peak_patterns': results,
            'peak_analysis': peak_analysis,
            'metadata': metadata
        }
    
    # Helper methods for analysis
    
    def _analyze_external_factor_impact(self, results: List[Dict], date: str, city: str) -> Dict[str, Any]:
        """Analyze impact of external factors on delays"""
        external_factors = []
        for result in results:
            factors = result.get('external_factors', [])
            for factor_list in factors:
                external_factors.extend(factor_list)
        
        if not external_factors:
            return {'impact': 'none', 'factors': []}
        
        factor_types = {}
        for factor in external_factors:
            factor_type = factor.get('factor_type', 'unknown')
            if factor_type not in factor_types:
                factor_types[factor_type] = {'count': 0, 'severity': []}
            factor_types[factor_type]['count'] += 1
            factor_types[factor_type]['severity'].append(factor.get('severity', 'low'))
        
        return {
            'impact': 'high' if len(external_factors) > 5 else 'moderate' if len(external_factors) > 2 else 'low',
            'factors': factor_types
        }
    
    def _generate_city_delay_insights(self, results: List[Dict], correlations: Dict, city: str, date: str) -> List[str]:
        """Generate insights for city delay analysis"""
        insights = []
        
        if not results:
            insights.append(f"No significant delays found in {city} on {date}")
            return insights
        
        top_cause = results[0]
        insights.append(f"Primary delay cause: {top_cause['_id']['event_type']} "
                       f"({top_cause['delay_count']} incidents, "
                       f"{top_cause['avg_delay_minutes']:.1f} min average)")
        
        if correlations['impact'] != 'none':
            insights.append(f"External factors had {correlations['impact']} impact on delays")
        
        total_delays = sum(r['delay_count'] for r in results)
        total_delay_time = sum(r['total_delay_minutes'] for r in results)
        insights.append(f"Total: {total_delays} delayed deliveries, "
                       f"{total_delay_time:.0f} minutes lost")
        
        return insights
    
    def _analyze_failure_patterns(self, results: List[Dict], client_id: str) -> Dict[str, Any]:
        """Analyze failure patterns for a client"""
        if not results:
            return {'primary_stage': 'none', 'risk_factors': []}
        
        stage_counts = {}
        for result in results:
            stage = result['_id']['failure_stage']
            stage_counts[stage] = stage_counts.get(stage, 0) + result['failure_count']
        
        primary_stage = max(stage_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'primary_stage': primary_stage,
            'stage_breakdown': stage_counts,
            'risk_factors': self._identify_risk_factors(results)
        }
    
    def _identify_risk_factors(self, results: List[Dict]) -> List[str]:
        """Identify risk factors from failure analysis"""
        risk_factors = []
        
        for result in results:
            if result['_id']['priority'] in ['high', 'urgent']:
                risk_factors.append('High priority orders failing frequently')
            
            if result['_id']['status'] == 'cancelled':
                risk_factors.append('High cancellation rate')
        
        return risk_factors
    
    def _generate_client_recommendations(self, results: List[Dict], patterns: Dict, client_id: str) -> List[str]:
        """Generate recommendations for client failure issues"""
        recommendations = []
        
        if patterns['primary_stage'] == 'warehouse':
            recommendations.append("Focus on warehouse operations optimization")
        elif patterns['primary_stage'] == 'delivery':
            recommendations.append("Improve delivery route planning and driver allocation")
        
        if 'High priority orders failing frequently' in patterns['risk_factors']:
            recommendations.append("Implement special handling for high-priority orders")
        
        return recommendations
    
    def _calculate_warehouse_efficiency(self, warehouse_data: List[Dict], 
                                      comparison_data: List[Dict], warehouse_id: str) -> Dict[str, Any]:
        """Calculate warehouse efficiency metrics"""
        if not warehouse_data:
            return {'efficiency_score': 0, 'ranking': 'unknown'}
        
        warehouse_metrics = warehouse_data[0]
        
        # Calculate ranking
        ranking = 1
        for comp in comparison_data:
            if comp['_id'] != warehouse_id and comp['avg_processing_time'] < warehouse_metrics['avg_processing_time']:
                ranking += 1
        
        # Calculate efficiency score (0-100)
        if comparison_data:
            best_time = min(comp['avg_processing_time'] for comp in comparison_data)
            worst_time = max(comp['avg_processing_time'] for comp in comparison_data)
            
            if worst_time > best_time:
                efficiency_score = 100 * (1 - (warehouse_metrics['avg_processing_time'] - best_time) / (worst_time - best_time))
            else:
                efficiency_score = 100
        else:
            efficiency_score = warehouse_metrics['success_rate'] * 100
        
        return {
            'efficiency_score': max(0, min(100, efficiency_score)),
            'ranking': f"{ranking} out of {len(comparison_data)}",
            'performance_category': 'excellent' if efficiency_score > 80 else 'good' if efficiency_score > 60 else 'needs_improvement'
        }
    
    def _calculate_performance_trends(self, results: List[Dict], time_period: str) -> Dict[str, Any]:
        """Calculate performance trend analysis"""
        if len(results) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend direction
        on_time_rates = [r['on_time_rate'] for r in results]
        
        if len(on_time_rates) >= 2:
            trend_direction = 'improving' if on_time_rates[-1] > on_time_rates[0] else 'declining'
            trend_magnitude = abs(on_time_rates[-1] - on_time_rates[0])
        else:
            trend_direction = 'stable'
            trend_magnitude = 0
        
        return {
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'current_on_time_rate': on_time_rates[-1] if on_time_rates else 0,
            'average_on_time_rate': sum(on_time_rates) / len(on_time_rates) if on_time_rates else 0
        }
    
    def _calculate_satisfaction_correlation(self, results: List[Dict], threshold: int) -> Dict[str, Any]:
        """Calculate satisfaction correlation metrics"""
        satisfied_on_time = 0
        satisfied_delayed = 0
        unsatisfied_on_time = 0
        unsatisfied_delayed = 0
        
        for result in results:
            delivery_status = result['_id']['delivery_status']
            is_satisfied = result['_id']['is_satisfied']
            count = result['count']
            
            if delivery_status == 'on_time':
                if is_satisfied:
                    satisfied_on_time += count
                else:
                    unsatisfied_on_time += count
            elif delivery_status == 'delayed':
                if is_satisfied:
                    satisfied_delayed += count
                else:
                    unsatisfied_delayed += count
        
        total = satisfied_on_time + satisfied_delayed + unsatisfied_on_time + unsatisfied_delayed
        
        if total == 0:
            return {'correlation_strength': 'no_data'}
        
        satisfaction_rate_on_time = satisfied_on_time / (satisfied_on_time + unsatisfied_on_time) if (satisfied_on_time + unsatisfied_on_time) > 0 else 0
        satisfaction_rate_delayed = satisfied_delayed / (satisfied_delayed + unsatisfied_delayed) if (satisfied_delayed + unsatisfied_delayed) > 0 else 0
        
        correlation_strength = abs(satisfaction_rate_on_time - satisfaction_rate_delayed)
        
        return {
            'correlation_strength': 'strong' if correlation_strength > 0.3 else 'moderate' if correlation_strength > 0.1 else 'weak',
            'satisfaction_rate_on_time': satisfaction_rate_on_time,
            'satisfaction_rate_delayed': satisfaction_rate_delayed,
            'impact_of_delays': correlation_strength
        }
    
    def _analyze_peak_failure_patterns(self, results: List[Dict], failure_type: str) -> Dict[str, Any]:
        """Analyze peak failure patterns"""
        if not results:
            return {'peak_times': [], 'patterns': []}
        
        # Find peak hours and days
        peak_times = results[:5]  # Top 5 peak times
        
        # Analyze patterns
        patterns = []
        hour_counts = {}
        day_counts = {}
        
        for result in results:
            hour = result['_id']['hour']
            day = result['_id']['day_of_week']
            
            hour_counts[hour] = hour_counts.get(hour, 0) + result['failure_count']
            day_counts[day] = day_counts.get(day, 0) + result['failure_count']
        
        # Identify patterns
        if max(hour_counts.values()) > sum(hour_counts.values()) * 0.3:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
            patterns.append(f"Peak failures occur around {peak_hour}:00")
        
        if max(day_counts.values()) > sum(day_counts.values()) * 0.25:
            peak_day = max(day_counts.items(), key=lambda x: x[1])[0]
            day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
            patterns.append(f"Peak failures occur on {day_names.get(peak_day, 'Unknown')}s")
        
        return {
            'peak_times': peak_times,
            'patterns': patterns,
            'hourly_distribution': hour_counts,
            'daily_distribution': day_counts
        }
