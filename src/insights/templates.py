"""
Structured insight templates for different analysis types
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class KeyFinding:
    """Individual key finding structure"""
    finding: str
    impact: str
    affected_items: int
    severity: str  # low, medium, high, critical
    confidence: float


@dataclass
class Recommendation:
    """Recommendation structure"""
    category: str  # operational, resource, process, strategic
    action: str
    expected_impact: str
    implementation_effort: str  # low, medium, high
    timeline: str
    priority: str  # low, medium, high, urgent


@dataclass
class FinancialImpact:
    """Financial impact structure"""
    total_impact: float
    currency: str
    breakdown: Dict[str, float]
    impact_type: str  # cost, revenue_loss, savings_opportunity


class InsightTemplates:
    """Structured templates for different analysis types"""
    
    def __init__(self):
        """Initialize insight templates"""
        pass
    
    def delay_analysis_template(self, 
                              analysis_results: Dict[str, Any],
                              recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Create delay analysis insight template
        
        Args:
            analysis_results: Processed analysis results
            recommendations: List of recommendations
            
        Returns:
            Structured delay analysis insight
        """
        template = {
            "analysis_type": "delay_analysis",
            "timestamp": datetime.now().isoformat(),
            "summary": self._generate_delay_summary(analysis_results),
            "key_findings": self._extract_delay_findings(analysis_results),
            "trends": self._extract_trend_info(analysis_results),
            "root_causes": self._identify_delay_root_causes(analysis_results),
            "affected_metrics": {
                "total_delayed_orders": analysis_results.get('total_delayed', 0),
                "average_delay_minutes": analysis_results.get('avg_delay', 0),
                "delay_percentage": analysis_results.get('delay_rate', 0),
                "worst_affected_routes": analysis_results.get('worst_routes', [])
            },
            "time_patterns": analysis_results.get('time_patterns', {}),
            "geographical_impact": analysis_results.get('geographical_data', {}),
            "recommendations": [asdict(rec) for rec in recommendations],
            "financial_impact": self._calculate_delay_financial_impact(analysis_results),
            "confidence_score": analysis_results.get('confidence', 0.8)
        }
        
        return template
    
    def client_analysis_template(self,
                               analysis_results: Dict[str, Any],
                               recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Create client analysis insight template
        
        Args:
            analysis_results: Processed analysis results
            recommendations: List of recommendations
            
        Returns:
            Structured client analysis insight
        """
        template = {
            "analysis_type": "client_analysis",
            "timestamp": datetime.now().isoformat(),
            "client_overview": self._generate_client_overview(analysis_results),
            "performance_metrics": {
                "success_rate": analysis_results.get('success_rate', 0),
                "average_rating": analysis_results.get('avg_rating', 0),
                "total_orders": analysis_results.get('total_orders', 0),
                "repeat_order_rate": analysis_results.get('repeat_rate', 0)
            },
            "failure_breakdown": self._create_failure_breakdown(analysis_results),
            "service_quality": {
                "on_time_delivery": analysis_results.get('on_time_rate', 0),
                "customer_satisfaction": analysis_results.get('satisfaction_score', 0),
                "complaint_rate": analysis_results.get('complaint_rate', 0)
            },
            "financial_impact": self._calculate_client_financial_impact(analysis_results),
            "trends": self._extract_client_trends(analysis_results),
            "risk_assessment": self._assess_client_risk(analysis_results),
            "action_items": [asdict(rec) for rec in recommendations],
            "comparative_analysis": analysis_results.get('peer_comparison', {}),
            "confidence_score": analysis_results.get('confidence', 0.8)
        }
        
        return template
    
    def operational_efficiency_template(self,
                                      analysis_results: Dict[str, Any],
                                      recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Create operational efficiency insight template
        
        Args:
            analysis_results: Processed analysis results
            recommendations: List of recommendations
            
        Returns:
            Structured operational efficiency insight
        """
        template = {
            "analysis_type": "operational_efficiency",
            "timestamp": datetime.now().isoformat(),
            "efficiency_overview": self._generate_efficiency_overview(analysis_results),
            "key_performance_indicators": {
                "overall_efficiency": analysis_results.get('efficiency_score', 0),
                "resource_utilization": analysis_results.get('resource_utilization', 0),
                "throughput": analysis_results.get('throughput', 0),
                "cost_per_operation": analysis_results.get('cost_per_op', 0)
            },
            "bottleneck_analysis": self._identify_bottlenecks(analysis_results),
            "capacity_analysis": {
                "current_capacity": analysis_results.get('current_capacity', 0),
                "peak_utilization": analysis_results.get('peak_utilization', 0),
                "capacity_constraints": analysis_results.get('constraints', [])
            },
            "performance_by_unit": analysis_results.get('unit_performance', {}),
            "optimization_opportunities": self._identify_optimization_opportunities(analysis_results),
            "cost_analysis": self._analyze_operational_costs(analysis_results),
            "recommendations": [asdict(rec) for rec in recommendations],
            "projected_improvements": self._calculate_projected_improvements(analysis_results, recommendations),
            "confidence_score": analysis_results.get('confidence', 0.8)
        }
        
        return template
    
    def predictive_analysis_template(self,
                                   analysis_results: Dict[str, Any],
                                   recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Create predictive analysis insight template
        
        Args:
            analysis_results: Processed analysis results
            recommendations: List of recommendations
            
        Returns:
            Structured predictive analysis insight
        """
        template = {
            "analysis_type": "predictive_analysis",
            "timestamp": datetime.now().isoformat(),
            "prediction_summary": self._generate_prediction_summary(analysis_results),
            "forecasts": {
                "demand_forecast": analysis_results.get('demand_forecast', {}),
                "capacity_forecast": analysis_results.get('capacity_forecast', {}),
                "risk_forecast": analysis_results.get('risk_forecast', {})
            },
            "trend_projections": analysis_results.get('trend_projections', {}),
            "scenario_analysis": {
                "best_case": analysis_results.get('best_case', {}),
                "worst_case": analysis_results.get('worst_case', {}),
                "most_likely": analysis_results.get('most_likely', {})
            },
            "risk_factors": self._identify_risk_factors(analysis_results),
            "early_warning_indicators": analysis_results.get('warning_indicators', []),
            "model_accuracy": {
                "confidence_interval": analysis_results.get('confidence_interval', {}),
                "historical_accuracy": analysis_results.get('historical_accuracy', 0),
                "model_type": analysis_results.get('model_type', 'statistical')
            },
            "actionable_insights": [asdict(rec) for rec in recommendations],
            "monitoring_recommendations": self._generate_monitoring_recommendations(analysis_results),
            "confidence_score": analysis_results.get('confidence', 0.7)
        }
        
        return template
    
    def comparative_analysis_template(self,
                                    analysis_results: Dict[str, Any],
                                    recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Create comparative analysis insight template
        
        Args:
            analysis_results: Processed analysis results
            recommendations: List of recommendations
            
        Returns:
            Structured comparative analysis insight
        """
        template = {
            "analysis_type": "comparative_analysis",
            "timestamp": datetime.now().isoformat(),
            "comparison_summary": self._generate_comparison_summary(analysis_results),
            "baseline_metrics": analysis_results.get('baseline', {}),
            "comparison_metrics": analysis_results.get('comparison', {}),
            "performance_gaps": self._identify_performance_gaps(analysis_results),
            "relative_performance": {
                "better_performing_areas": analysis_results.get('better_areas', []),
                "underperforming_areas": analysis_results.get('worse_areas', []),
                "performance_variance": analysis_results.get('variance', {})
            },
            "statistical_significance": analysis_results.get('statistical_tests', {}),
            "trend_comparison": analysis_results.get('trend_comparison', {}),
            "root_cause_differences": self._analyze_performance_differences(analysis_results),
            "improvement_opportunities": [asdict(rec) for rec in recommendations],
            "benchmarking_insights": analysis_results.get('benchmarking', {}),
            "confidence_score": analysis_results.get('confidence', 0.8)
        }
        
        return template
    
    def correlation_analysis_template(self,
                                    analysis_results: Dict[str, Any],
                                    recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Create correlation analysis insight template
        
        Args:
            analysis_results: Processed analysis results
            recommendations: List of recommendations
            
        Returns:
            Structured correlation analysis insight
        """
        template = {
            "analysis_type": "correlation_analysis",
            "timestamp": datetime.now().isoformat(),
            "correlation_summary": self._generate_correlation_summary(analysis_results),
            "strong_correlations": analysis_results.get('strong_correlations', []),
            "weak_correlations": analysis_results.get('weak_correlations', []),
            "causal_relationships": self._identify_causal_relationships(analysis_results),
            "correlation_matrix": analysis_results.get('correlation_matrix', {}),
            "factor_analysis": {
                "primary_factors": analysis_results.get('primary_factors', []),
                "secondary_factors": analysis_results.get('secondary_factors', []),
                "interaction_effects": analysis_results.get('interactions', [])
            },
            "predictive_relationships": analysis_results.get('predictive_power', {}),
            "actionable_correlations": self._extract_actionable_correlations(analysis_results),
            "recommendations": [asdict(rec) for rec in recommendations],
            "statistical_validation": analysis_results.get('validation', {}),
            "confidence_score": analysis_results.get('confidence', 0.8)
        }
        
        return template
    
    # Helper methods for template generation
    
    def _generate_delay_summary(self, results: Dict[str, Any]) -> str:
        """Generate delay analysis summary"""
        total_delays = results.get('total_delayed', 0)
        avg_delay = results.get('avg_delay', 0)
        top_cause = results.get('top_delay_cause', 'Unknown')
        
        return f"Analysis of {total_delays} delayed orders shows an average delay of {avg_delay:.1f} minutes, with {top_cause} being the primary cause."
    
    def _extract_delay_findings(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings from delay analysis"""
        findings = []
        
        # Top delay causes
        if 'delay_causes' in results:
            for cause, data in results['delay_causes'].items():
                findings.append({
                    "finding": f"{cause.replace('_', ' ').title()} caused {data.get('percentage', 0):.1f}% of delays",
                    "impact": f"Average delay: {data.get('avg_delay', 0):.1f} minutes",
                    "affected_orders": data.get('count', 0),
                    "severity": self._determine_severity(data.get('percentage', 0)),
                    "confidence": 0.9
                })
        
        return findings
    
    def _extract_trend_info(self, results: Dict[str, Any]) -> str:
        """Extract trend information"""
        trend_data = results.get('trend_analysis', {})
        direction = trend_data.get('direction', 'stable')
        change = trend_data.get('change_percentage', 0)
        
        if direction == 'increasing':
            return f"Delays have increased by {change:.1f}% compared to the previous period"
        elif direction == 'decreasing':
            return f"Delays have decreased by {abs(change):.1f}% compared to the previous period"
        else:
            return "Delay patterns remain stable with no significant trend"
    
    def _identify_delay_root_causes(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify root causes of delays"""
        causes = []
        
        if 'root_cause_analysis' in results:
            for cause, impact in results['root_cause_analysis'].items():
                causes.append({
                    "cause": cause,
                    "impact_score": impact.get('score', 0),
                    "frequency": impact.get('frequency', 0),
                    "mitigation_difficulty": impact.get('difficulty', 'medium')
                })
        
        return sorted(causes, key=lambda x: x['impact_score'], reverse=True)
    
    def _calculate_delay_financial_impact(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial impact of delays"""
        total_delayed = results.get('total_delayed', 0)
        avg_order_value = results.get('avg_order_value', 1000)  # Default assumption
        delay_cost_factor = 0.05  # 5% cost impact per delayed order
        
        return {
            "total_impact": total_delayed * avg_order_value * delay_cost_factor,
            "currency": "INR",
            "breakdown": {
                "customer_compensation": total_delayed * 100,  # ₹100 per delayed order
                "operational_overhead": total_delayed * 50,
                "reputation_impact": total_delayed * avg_order_value * 0.02
            },
            "impact_type": "cost"
        }
    
    def _generate_client_overview(self, results: Dict[str, Any]) -> str:
        """Generate client analysis overview"""
        client_name = results.get('client_name', 'Client')
        success_rate = results.get('success_rate', 0)
        total_orders = results.get('total_orders', 0)
        
        return f"{client_name} has a {success_rate:.1f}% success rate across {total_orders} orders with specific areas requiring attention."
    
    def _create_failure_breakdown(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create failure breakdown for client analysis"""
        failures = results.get('failure_analysis', {})
        total_failures = sum(data.get('count', 0) for data in failures.values())
        
        breakdown = {}
        for failure_type, data in failures.items():
            count = data.get('count', 0)
            percentage = (count / total_failures * 100) if total_failures > 0 else 0
            breakdown[failure_type] = {
                "count": count,
                "percentage": round(percentage, 1)
            }
        
        return breakdown
    
    def _calculate_client_financial_impact(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial impact for client"""
        failed_orders = results.get('failed_orders', 0)
        avg_order_value = results.get('avg_order_value', 1000)
        
        return {
            "total_impact": failed_orders * avg_order_value,
            "currency": "INR",
            "breakdown": {
                "lost_revenue": failed_orders * avg_order_value,
                "refunds_compensation": failed_orders * 200,
                "recovery_costs": failed_orders * 100
            },
            "impact_type": "revenue_loss"
        }
    
    def _extract_client_trends(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract client performance trends"""
        trend_data = results.get('trend_analysis', {})
        return {
            "performance_direction": trend_data.get('direction', 'stable'),
            "change_percentage": trend_data.get('change_percentage', 0),
            "trend_confidence": trend_data.get('confidence', 0.8),
            "seasonal_patterns": trend_data.get('seasonal_patterns', [])
        }
    
    def _assess_client_risk(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess client risk level"""
        success_rate = results.get('success_rate', 100)
        complaint_rate = results.get('complaint_rate', 0)
        payment_history = results.get('payment_score', 100)
        
        # Simple risk scoring
        risk_score = (100 - success_rate) + complaint_rate + (100 - payment_history)
        
        if risk_score < 10:
            risk_level = "low"
        elif risk_score < 30:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": self._identify_client_risk_factors(results),
            "mitigation_priority": "high" if risk_score > 30 else "medium"
        }
    
    def _identify_client_risk_factors(self, results: Dict[str, Any]) -> List[str]:
        """Identify specific risk factors for client"""
        factors = []
        
        if results.get('success_rate', 100) < 90:
            factors.append("Low delivery success rate")
        if results.get('complaint_rate', 0) > 5:
            factors.append("High complaint rate")
        if results.get('payment_score', 100) < 80:
            factors.append("Payment reliability issues")
        if results.get('order_frequency_decline', False):
            factors.append("Declining order frequency")
        
        return factors
    
    def _generate_efficiency_overview(self, results: Dict[str, Any]) -> str:
        """Generate operational efficiency overview"""
        efficiency_score = results.get('efficiency_score', 0)
        return f"Current operational efficiency is at {efficiency_score:.1f}% with key optimization opportunities identified."
    
    def _identify_bottlenecks(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify operational bottlenecks"""
        bottlenecks = []
        
        if 'bottleneck_analysis' in results:
            for bottleneck, data in results['bottleneck_analysis'].items():
                bottlenecks.append({
                    "process": bottleneck,
                    "impact_score": data.get('impact', 0),
                    "frequency": data.get('frequency', 0),
                    "resolution_difficulty": data.get('difficulty', 'medium')
                })
        
        return sorted(bottlenecks, key=lambda x: x['impact_score'], reverse=True)
    
    def _identify_optimization_opportunities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        if 'optimization_analysis' in results:
            for opp, data in results['optimization_analysis'].items():
                opportunities.append({
                    "opportunity": opp,
                    "potential_improvement": data.get('improvement', 0),
                    "implementation_cost": data.get('cost', 'medium'),
                    "roi_estimate": data.get('roi', 0)
                })
        
        return sorted(opportunities, key=lambda x: x['roi_estimate'], reverse=True)
    
    def _analyze_operational_costs(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operational costs"""
        return {
            "total_operational_cost": results.get('total_cost', 0),
            "cost_per_unit": results.get('cost_per_unit', 0),
            "cost_breakdown": results.get('cost_breakdown', {}),
            "cost_trends": results.get('cost_trends', {}),
            "cost_optimization_potential": results.get('cost_savings_potential', 0)
        }
    
    def _calculate_projected_improvements(self, results: Dict[str, Any], recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Calculate projected improvements from recommendations"""
        total_impact = 0
        implementation_cost = 0
        
        for rec in recommendations:
            # Extract numeric impact if possible
            impact_str = rec.expected_impact
            # Simple parsing - in real implementation, this would be more sophisticated
            if "%" in impact_str:
                try:
                    impact_val = float(impact_str.split("%")[0].split()[-1])
                    total_impact += impact_val
                except:
                    pass
        
        return {
            "projected_efficiency_gain": f"{total_impact:.1f}%",
            "estimated_cost_savings": results.get('projected_savings', 0),
            "implementation_timeline": "2-6 months",
            "roi_projection": "150-300%"
        }
    
    def _determine_severity(self, percentage: float) -> str:
        """Determine severity level based on percentage"""
        if percentage >= 40:
            return "critical"
        elif percentage >= 20:
            return "high"
        elif percentage >= 10:
            return "medium"
        else:
            return "low"
    
    # Additional helper methods for other templates...
    
    def _generate_prediction_summary(self, results: Dict[str, Any]) -> str:
        """Generate predictive analysis summary"""
        return "Predictive analysis based on historical patterns and current trends."
    
    def _identify_risk_factors(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risk factors from predictive analysis"""
        return results.get('risk_factors', [])
    
    def _generate_monitoring_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations"""
        return [
            "Monitor key performance indicators daily",
            "Set up automated alerts for threshold breaches",
            "Review predictions weekly and adjust models as needed"
        ]
    
    def _generate_comparison_summary(self, results: Dict[str, Any]) -> str:
        """Generate comparative analysis summary"""
        return "Comparative analysis reveals key performance differences and improvement opportunities."
    
    def _identify_performance_gaps(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance gaps"""
        return results.get('performance_gaps', [])
    
    def _analyze_performance_differences(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze root causes of performance differences"""
        return results.get('difference_analysis', [])
    
    def _generate_correlation_summary(self, results: Dict[str, Any]) -> str:
        """Generate correlation analysis summary"""
        return "Correlation analysis reveals relationships between key operational factors."
    
    def _identify_causal_relationships(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify causal relationships"""
        return results.get('causal_relationships', [])
    
    def _extract_actionable_correlations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable correlations"""
        return results.get('actionable_correlations', [])
