"""
Actionable recommendation engine for generating business recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
# Import will be handled by the calling code
# from .templates import Recommendation

logger = logging.getLogger(__name__)


@dataclass
class RecommendationRule:
    """Rule for generating recommendations"""
    condition: str
    recommendation_template: Recommendation
    priority_boost: float = 0.0


class RecommendationEngine:
    """Generate actionable recommendations based on analysis results"""
    
    def __init__(self):
        """Initialize recommendation engine with predefined rules"""
        self.logger = logging.getLogger(__name__)
        self.rules = self._initialize_recommendation_rules()
    
    def generate_operational_recommendations(self, 
                                           query_results: List[Dict[str, Any]],
                                           query_context: Dict[str, Any],
                                           analysis_type: str) -> List[Recommendation]:
        """Generate operational recommendations based on analysis results
        
        Args:
            query_results: Raw query results from MongoDB
            query_context: Context about the query and analysis
            analysis_type: Type of analysis performed
            
        Returns:
            List of prioritized recommendations
        """
        try:
            recommendations = []
            
            # Analyze results to extract key metrics
            metrics = self._extract_key_metrics(query_results, query_context)
            
            # Apply analysis-specific recommendation logic
            if analysis_type == "delay_analysis":
                recommendations.extend(self._generate_delay_recommendations(metrics, query_results))
            elif analysis_type == "client_analysis":
                recommendations.extend(self._generate_client_recommendations(metrics, query_results))
            elif analysis_type == "operational_efficiency":
                recommendations.extend(self._generate_efficiency_recommendations(metrics, query_results))
            elif analysis_type == "failure_analysis":
                recommendations.extend(self._generate_failure_recommendations(metrics, query_results))
            else:
                # Generic recommendations
                recommendations.extend(self._generate_generic_recommendations(metrics, query_results))
            
            # Apply rule-based recommendations
            rule_recommendations = self._apply_recommendation_rules(metrics, query_context)
            recommendations.extend(rule_recommendations)
            
            # Prioritize and deduplicate
            prioritized_recommendations = self._prioritize_recommendations(recommendations)
            
            self.logger.info(f"Generated {len(prioritized_recommendations)} recommendations for {analysis_type}")
            return prioritized_recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating operational recommendations: {e}")
            return [self._create_fallback_recommendation()]
    
    def generate_executive_recommendations(self, 
                                         query_results: List[Dict[str, Any]],
                                         query_context: Dict[str, Any]) -> List[Recommendation]:
        """Generate high-level strategic recommendations for executives
        
        Args:
            query_results: Raw query results from MongoDB
            query_context: Context about the query and analysis
            
        Returns:
            List of strategic recommendations
        """
        try:
            recommendations = []
            metrics = self._extract_key_metrics(query_results, query_context)
            
            # Strategic recommendations based on overall performance
            if metrics.get('success_rate', 100) < 85:
                recommendations.append(Recommendation(
                    category="strategic",
                    action="Implement comprehensive quality improvement program",
                    expected_impact="Increase success rate by 10-15%",
                    implementation_effort="high",
                    timeline="3-6 months",
                    priority="urgent"
                ))
            
            if metrics.get('failure_rate', 0) > 15:
                recommendations.append(Recommendation(
                    category="strategic",
                    action="Establish dedicated failure analysis and prevention team",
                    expected_impact="Reduce failure rate by 20-30%",
                    implementation_effort="medium",
                    timeline="1-2 months",
                    priority="high"
                ))
            
            # Financial impact recommendations
            if metrics.get('total_value', 0) > 0:
                cost_per_failure = metrics.get('total_value', 0) * 0.05  # Assume 5% cost impact
                if cost_per_failure > 10000:  # Significant financial impact
                    recommendations.append(Recommendation(
                        category="strategic",
                        action="Invest in predictive analytics and early warning systems",
                        expected_impact=f"Prevent ₹{cost_per_failure:,.0f} in potential losses",
                        implementation_effort="high",
                        timeline="6-12 months",
                        priority="high"
                    ))
            
            # Technology and automation recommendations
            if len(query_results) > 1000:  # High volume operations
                recommendations.append(Recommendation(
                    category="strategic",
                    action="Implement automated monitoring and alerting systems",
                    expected_impact="Reduce response time by 50% and prevent 30% of issues",
                    implementation_effort="medium",
                    timeline="2-4 months",
                    priority="medium"
                ))
            
            return self._prioritize_recommendations(recommendations)
            
        except Exception as e:
            self.logger.error(f"Error generating executive recommendations: {e}")
            return [self._create_strategic_fallback_recommendation()]
    
    def generate_comparative_recommendations(self, 
                                           comparison_analysis: Dict[str, Any],
                                           comparison_context: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations based on comparative analysis
        
        Args:
            comparison_analysis: Results of comparative analysis
            comparison_context: Context about the comparison
            
        Returns:
            List of improvement recommendations
        """
        try:
            recommendations = []
            
            # Analyze performance gaps
            performance_changes = comparison_analysis.get('performance_changes', {})
            
            for metric, change_data in performance_changes.items():
                change_percentage = change_data.get('change_percentage', 0)
                
                if change_percentage < -10:  # Significant decline
                    recommendations.append(Recommendation(
                        category="operational",
                        action=f"Investigate and address decline in {metric.replace('_', ' ')}",
                        expected_impact=f"Restore {metric} to previous levels",
                        implementation_effort="medium",
                        timeline="2-4 weeks",
                        priority="high"
                    ))
                elif change_percentage > 20:  # Significant improvement
                    recommendations.append(Recommendation(
                        category="process",
                        action=f"Document and replicate successful practices that improved {metric.replace('_', ' ')}",
                        expected_impact="Maintain and scale improvements",
                        implementation_effort="low",
                        timeline="1-2 weeks",
                        priority="medium"
                    ))
            
            # Best practice recommendations
            better_areas = comparison_analysis.get('better_areas', [])
            worse_areas = comparison_analysis.get('worse_areas', [])
            
            if better_areas and worse_areas:
                recommendations.append(Recommendation(
                    category="process",
                    action="Transfer best practices from high-performing areas to underperforming ones",
                    expected_impact="Standardize performance across all areas",
                    implementation_effort="medium",
                    timeline="1-3 months",
                    priority="medium"
                ))
            
            return self._prioritize_recommendations(recommendations)
            
        except Exception as e:
            self.logger.error(f"Error generating comparative recommendations: {e}")
            return [self._create_fallback_recommendation()]
    
    def generate_predictive_recommendations(self, 
                                          predictions: Dict[str, Any],
                                          risk_factors: List[Dict[str, Any]],
                                          prediction_context: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations based on predictive analysis
        
        Args:
            predictions: Prediction results
            risk_factors: Identified risk factors
            prediction_context: Context about the predictions
            
        Returns:
            List of proactive recommendations
        """
        try:
            recommendations = []
            
            # Risk mitigation recommendations
            for risk in risk_factors:
                risk_level = risk.get('severity', 'medium')
                risk_description = risk.get('description', 'Unknown risk')
                
                if risk_level in ['high', 'critical']:
                    recommendations.append(Recommendation(
                        category="risk_mitigation",
                        action=f"Implement preventive measures for {risk_description}",
                        expected_impact="Reduce risk probability by 40-60%",
                        implementation_effort="medium",
                        timeline="2-6 weeks",
                        priority="high" if risk_level == 'critical' else "medium"
                    ))
            
            # Capacity planning recommendations
            demand_forecast = predictions.get('demand_forecast', {})
            if demand_forecast:
                predicted_increase = demand_forecast.get('growth_percentage', 0)
                if predicted_increase > 20:
                    recommendations.append(Recommendation(
                        category="resource",
                        action="Scale up capacity to meet predicted demand increase",
                        expected_impact=f"Handle {predicted_increase}% increase in demand",
                        implementation_effort="high",
                        timeline="1-3 months",
                        priority="high"
                    ))
            
            # Early warning system recommendations
            if risk_factors:
                recommendations.append(Recommendation(
                    category="operational",
                    action="Implement early warning indicators for identified risk factors",
                    expected_impact="Detect issues 2-3 days earlier",
                    implementation_effort="medium",
                    timeline="3-4 weeks",
                    priority="medium"
                ))
            
            return self._prioritize_recommendations(recommendations)
            
        except Exception as e:
            self.logger.error(f"Error generating predictive recommendations: {e}")
            return [self._create_fallback_recommendation()]
    
    def _generate_delay_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[Recommendation]:
        """Generate recommendations specific to delay analysis"""
        recommendations = []
        
        avg_delay = metrics.get('average_delay_minutes', 0)
        delay_rate = metrics.get('delay_rate', 0)
        
        if avg_delay > 60:  # More than 1 hour average delay
            recommendations.append(Recommendation(
                category="operational",
                action="Implement dynamic routing to avoid traffic congestion",
                expected_impact="Reduce average delay by 30-40%",
                implementation_effort="medium",
                timeline="2-3 weeks",
                priority="high"
            ))
        
        if delay_rate > 25:  # More than 25% of deliveries delayed
            recommendations.append(Recommendation(
                category="process",
                action="Review and optimize delivery scheduling processes",
                expected_impact="Reduce delay rate by 15-20%",
                implementation_effort="low",
                timeline="1-2 weeks",
                priority="medium"
            ))
        
        # Analyze delay patterns for specific recommendations
        delay_patterns = self._analyze_delay_patterns(results)
        
        if delay_patterns.get('peak_hour_delays', 0) > 50:
            recommendations.append(Recommendation(
                category="operational",
                action="Reschedule deliveries to avoid peak traffic hours",
                expected_impact="Reduce peak hour delays by 40-50%",
                implementation_effort="low",
                timeline="1 week",
                priority="medium"
            ))
        
        return recommendations
    
    def _generate_client_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[Recommendation]:
        """Generate recommendations specific to client analysis"""
        recommendations = []
        
        success_rate = metrics.get('success_rate', 100)
        complaint_rate = metrics.get('complaint_rate', 0)
        
        if success_rate < 90:
            recommendations.append(Recommendation(
                category="process",
                action="Implement client-specific quality assurance protocols",
                expected_impact="Increase success rate to 95%+",
                implementation_effort="medium",
                timeline="3-4 weeks",
                priority="high"
            ))
        
        if complaint_rate > 5:
            recommendations.append(Recommendation(
                category="process",
                action="Establish proactive client communication and issue resolution process",
                expected_impact="Reduce complaint rate by 60-70%",
                implementation_effort="low",
                timeline="1-2 weeks",
                priority="medium"
            ))
        
        # Analyze failure patterns for client-specific recommendations
        failure_patterns = self._analyze_failure_patterns(results)
        
        if failure_patterns.get('address_issues', 0) > 20:
            recommendations.append(Recommendation(
                category="process",
                action="Implement address verification system before dispatch",
                expected_impact="Reduce address-related failures by 80%",
                implementation_effort="medium",
                timeline="2-3 weeks",
                priority="high"
            ))
        
        return recommendations
    
    def _generate_efficiency_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[Recommendation]:
        """Generate recommendations specific to operational efficiency"""
        recommendations = []
        
        efficiency_score = metrics.get('efficiency_score', 100)
        resource_utilization = metrics.get('resource_utilization', 100)
        
        if efficiency_score < 75:
            recommendations.append(Recommendation(
                category="operational",
                action="Conduct comprehensive process optimization review",
                expected_impact="Increase efficiency by 20-25%",
                implementation_effort="high",
                timeline="6-8 weeks",
                priority="high"
            ))
        
        if resource_utilization < 60:
            recommendations.append(Recommendation(
                category="resource",
                action="Optimize resource allocation and scheduling",
                expected_impact="Increase utilization to 80%+",
                implementation_effort="medium",
                timeline="3-4 weeks",
                priority="medium"
            ))
        
        # Bottleneck analysis
        bottlenecks = self._identify_bottlenecks(results)
        
        for bottleneck in bottlenecks[:2]:  # Top 2 bottlenecks
            recommendations.append(Recommendation(
                category="operational",
                action=f"Address bottleneck in {bottleneck['process']}",
                expected_impact=f"Improve throughput by {bottleneck.get('improvement_potential', 15)}%",
                implementation_effort="medium",
                timeline="2-4 weeks",
                priority="high" if bottleneck.get('impact_score', 0) > 80 else "medium"
            ))
        
        return recommendations
    
    def _generate_failure_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[Recommendation]:
        """Generate recommendations specific to failure analysis"""
        recommendations = []
        
        failure_rate = metrics.get('failure_rate', 0)
        
        if failure_rate > 10:
            recommendations.append(Recommendation(
                category="process",
                action="Implement root cause analysis for all failures",
                expected_impact="Reduce failure rate by 30-40%",
                implementation_effort="medium",
                timeline="2-3 weeks",
                priority="high"
            ))
        
        # Analyze failure patterns
        failure_patterns = self._analyze_failure_patterns(results)
        
        top_failure_reason = max(failure_patterns.items(), key=lambda x: x[1]) if failure_patterns else None
        
        if top_failure_reason and top_failure_reason[1] > 30:  # More than 30% of failures
            reason, percentage = top_failure_reason
            recommendations.append(Recommendation(
                category="process",
                action=f"Implement specific controls to prevent {reason.replace('_', ' ')}",
                expected_impact=f"Reduce {reason} failures by 70-80%",
                implementation_effort="medium",
                timeline="2-4 weeks",
                priority="high"
            ))
        
        return recommendations
    
    def _generate_generic_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[Recommendation]:
        """Generate generic recommendations for unknown analysis types"""
        recommendations = []
        
        # Data quality recommendation
        if len(results) < 100:
            recommendations.append(Recommendation(
                category="process",
                action="Improve data collection and monitoring systems",
                expected_impact="Better insights and decision making",
                implementation_effort="medium",
                timeline="3-4 weeks",
                priority="medium"
            ))
        
        # Performance monitoring recommendation
        recommendations.append(Recommendation(
            category="operational",
            action="Implement regular performance monitoring and reporting",
            expected_impact="Proactive issue identification and resolution",
            implementation_effort="low",
            timeline="1-2 weeks",
            priority="medium"
        ))
        
        return recommendations
    
    def _extract_key_metrics(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from query results"""
        metrics = {
            'total_records': len(results)
        }
        
        if not results:
            return metrics
        
        try:
            # Success/failure rates
            success_statuses = ['completed', 'delivered', 'success']
            failure_statuses = ['failed', 'cancelled', 'error']
            
            success_count = sum(1 for r in results if r.get('status') in success_statuses)
            failure_count = sum(1 for r in results if r.get('status') in failure_statuses)
            
            metrics['success_rate'] = (success_count / len(results)) * 100
            metrics['failure_rate'] = (failure_count / len(results)) * 100
            
            # Delay metrics
            delays = [r.get('delay_minutes', 0) for r in results if 'delay_minutes' in r]
            if delays:
                metrics['average_delay_minutes'] = sum(delays) / len(delays)
                metrics['delay_rate'] = (len([d for d in delays if d > 0]) / len(results)) * 100
            
            # Financial metrics
            amounts = [r.get('amount', r.get('value', 0)) for r in results]
            amounts = [a for a in amounts if isinstance(a, (int, float))]
            if amounts:
                metrics['total_value'] = sum(amounts)
                metrics['average_value'] = sum(amounts) / len(amounts)
            
            # Efficiency metrics (if available)
            if any('efficiency' in r for r in results):
                efficiency_scores = [r.get('efficiency', 0) for r in results if 'efficiency' in r]
                metrics['efficiency_score'] = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0
            
            # Resource utilization (if available)
            if any('utilization' in r for r in results):
                utilization_scores = [r.get('utilization', 0) for r in results if 'utilization' in r]
                metrics['resource_utilization'] = sum(utilization_scores) / len(utilization_scores) if utilization_scores else 0
        
        except Exception as e:
            self.logger.error(f"Error extracting key metrics: {e}")
        
        return metrics
    
    def _analyze_delay_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze delay patterns in the data"""
        patterns = {}
        
        try:
            delayed_results = [r for r in results if r.get('delay_minutes', 0) > 0]
            
            if delayed_results:
                # Peak hour analysis (simplified)
                peak_hour_delays = sum(1 for r in delayed_results if r.get('hour', 12) in [8, 9, 17, 18, 19])
                patterns['peak_hour_delays'] = (peak_hour_delays / len(delayed_results)) * 100
                
                # Weather-related delays
                weather_delays = sum(1 for r in delayed_results if 'weather' in str(r.get('delay_reason', '')).lower())
                patterns['weather_delays'] = (weather_delays / len(delayed_results)) * 100
                
                # Traffic-related delays
                traffic_delays = sum(1 for r in delayed_results if 'traffic' in str(r.get('delay_reason', '')).lower())
                patterns['traffic_delays'] = (traffic_delays / len(delayed_results)) * 100
        
        except Exception as e:
            self.logger.error(f"Error analyzing delay patterns: {e}")
        
        return patterns
    
    def _analyze_failure_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze failure patterns in the data"""
        patterns = {}
        
        try:
            failed_results = [r for r in results if r.get('status') in ['failed', 'cancelled', 'error']]
            
            if failed_results:
                total_failures = len(failed_results)
                
                # Address issues
                address_failures = sum(1 for r in failed_results if 'address' in str(r.get('failure_reason', '')).lower())
                patterns['address_issues'] = (address_failures / total_failures) * 100
                
                # Stock issues
                stock_failures = sum(1 for r in failed_results if 'stock' in str(r.get('failure_reason', '')).lower())
                patterns['stock_issues'] = (stock_failures / total_failures) * 100
                
                # Communication issues
                comm_failures = sum(1 for r in failed_results if 'communication' in str(r.get('failure_reason', '')).lower())
                patterns['communication_issues'] = (comm_failures / total_failures) * 100
        
        except Exception as e:
            self.logger.error(f"Error analyzing failure patterns: {e}")
        
        return patterns
    
    def _identify_bottlenecks(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify operational bottlenecks"""
        bottlenecks = []
        
        try:
            # Processing time analysis
            processing_times = {}
            for result in results:
                process = result.get('process_type', 'unknown')
                time = result.get('processing_time_minutes', 0)
                if process not in processing_times:
                    processing_times[process] = []
                processing_times[process].append(time)
            
            # Identify processes with high average processing times
            for process, times in processing_times.items():
                if times:
                    avg_time = sum(times) / len(times)
                    if avg_time > 30:  # More than 30 minutes average
                        bottlenecks.append({
                            'process': process,
                            'average_time': avg_time,
                            'impact_score': min(avg_time * 2, 100),  # Simple impact calculation
                            'improvement_potential': min(30, avg_time * 0.3)  # 30% improvement potential
                        })
            
            # Sort by impact score
            bottlenecks.sort(key=lambda x: x['impact_score'], reverse=True)
        
        except Exception as e:
            self.logger.error(f"Error identifying bottlenecks: {e}")
        
        return bottlenecks
    
    def _apply_recommendation_rules(self, metrics: Dict[str, Any], context: Dict[str, Any]) -> List[Recommendation]:
        """Apply predefined recommendation rules"""
        recommendations = []
        
        try:
            for rule in self.rules:
                if self._evaluate_rule_condition(rule.condition, metrics, context):
                    recommendation = rule.recommendation_template
                    # Apply priority boost if specified
                    if rule.priority_boost > 0:
                        # Boost priority logic would go here
                        pass
                    recommendations.append(recommendation)
        
        except Exception as e:
            self.logger.error(f"Error applying recommendation rules: {e}")
        
        return recommendations
    
    def _evaluate_rule_condition(self, condition: str, metrics: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a rule condition against metrics and context"""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            if "success_rate < 90" in condition:
                return metrics.get('success_rate', 100) < 90
            elif "failure_rate > 10" in condition:
                return metrics.get('failure_rate', 0) > 10
            elif "delay_rate > 20" in condition:
                return metrics.get('delay_rate', 0) > 20
            # Add more conditions as needed
            
            return False
        except Exception as e:
            self.logger.error(f"Error evaluating rule condition: {e}")
            return False
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioritize and deduplicate recommendations"""
        if not recommendations:
            return []
        
        try:
            # Remove duplicates based on action text
            seen_actions = set()
            unique_recommendations = []
            
            for rec in recommendations:
                action_key = rec.action.lower().strip()
                if action_key not in seen_actions:
                    seen_actions.add(action_key)
                    unique_recommendations.append(rec)
            
            # Sort by priority (urgent > high > medium > low)
            priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
            
            sorted_recommendations = sorted(
                unique_recommendations,
                key=lambda x: (
                    priority_order.get(x.priority, 0),
                    -len(x.expected_impact)  # Longer impact descriptions might be more important
                ),
                reverse=True
            )
            
            # Limit to top 10 recommendations
            return sorted_recommendations[:10]
        
        except Exception as e:
            self.logger.error(f"Error prioritizing recommendations: {e}")
            return recommendations[:5]  # Return first 5 as fallback
    
    def _initialize_recommendation_rules(self) -> List[RecommendationRule]:
        """Initialize predefined recommendation rules"""
        rules = []
        
        # High failure rate rule
        rules.append(RecommendationRule(
            condition="failure_rate > 10",
            recommendation_template=Recommendation(
                category="process",
                action="Implement comprehensive failure analysis and prevention program",
                expected_impact="Reduce failure rate by 40-50%",
                implementation_effort="medium",
                timeline="4-6 weeks",
                priority="high"
            )
        ))
        
        # Low success rate rule
        rules.append(RecommendationRule(
            condition="success_rate < 90",
            recommendation_template=Recommendation(
                category="operational",
                action="Review and improve quality control processes",
                expected_impact="Increase success rate to 95%+",
                implementation_effort="medium",
                timeline="3-4 weeks",
                priority="high"
            )
        ))
        
        # High delay rate rule
        rules.append(RecommendationRule(
            condition="delay_rate > 20",
            recommendation_template=Recommendation(
                category="operational",
                action="Optimize scheduling and routing algorithms",
                expected_impact="Reduce delays by 25-35%",
                implementation_effort="medium",
                timeline="2-3 weeks",
                priority="medium"
            )
        ))
        
        return rules
    
    def _create_fallback_recommendation(self) -> Recommendation:
        """Create a fallback recommendation when generation fails"""
        return Recommendation(
            category="operational",
            action="Review current processes and identify improvement opportunities",
            expected_impact="Improve overall operational efficiency",
            implementation_effort="medium",
            timeline="2-4 weeks",
            priority="medium"
        )
    
    def _create_strategic_fallback_recommendation(self) -> Recommendation:
        """Create a strategic fallback recommendation for executives"""
        return Recommendation(
            category="strategic",
            action="Conduct comprehensive operational review and develop improvement roadmap",
            expected_impact="Identify and prioritize key improvement opportunities",
            implementation_effort="high",
            timeline="6-8 weeks",
            priority="medium"
        )
