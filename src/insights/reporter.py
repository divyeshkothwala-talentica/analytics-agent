"""
Comprehensive report generator for structured insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .processor import ResultProcessor
from .templates import InsightTemplates, Recommendation
from .narrator import NarrativeGenerator
from .visualizer import VisualizationDataPrep
from .recommender import RecommendationEngine

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comprehensive reports from analysis results"""
    
    def __init__(self, 
                 openai_client=None,
                 processor: Optional[ResultProcessor] = None,
                 templates: Optional[InsightTemplates] = None,
                 narrator: Optional[NarrativeGenerator] = None,
                 visualizer: Optional[VisualizationDataPrep] = None,
                 recommender: Optional[RecommendationEngine] = None):
        """Initialize report generator
        
        Args:
            openai_client: OpenAI client for narrative generation
            processor: Result processor instance
            templates: Insight templates instance
            narrator: Narrative generator instance
            visualizer: Visualization data prep instance
            recommender: Recommendation engine instance
        """
        self.processor = processor or ResultProcessor()
        self.templates = templates or InsightTemplates()
        self.narrator = narrator or NarrativeGenerator(openai_client)
        self.visualizer = visualizer or VisualizationDataPrep()
        self.recommender = recommender or RecommendationEngine()
        self.logger = logging.getLogger(__name__)
    
    def generate_executive_dashboard(self, 
                                   query_results: List[Dict[str, Any]],
                                   query_context: Dict[str, Any],
                                   time_period: str = "last_30_days") -> Dict[str, Any]:
        """Generate executive dashboard with high-level KPIs and trends
        
        Args:
            query_results: Raw query results from MongoDB
            query_context: Context about the query and analysis
            time_period: Time period for the analysis
            
        Returns:
            Executive dashboard data structure
        """
        try:
            self.logger.info("Generating executive dashboard")
            
            # Calculate key performance indicators
            kpis = self._calculate_executive_kpis(query_results, query_context)
            
            # Analyze trends
            trends = self._analyze_executive_trends(query_results, query_context)
            
            # Identify critical issues
            critical_issues = self._identify_critical_issues(query_results, query_context)
            
            # Generate high-level recommendations
            recommendations = self.recommender.generate_executive_recommendations(
                query_results, query_context
            )
            
            # Create visualizations
            visualizations = self._create_executive_visualizations(query_results, query_context)
            
            # Generate executive narrative
            executive_summary = self.narrator.generate_executive_summary({
                'kpis': kpis,
                'trends': trends,
                'critical_issues': critical_issues,
                'analysis_type': 'executive_dashboard'
            })
            
            dashboard = {
                'report_type': 'executive_dashboard',
                'generated_at': datetime.now().isoformat(),
                'time_period': time_period,
                'executive_summary': executive_summary,
                'key_performance_indicators': kpis,
                'trends_overview': trends,
                'critical_issues': critical_issues,
                'strategic_recommendations': [rec.__dict__ if hasattr(rec, '__dict__') else rec for rec in recommendations],
                'visualizations': visualizations,
                'performance_score': self._calculate_overall_performance_score(kpis),
                'risk_assessment': self._assess_overall_risk(critical_issues),
                'next_review_date': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error generating executive dashboard: {e}")
            return self._generate_error_report('executive_dashboard', str(e))
    
    def generate_operational_report(self, 
                                  query_results: List[Dict[str, Any]],
                                  query_context: Dict[str, Any],
                                  analysis_type: str = "operational_efficiency") -> Dict[str, Any]:
        """Generate detailed operational report with drill-down analysis
        
        Args:
            query_results: Raw query results from MongoDB
            query_context: Context about the query and analysis
            analysis_type: Type of operational analysis
            
        Returns:
            Detailed operational report
        """
        try:
            self.logger.info(f"Generating operational report for {analysis_type}")
            
            # Process results for detailed analysis
            processed_results = self._process_operational_data(query_results, query_context)
            
            # Generate recommendations
            recommendations = self.recommender.generate_operational_recommendations(
                query_results, query_context, analysis_type
            )
            
            # Create appropriate template
            if analysis_type == "delay_analysis":
                insight_template = self.templates.delay_analysis_template(
                    processed_results, recommendations
                )
            elif analysis_type == "client_analysis":
                insight_template = self.templates.client_analysis_template(
                    processed_results, recommendations
                )
            elif analysis_type == "operational_efficiency":
                insight_template = self.templates.operational_efficiency_template(
                    processed_results, recommendations
                )
            else:
                # Generic operational template
                insight_template = self._create_generic_operational_template(
                    processed_results, recommendations, analysis_type
                )
            
            # Generate narrative
            narrative = self.narrator.generate_narrative(
                insight_template, analysis_type, "operations_manager"
            )
            
            # Create detailed visualizations
            visualizations = self._create_operational_visualizations(
                query_results, query_context, analysis_type
            )
            
            # Add drill-down data
            drill_down_data = self._create_drill_down_data(query_results, query_context)
            
            operational_report = {
                'report_type': 'operational_report',
                'analysis_type': analysis_type,
                'generated_at': datetime.now().isoformat(),
                'narrative_summary': narrative,
                'detailed_insights': insight_template,
                'visualizations': visualizations,
                'drill_down_data': drill_down_data,
                'action_items': self._prioritize_action_items(recommendations),
                'performance_metrics': processed_results.get('performance_metrics', {}),
                'comparative_analysis': self._generate_comparative_analysis(query_results, query_context),
                'data_quality_notes': self._assess_data_quality(query_results)
            }
            
            return operational_report
            
        except Exception as e:
            self.logger.error(f"Error generating operational report: {e}")
            return self._generate_error_report('operational_report', str(e))
    
    def generate_comparative_analysis(self, 
                                    baseline_results: List[Dict[str, Any]],
                                    comparison_results: List[Dict[str, Any]],
                                    comparison_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative analysis report
        
        Args:
            baseline_results: Baseline period results
            comparison_results: Comparison period results
            comparison_context: Context about the comparison
            
        Returns:
            Comparative analysis report
        """
        try:
            self.logger.info("Generating comparative analysis report")
            
            # Process both datasets
            baseline_processed = self._process_operational_data(baseline_results, comparison_context)
            comparison_processed = self._process_operational_data(comparison_results, comparison_context)
            
            # Calculate differences and changes
            comparison_analysis = self._calculate_period_comparison(
                baseline_processed, comparison_processed
            )
            
            # Generate recommendations based on comparison
            recommendations = self.recommender.generate_comparative_recommendations(
                comparison_analysis, comparison_context
            )
            
            # Create comparative template
            insight_template = self.templates.comparative_analysis_template(
                comparison_analysis, recommendations
            )
            
            # Generate narrative
            narrative = self.narrator.generate_narrative(
                insight_template, "comparative_analysis", "operations_manager"
            )
            
            # Create comparative visualizations
            visualizations = self._create_comparative_visualizations(
                baseline_results, comparison_results, comparison_context
            )
            
            comparative_report = {
                'report_type': 'comparative_analysis',
                'generated_at': datetime.now().isoformat(),
                'comparison_periods': {
                    'baseline': comparison_context.get('baseline_period', 'Previous Period'),
                    'comparison': comparison_context.get('comparison_period', 'Current Period')
                },
                'narrative_summary': narrative,
                'detailed_insights': insight_template,
                'performance_changes': comparison_analysis.get('performance_changes', {}),
                'statistical_significance': comparison_analysis.get('statistical_tests', {}),
                'visualizations': visualizations,
                'improvement_opportunities': [rec.__dict__ if hasattr(rec, '__dict__') else rec for rec in recommendations],
                'key_takeaways': self._extract_key_takeaways(comparison_analysis)
            }
            
            return comparative_report
            
        except Exception as e:
            self.logger.error(f"Error generating comparative analysis: {e}")
            return self._generate_error_report('comparative_analysis', str(e))
    
    def generate_predictive_insights(self, 
                                   historical_results: List[Dict[str, Any]],
                                   prediction_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive insights report
        
        Args:
            historical_results: Historical data for predictions
            prediction_context: Context about the prediction requirements
            
        Returns:
            Predictive insights report
        """
        try:
            self.logger.info("Generating predictive insights report")
            
            # Analyze historical trends
            trend_analysis = self.processor.analyze_trends(
                historical_results,
                prediction_context.get('time_field', 'timestamp'),
                prediction_context.get('value_field', 'value')
            )
            
            # Generate predictions (simplified statistical approach)
            predictions = self._generate_statistical_predictions(historical_results, prediction_context)
            
            # Identify risk factors
            risk_factors = self._identify_predictive_risk_factors(historical_results, predictions)
            
            # Generate predictive recommendations
            recommendations = self.recommender.generate_predictive_recommendations(
                predictions, risk_factors, prediction_context
            )
            
            # Create predictive template
            prediction_data = {
                'trend_analysis': trend_analysis.__dict__ if hasattr(trend_analysis, '__dict__') else trend_analysis,
                'predictions': predictions,
                'risk_factors': risk_factors,
                'confidence': predictions.get('confidence', 0.7)
            }
            
            insight_template = self.templates.predictive_analysis_template(
                prediction_data, recommendations
            )
            
            # Generate narrative
            narrative = self.narrator.generate_narrative(
                insight_template, "predictive_analysis", "operations_manager"
            )
            
            # Create predictive visualizations
            visualizations = self._create_predictive_visualizations(
                historical_results, predictions, prediction_context
            )
            
            predictive_report = {
                'report_type': 'predictive_insights',
                'generated_at': datetime.now().isoformat(),
                'prediction_horizon': prediction_context.get('horizon', '30 days'),
                'narrative_summary': narrative,
                'detailed_insights': insight_template,
                'forecasts': predictions,
                'trend_analysis': trend_analysis.__dict__ if hasattr(trend_analysis, '__dict__') else trend_analysis,
                'risk_assessment': risk_factors,
                'visualizations': visualizations,
                'model_accuracy': predictions.get('model_accuracy', {}),
                'monitoring_recommendations': self._generate_monitoring_recommendations(predictions),
                'confidence_intervals': predictions.get('confidence_intervals', {})
            }
            
            return predictive_report
            
        except Exception as e:
            self.logger.error(f"Error generating predictive insights: {e}")
            return self._generate_error_report('predictive_insights', str(e))
    
    # Helper methods
    
    def _calculate_executive_kpis(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance indicators for executives"""
        kpis = {}
        
        try:
            # Basic metrics
            total_records = len(results)
            kpis['total_operations'] = total_records
            
            # Success/failure rates
            if results:
                success_count = sum(1 for r in results if r.get('status') in ['completed', 'delivered', 'success'])
                kpis['success_rate'] = round((success_count / total_records) * 100, 1) if total_records > 0 else 0
                kpis['failure_rate'] = round(100 - kpis['success_rate'], 1)
            
            # Financial metrics (if available)
            if any('amount' in r or 'value' in r or 'cost' in r for r in results):
                amounts = [r.get('amount', r.get('value', r.get('cost', 0))) for r in results]
                amounts = [a for a in amounts if isinstance(a, (int, float))]
                if amounts:
                    kpis['total_value'] = sum(amounts)
                    kpis['average_value'] = round(sum(amounts) / len(amounts), 2)
            
            # Time-based metrics
            if any('delay' in r or 'processing_time' in r for r in results):
                delays = [r.get('delay_minutes', r.get('processing_time_minutes', 0)) for r in results]
                delays = [d for d in delays if isinstance(d, (int, float)) and d > 0]
                if delays:
                    kpis['average_delay_minutes'] = round(sum(delays) / len(delays), 1)
                    kpis['on_time_percentage'] = round(((total_records - len(delays)) / total_records) * 100, 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating executive KPIs: {e}")
            kpis['calculation_error'] = str(e)
        
        return kpis
    
    def _analyze_executive_trends(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends for executive dashboard"""
        trends = {}
        
        try:
            # Look for time-based data
            time_field = context.get('time_field', 'timestamp')
            value_field = context.get('value_field', 'value')
            
            if results and any(time_field in r for r in results):
                trend_analysis = self.processor.analyze_trends(results, time_field, value_field)
                trends = {
                    'direction': trend_analysis.direction,
                    'change_percentage': trend_analysis.change_percentage,
                    'confidence': trend_analysis.confidence,
                    'summary': f"Performance is {trend_analysis.direction} by {abs(trend_analysis.change_percentage):.1f}%"
                }
        except Exception as e:
            self.logger.error(f"Error analyzing executive trends: {e}")
            trends['analysis_error'] = str(e)
        
        return trends
    
    def _identify_critical_issues(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical issues requiring executive attention"""
        critical_issues = []
        
        try:
            # High failure rates
            if results:
                failure_count = sum(1 for r in results if r.get('status') in ['failed', 'cancelled', 'error'])
                failure_rate = (failure_count / len(results)) * 100 if results else 0
                
                if failure_rate > 10:  # More than 10% failure rate
                    critical_issues.append({
                        'issue': 'High Failure Rate',
                        'severity': 'critical' if failure_rate > 20 else 'high',
                        'impact': f'{failure_rate:.1f}% of operations are failing',
                        'affected_count': failure_count
                    })
            
            # Detect anomalies
            if results and any(isinstance(r.get('value', r.get('amount', 0)), (int, float)) for r in results):
                anomalies = self.processor.detect_anomalies(results, 'value')
                if anomalies.total_anomalies > 0:
                    critical_issues.append({
                        'issue': 'Performance Anomalies Detected',
                        'severity': 'medium',
                        'impact': f'{anomalies.total_anomalies} unusual patterns identified',
                        'affected_count': anomalies.total_anomalies
                    })
        
        except Exception as e:
            self.logger.error(f"Error identifying critical issues: {e}")
        
        return critical_issues
    
    def _create_executive_visualizations(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create visualizations for executive dashboard"""
        visualizations = []
        
        try:
            # Success/Failure pie chart
            if results:
                status_data = [{'status': r.get('status', 'unknown')} for r in results]
                pie_chart = self.visualizer.prepare_pie_chart_data(status_data, 'status')
                if pie_chart['labels']:
                    visualizations.append({
                        'type': 'pie_chart',
                        'title': 'Operations Status Distribution',
                        'data': pie_chart
                    })
            
            # Trend line chart (if time data available)
            time_field = context.get('time_field', 'timestamp')
            if results and any(time_field in r for r in results):
                time_series = self.visualizer.prepare_time_series_data(
                    results, time_field, 'value', 'count', 'daily'
                )
                if time_series['labels']:
                    visualizations.append({
                        'type': 'line_chart',
                        'title': 'Operations Trend Over Time',
                        'data': time_series
                    })
        
        except Exception as e:
            self.logger.error(f"Error creating executive visualizations: {e}")
        
        return visualizations
    
    def _process_operational_data(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw results for operational analysis"""
        processed = {
            'total_records': len(results),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Calculate basic statistics
            if results:
                # Success rates
                success_statuses = ['completed', 'delivered', 'success']
                success_count = sum(1 for r in results if r.get('status') in success_statuses)
                processed['success_rate'] = (success_count / len(results)) * 100
                
                # Pattern detection
                if any('failure_reason' in r for r in results):
                    failure_patterns = self.processor.detect_patterns(results, 'failure_reason', 'count')
                    processed['failure_patterns'] = failure_patterns
                
                # Statistical analysis on numeric fields
                numeric_fields = ['delay_minutes', 'processing_time', 'amount', 'value']
                for field in numeric_fields:
                    if any(field in r for r in results):
                        stats = self.processor.calculate_statistics(results, field)
                        if stats:
                            processed[f'{field}_statistics'] = stats.__dict__
        
        except Exception as e:
            self.logger.error(f"Error processing operational data: {e}")
            processed['processing_error'] = str(e)
        
        return processed
    
    def _calculate_overall_performance_score(self, kpis: Dict[str, Any]) -> float:
        """Calculate overall performance score from KPIs"""
        try:
            score = 0.0
            factors = 0
            
            # Success rate (40% weight)
            if 'success_rate' in kpis:
                score += (kpis['success_rate'] / 100) * 0.4
                factors += 0.4
            
            # On-time performance (30% weight)
            if 'on_time_percentage' in kpis:
                score += (kpis['on_time_percentage'] / 100) * 0.3
                factors += 0.3
            
            # Efficiency (30% weight) - inverse of average delay
            if 'average_delay_minutes' in kpis:
                # Convert delay to efficiency score (lower delay = higher score)
                delay_score = max(0, 1 - (kpis['average_delay_minutes'] / 120))  # 120 min = 0 score
                score += delay_score * 0.3
                factors += 0.3
            
            return round((score / factors) * 100, 1) if factors > 0 else 50.0
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return 50.0
    
    def _assess_overall_risk(self, critical_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall risk level from critical issues"""
        if not critical_issues:
            return {'level': 'low', 'score': 10, 'summary': 'No critical issues identified'}
        
        # Calculate risk score
        risk_score = 0
        for issue in critical_issues:
            severity = issue.get('severity', 'medium')
            if severity == 'critical':
                risk_score += 30
            elif severity == 'high':
                risk_score += 20
            elif severity == 'medium':
                risk_score += 10
            else:
                risk_score += 5
        
        # Determine risk level
        if risk_score >= 50:
            level = 'critical'
        elif risk_score >= 30:
            level = 'high'
        elif risk_score >= 15:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': min(risk_score, 100),
            'summary': f'{len(critical_issues)} critical issues requiring attention',
            'top_issue': critical_issues[0]['issue'] if critical_issues else None
        }
    
    def _generate_error_report(self, report_type: str, error_message: str) -> Dict[str, Any]:
        """Generate error report when processing fails"""
        return {
            'report_type': report_type,
            'status': 'error',
            'generated_at': datetime.now().isoformat(),
            'error_message': error_message,
            'summary': f'Report generation failed: {error_message}',
            'recommendations': ['Check data quality and try again', 'Contact system administrator if issue persists']
        }
    
    # Additional helper methods for other report types...
    
    def _create_operational_visualizations(self, results: List[Dict[str, Any]], context: Dict[str, Any], analysis_type: str) -> List[Dict[str, Any]]:
        """Create visualizations for operational reports"""
        # Implementation would create specific visualizations based on analysis type
        return []
    
    def _create_drill_down_data(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create drill-down data for detailed analysis"""
        # Implementation would create hierarchical data for drilling down
        return {}
    
    def _prioritize_action_items(self, recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
        """Prioritize action items from recommendations"""
        # Implementation would sort and prioritize recommendations
        return [rec.__dict__ if hasattr(rec, '__dict__') else rec for rec in recommendations]
    
    def _generate_comparative_analysis(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative analysis data"""
        # Implementation would compare current results with historical data
        return {}
    
    def _assess_data_quality(self, results: List[Dict[str, Any]]) -> List[str]:
        """Assess data quality and return notes"""
        notes = []
        if not results:
            notes.append("No data available for analysis")
        elif len(results) < 10:
            notes.append("Limited data sample - results may not be representative")
        return notes
    
    def _calculate_period_comparison(self, baseline: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comparison between two periods"""
        # Implementation would compare metrics between periods
        return {'baseline': baseline, 'comparison': comparison}
    
    def _create_comparative_visualizations(self, baseline_results: List[Dict[str, Any]], comparison_results: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create comparative visualizations"""
        # Implementation would create side-by-side comparisons
        return []
    
    def _extract_key_takeaways(self, comparison_analysis: Dict[str, Any]) -> List[str]:
        """Extract key takeaways from comparative analysis"""
        # Implementation would extract main insights
        return []
    
    def _generate_statistical_predictions(self, historical_results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistical predictions from historical data"""
        # Simplified prediction implementation
        return {'confidence': 0.7, 'predictions': {}}
    
    def _identify_predictive_risk_factors(self, historical_results: List[Dict[str, Any]], predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risk factors for predictions"""
        # Implementation would identify potential risks
        return []
    
    def _create_predictive_visualizations(self, historical_results: List[Dict[str, Any]], predictions: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create predictive visualizations"""
        # Implementation would create forecast charts
        return []
    
    def _generate_monitoring_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations for predictions"""
        return [
            "Monitor key performance indicators daily",
            "Set up automated alerts for threshold breaches",
            "Review predictions weekly and adjust models as needed"
        ]
    
    def _create_generic_operational_template(self, processed_results: Dict[str, Any], recommendations: List[Recommendation], analysis_type: str) -> Dict[str, Any]:
        """Create generic operational template for unknown analysis types"""
        return {
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'summary': f'{analysis_type} analysis completed',
            'processed_data': processed_results,
            'recommendations': [rec.__dict__ if hasattr(rec, '__dict__') else rec for rec in recommendations],
            'confidence_score': 0.8
        }
