"""
OpenAI-powered narrative generator for human-readable insights
"""

import logging
from typing import Dict, List, Any, Optional
from ai.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """Generate human-readable narratives from structured insights using OpenAI"""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """Initialize narrative generator
        
        Args:
            openai_client: OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()
        self.logger = logging.getLogger(__name__)
    
    def generate_narrative(self, insight_data: Dict[str, Any], 
                          query_type: str,
                          target_audience: str = "operations_manager") -> str:
        """Generate human-readable narrative from insight data
        
        Args:
            insight_data: Structured insight data from templates
            query_type: Type of analysis (delay, client, efficiency, etc.)
            target_audience: Target audience for the narrative
            
        Returns:
            Human-readable narrative explanation
        """
        try:
            prompt = self._build_narrative_prompt(insight_data, query_type, target_audience)
            
            messages = [
                {"role": "system", "content": self._get_system_prompt(target_audience)},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client._make_request_with_retry(
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )
            
            narrative = response.choices[0].message.content
            self.logger.info(f"Generated narrative for {query_type} analysis")
            
            return narrative
            
        except Exception as e:
            self.logger.error(f"Error generating narrative: {e}")
            return self._generate_fallback_narrative(insight_data, query_type)
    
    def generate_executive_summary(self, insight_data: Dict[str, Any]) -> str:
        """Generate executive summary (2-3 sentences)
        
        Args:
            insight_data: Structured insight data
            
        Returns:
            Concise executive summary
        """
        try:
            key_metrics = self._extract_key_metrics(insight_data)
            analysis_type = insight_data.get('analysis_type', 'analysis')
            
            prompt = f"""
            Create a 2-3 sentence executive summary for this {analysis_type}:
            
            Key Metrics: {key_metrics}
            Summary: {insight_data.get('summary', '')}
            Top Finding: {self._get_top_finding(insight_data)}
            
            Focus on the most critical business impact and required action.
            """
            
            messages = [
                {"role": "system", "content": "You are an expert at creating concise executive summaries for business leaders."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client._make_request_with_retry(
                messages=messages,
                temperature=0.2,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            return f"Analysis completed with key findings requiring management attention."
    
    def generate_detailed_explanation(self, insight_data: Dict[str, Any],
                                    include_technical_details: bool = False) -> str:
        """Generate detailed explanation with root cause analysis
        
        Args:
            insight_data: Structured insight data
            include_technical_details: Whether to include technical details
            
        Returns:
            Detailed explanation with root cause analysis
        """
        try:
            prompt = self._build_detailed_explanation_prompt(insight_data, include_technical_details)
            
            messages = [
                {"role": "system", "content": self._get_detailed_analysis_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client._make_request_with_retry(
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating detailed explanation: {e}")
            return "Detailed analysis completed. Please refer to the structured data for specific insights."
    
    def generate_actionable_recommendations(self, recommendations: List[Dict[str, Any]],
                                          context: Dict[str, Any]) -> str:
        """Generate narrative for actionable recommendations
        
        Args:
            recommendations: List of recommendation objects
            context: Context about the analysis
            
        Returns:
            Human-readable recommendations narrative
        """
        try:
            if not recommendations:
                return "No specific recommendations generated from this analysis."
            
            prompt = f"""
            Convert these structured recommendations into a clear, actionable narrative:
            
            Context: {context.get('analysis_type', 'Analysis')} revealed several improvement opportunities.
            
            Recommendations:
            {self._format_recommendations_for_prompt(recommendations)}
            
            Create a narrative that:
            1. Prioritizes recommendations by impact and urgency
            2. Explains the expected benefits of each action
            3. Provides realistic implementation guidance
            4. Groups related recommendations together
            """
            
            messages = [
                {"role": "system", "content": "You are an expert operations consultant providing actionable business recommendations."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client._make_request_with_retry(
                messages=messages,
                temperature=0.3,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations narrative: {e}")
            return self._generate_fallback_recommendations(recommendations)
    
    def generate_trend_narrative(self, trend_data: Dict[str, Any]) -> str:
        """Generate narrative explanation of trends
        
        Args:
            trend_data: Trend analysis data
            
        Returns:
            Human-readable trend explanation
        """
        try:
            direction = trend_data.get('direction', 'stable')
            change = trend_data.get('change_percentage', 0)
            confidence = trend_data.get('confidence', 0)
            
            prompt = f"""
            Explain this trend analysis in business terms:
            
            Trend Direction: {direction}
            Change Percentage: {change}%
            Confidence Level: {confidence}
            Period Comparison: {trend_data.get('period_comparison', {})}
            Seasonal Patterns: {trend_data.get('seasonal_patterns', [])}
            
            Provide insights about:
            1. What the trend means for business operations
            2. Whether this is a concerning or positive development
            3. What factors might be driving this trend
            4. What to monitor going forward
            """
            
            messages = [
                {"role": "system", "content": "You are a business analyst explaining trends to operations managers."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client._make_request_with_retry(
                messages=messages,
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating trend narrative: {e}")
            return f"Trend analysis shows {direction} pattern with {abs(change):.1f}% change."
    
    def _build_narrative_prompt(self, insight_data: Dict[str, Any], 
                               query_type: str, 
                               target_audience: str) -> str:
        """Build the main narrative generation prompt"""
        analysis_type = insight_data.get('analysis_type', query_type)
        summary = insight_data.get('summary', '')
        key_findings = insight_data.get('key_findings', [])
        recommendations = insight_data.get('recommendations', [])
        
        prompt = f"""
        Generate a clear, actionable explanation for this {analysis_type} for {target_audience}:
        
        ANALYSIS SUMMARY:
        {summary}
        
        KEY FINDINGS:
        {self._format_findings_for_prompt(key_findings)}
        
        RECOMMENDATIONS:
        {self._format_recommendations_for_prompt(recommendations)}
        
        ADDITIONAL DATA:
        {self._format_additional_data_for_prompt(insight_data)}
        
        Generate a response that includes:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (bullet points with business impact)
        3. Root Cause Analysis (what's driving these issues)
        4. Actionable Recommendations (prioritized by impact)
        5. Expected Impact of Recommendations
        
        Use business language, avoid technical jargon, and focus on actionable insights.
        """
        
        return prompt
    
    def _build_detailed_explanation_prompt(self, insight_data: Dict[str, Any],
                                         include_technical: bool) -> str:
        """Build prompt for detailed explanation"""
        analysis_type = insight_data.get('analysis_type', 'analysis')
        
        technical_note = """
        Include technical details about:
        - Statistical methods used
        - Confidence levels and data quality
        - Assumptions and limitations
        """ if include_technical else "Focus on business implications, not technical details."
        
        prompt = f"""
        Provide a comprehensive explanation of this {analysis_type}:
        
        FULL INSIGHT DATA:
        {self._format_full_data_for_prompt(insight_data)}
        
        {technical_note}
        
        Structure your response as:
        1. Situation Overview
        2. Detailed Findings Analysis
        3. Root Cause Deep Dive
        4. Impact Assessment
        5. Strategic Implications
        6. Implementation Roadmap
        """
        
        return prompt
    
    def _get_system_prompt(self, target_audience: str) -> str:
        """Get system prompt based on target audience"""
        audience_prompts = {
            "operations_manager": """You are an expert logistics analyst explaining insights to operations managers. 
            Focus on operational efficiency, cost implications, and actionable improvements. 
            Use clear business language and provide specific, implementable recommendations.""",
            
            "executive": """You are a senior business consultant presenting to executives. 
            Focus on strategic implications, financial impact, and high-level recommendations. 
            Be concise, data-driven, and emphasize business outcomes.""",
            
            "technical_team": """You are a data analyst explaining findings to technical teams. 
            Include relevant technical details, methodology notes, and data quality considerations. 
            Balance technical accuracy with practical implementation guidance.""",
            
            "client": """You are a customer success manager explaining performance insights to clients. 
            Focus on service quality, improvement initiatives, and partnership opportunities. 
            Be transparent, solution-oriented, and emphasize mutual benefits."""
        }
        
        return audience_prompts.get(target_audience, audience_prompts["operations_manager"])
    
    def _get_detailed_analysis_system_prompt(self) -> str:
        """Get system prompt for detailed analysis"""
        return """You are a senior business analyst providing comprehensive operational insights. 
        Your analysis should be thorough, well-structured, and actionable. 
        Connect data points to business outcomes and provide clear implementation guidance. 
        Balance depth with clarity, ensuring insights are both comprehensive and accessible."""
    
    def _format_findings_for_prompt(self, findings: List[Dict[str, Any]]) -> str:
        """Format findings for prompt inclusion"""
        if not findings:
            return "No specific findings available."
        
        formatted = []
        for finding in findings[:5]:  # Limit to top 5 findings
            if isinstance(finding, dict):
                finding_text = finding.get('finding', str(finding))
                impact = finding.get('impact', '')
                affected = finding.get('affected_items', finding.get('affected_orders', 0))
                
                formatted.append(f"- {finding_text}")
                if impact:
                    formatted.append(f"  Impact: {impact}")
                if affected:
                    formatted.append(f"  Affected items: {affected}")
            else:
                formatted.append(f"- {finding}")
        
        return "\n".join(formatted)
    
    def _format_recommendations_for_prompt(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for prompt inclusion"""
        if not recommendations:
            return "No specific recommendations available."
        
        formatted = []
        for rec in recommendations[:5]:  # Limit to top 5 recommendations
            if isinstance(rec, dict):
                action = rec.get('action', str(rec))
                category = rec.get('category', '')
                impact = rec.get('expected_impact', '')
                effort = rec.get('implementation_effort', '')
                
                formatted.append(f"- {action}")
                if category:
                    formatted.append(f"  Category: {category}")
                if impact:
                    formatted.append(f"  Expected Impact: {impact}")
                if effort:
                    formatted.append(f"  Effort: {effort}")
            else:
                formatted.append(f"- {rec}")
        
        return "\n".join(formatted)
    
    def _format_additional_data_for_prompt(self, insight_data: Dict[str, Any]) -> str:
        """Format additional data for prompt inclusion"""
        additional_info = []
        
        # Financial impact
        if 'financial_impact' in insight_data:
            financial = insight_data['financial_impact']
            if isinstance(financial, dict):
                total_impact = financial.get('total_impact', 0)
                currency = financial.get('currency', 'INR')
                additional_info.append(f"Financial Impact: {currency} {total_impact:,.0f}")
        
        # Performance metrics
        if 'performance_metrics' in insight_data:
            metrics = insight_data['performance_metrics']
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    additional_info.append(f"{key.replace('_', ' ').title()}: {value}")
        
        # Trends
        if 'trends' in insight_data:
            trends = insight_data['trends']
            if isinstance(trends, str):
                additional_info.append(f"Trend: {trends}")
            elif isinstance(trends, dict):
                direction = trends.get('performance_direction', 'stable')
                change = trends.get('change_percentage', 0)
                additional_info.append(f"Trend: {direction} ({change:+.1f}%)")
        
        return "\n".join(additional_info) if additional_info else "No additional data available."
    
    def _format_full_data_for_prompt(self, insight_data: Dict[str, Any]) -> str:
        """Format full insight data for detailed analysis prompt"""
        # Simplified representation of the full data
        key_sections = ['summary', 'key_findings', 'trends', 'recommendations', 
                       'financial_impact', 'performance_metrics']
        
        formatted_sections = []
        for section in key_sections:
            if section in insight_data:
                data = insight_data[section]
                formatted_sections.append(f"{section.upper()}: {data}")
        
        return "\n\n".join(formatted_sections)
    
    def _extract_key_metrics(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from insight data"""
        key_metrics = {}
        
        # Look for common metric patterns
        metric_fields = ['total_orders', 'success_rate', 'efficiency_score', 
                        'total_delayed', 'avg_delay', 'failure_rate']
        
        for field in metric_fields:
            if field in insight_data:
                key_metrics[field] = insight_data[field]
        
        # Look in nested structures
        if 'performance_metrics' in insight_data:
            key_metrics.update(insight_data['performance_metrics'])
        
        if 'affected_metrics' in insight_data:
            key_metrics.update(insight_data['affected_metrics'])
        
        return key_metrics
    
    def _get_top_finding(self, insight_data: Dict[str, Any]) -> str:
        """Get the top finding from insight data"""
        findings = insight_data.get('key_findings', [])
        if findings and isinstance(findings, list) and len(findings) > 0:
            top_finding = findings[0]
            if isinstance(top_finding, dict):
                return top_finding.get('finding', 'Key issue identified')
            else:
                return str(top_finding)
        
        return insight_data.get('summary', 'Analysis completed')
    
    def _generate_fallback_narrative(self, insight_data: Dict[str, Any], query_type: str) -> str:
        """Generate fallback narrative when OpenAI fails"""
        analysis_type = insight_data.get('analysis_type', query_type)
        summary = insight_data.get('summary', f'{analysis_type} completed')
        
        narrative = f"**{analysis_type.replace('_', ' ').title()} Results**\n\n"
        narrative += f"{summary}\n\n"
        
        # Add key findings if available
        findings = insight_data.get('key_findings', [])
        if findings:
            narrative += "**Key Findings:**\n"
            for i, finding in enumerate(findings[:3], 1):
                if isinstance(finding, dict):
                    narrative += f"{i}. {finding.get('finding', 'Finding identified')}\n"
                else:
                    narrative += f"{i}. {finding}\n"
            narrative += "\n"
        
        # Add recommendations if available
        recommendations = insight_data.get('recommendations', [])
        if recommendations:
            narrative += "**Recommendations:**\n"
            for i, rec in enumerate(recommendations[:3], 1):
                if isinstance(rec, dict):
                    narrative += f"{i}. {rec.get('action', 'Action recommended')}\n"
                else:
                    narrative += f"{i}. {rec}\n"
        
        return narrative
    
    def _generate_fallback_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate fallback recommendations narrative"""
        if not recommendations:
            return "No specific recommendations available."
        
        narrative = "**Recommended Actions:**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, dict):
                action = rec.get('action', 'Action recommended')
                impact = rec.get('expected_impact', '')
                effort = rec.get('implementation_effort', '')
                
                narrative += f"{i}. {action}\n"
                if impact:
                    narrative += f"   Expected Impact: {impact}\n"
                if effort:
                    narrative += f"   Implementation Effort: {effort}\n"
                narrative += "\n"
            else:
                narrative += f"{i}. {rec}\n\n"
        
        return narrative
