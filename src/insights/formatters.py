"""
Multiple output formatters for different presentation formats
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseFormatter(ABC):
    """Base class for output formatters"""
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """Format data to specific output format"""
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get content type for the formatted output"""
        pass


class JSONFormatter(BaseFormatter):
    """Format output as JSON"""
    
    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        """Initialize JSON formatter
        
        Args:
            indent: Number of spaces for indentation
            ensure_ascii: Whether to escape non-ASCII characters
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as JSON string"""
        try:
            return json.dumps(data, indent=self.indent, ensure_ascii=self.ensure_ascii, default=self._json_serializer)
        except Exception as e:
            logger.error(f"Error formatting JSON: {e}")
            return json.dumps({"error": f"JSON formatting failed: {str(e)}"}, indent=self.indent)
    
    def get_content_type(self) -> str:
        """Get JSON content type"""
        return "application/json"
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-serializable objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, '_asdict'):
            return obj._asdict()
        else:
            return str(obj)


class MarkdownFormatter(BaseFormatter):
    """Format output as Markdown"""
    
    def __init__(self, include_toc: bool = True, max_depth: int = 3):
        """Initialize Markdown formatter
        
        Args:
            include_toc: Whether to include table of contents
            max_depth: Maximum heading depth for TOC
        """
        self.include_toc = include_toc
        self.max_depth = max_depth
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as Markdown string"""
        try:
            markdown_content = []
            
            # Title
            report_type = data.get('report_type', 'Analysis Report').replace('_', ' ').title()
            markdown_content.append(f"# {report_type}")
            markdown_content.append("")
            
            # Metadata
            generated_at = data.get('generated_at', datetime.now().isoformat())
            markdown_content.append(f"**Generated:** {self._format_datetime(generated_at)}")
            
            if 'analysis_type' in data:
                analysis_type = data['analysis_type'].replace('_', ' ').title()
                markdown_content.append(f"**Analysis Type:** {analysis_type}")
            
            markdown_content.append("")
            
            # Table of Contents
            if self.include_toc:
                toc = self._generate_toc(data)
                if toc:
                    markdown_content.append("## Table of Contents")
                    markdown_content.extend(toc)
                    markdown_content.append("")
            
            # Executive Summary
            if 'executive_summary' in data:
                markdown_content.append("## Executive Summary")
                markdown_content.append("")
                markdown_content.append(data['executive_summary'])
                markdown_content.append("")
            
            # Narrative Summary
            if 'narrative_summary' in data:
                markdown_content.append("## Summary")
                markdown_content.append("")
                markdown_content.append(data['narrative_summary'])
                markdown_content.append("")
            
            # Key Performance Indicators
            if 'key_performance_indicators' in data:
                markdown_content.extend(self._format_kpis(data['key_performance_indicators']))
            
            # Key Findings
            if 'key_findings' in data:
                markdown_content.extend(self._format_key_findings(data['key_findings']))
            
            # Detailed Insights
            if 'detailed_insights' in data:
                markdown_content.extend(self._format_detailed_insights(data['detailed_insights']))
            
            # Recommendations
            if 'recommendations' in data:
                markdown_content.extend(self._format_recommendations(data['recommendations']))
            elif 'strategic_recommendations' in data:
                markdown_content.extend(self._format_recommendations(data['strategic_recommendations']))
            elif 'action_items' in data:
                markdown_content.extend(self._format_recommendations(data['action_items']))
            
            # Visualizations
            if 'visualizations' in data:
                markdown_content.extend(self._format_visualizations(data['visualizations']))
            
            # Additional sections
            additional_sections = [
                ('trends_overview', 'Trends Overview'),
                ('critical_issues', 'Critical Issues'),
                ('performance_metrics', 'Performance Metrics'),
                ('risk_assessment', 'Risk Assessment'),
                ('comparative_analysis', 'Comparative Analysis'),
                ('forecasts', 'Forecasts'),
                ('data_quality_notes', 'Data Quality Notes')
            ]
            
            for key, title in additional_sections:
                if key in data and data[key]:
                    markdown_content.append(f"## {title}")
                    markdown_content.append("")
                    markdown_content.extend(self._format_generic_section(data[key]))
                    markdown_content.append("")
            
            return "\n".join(markdown_content)
            
        except Exception as e:
            logger.error(f"Error formatting Markdown: {e}")
            return f"# Error\n\nMarkdown formatting failed: {str(e)}"
    
    def get_content_type(self) -> str:
        """Get Markdown content type"""
        return "text/markdown"
    
    def _generate_toc(self, data: Dict[str, Any]) -> List[str]:
        """Generate table of contents"""
        toc = []
        
        sections = [
            ("Executive Summary", "executive_summary"),
            ("Summary", "narrative_summary"),
            ("Key Performance Indicators", "key_performance_indicators"),
            ("Key Findings", "key_findings"),
            ("Detailed Insights", "detailed_insights"),
            ("Recommendations", "recommendations"),
            ("Visualizations", "visualizations"),
            ("Trends Overview", "trends_overview"),
            ("Critical Issues", "critical_issues"),
            ("Performance Metrics", "performance_metrics"),
            ("Risk Assessment", "risk_assessment")
        ]
        
        for title, key in sections:
            if key in data and data[key]:
                toc.append(f"- [{title}](#{title.lower().replace(' ', '-')})")
        
        return toc
    
    def _format_kpis(self, kpis: Dict[str, Any]) -> List[str]:
        """Format KPIs section"""
        content = ["## Key Performance Indicators", ""]
        
        if isinstance(kpis, dict):
            for key, value in kpis.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (int, float)):
                    if 'rate' in key or 'percentage' in key:
                        content.append(f"- **{formatted_key}:** {value:.1f}%")
                    elif 'amount' in key or 'value' in key or 'cost' in key:
                        content.append(f"- **{formatted_key}:** ₹{value:,.2f}")
                    else:
                        content.append(f"- **{formatted_key}:** {value:,.0f}")
                else:
                    content.append(f"- **{formatted_key}:** {value}")
        else:
            content.append(str(kpis))
        
        content.append("")
        return content
    
    def _format_key_findings(self, findings: List[Any]) -> List[str]:
        """Format key findings section"""
        content = ["## Key Findings", ""]
        
        if isinstance(findings, list):
            for i, finding in enumerate(findings, 1):
                if isinstance(finding, dict):
                    finding_text = finding.get('finding', str(finding))
                    impact = finding.get('impact', '')
                    affected = finding.get('affected_items', finding.get('affected_orders', 0))
                    
                    content.append(f"### {i}. {finding_text}")
                    if impact:
                        content.append(f"**Impact:** {impact}")
                    if affected:
                        content.append(f"**Affected Items:** {affected:,}")
                    content.append("")
                else:
                    content.append(f"{i}. {finding}")
                    content.append("")
        else:
            content.append(str(findings))
            content.append("")
        
        return content
    
    def _format_detailed_insights(self, insights: Dict[str, Any]) -> List[str]:
        """Format detailed insights section"""
        content = ["## Detailed Analysis", ""]
        
        if isinstance(insights, dict):
            # Summary
            if 'summary' in insights:
                content.append("### Overview")
                content.append(insights['summary'])
                content.append("")
            
            # Performance metrics
            if 'performance_metrics' in insights:
                content.append("### Performance Metrics")
                metrics = insights['performance_metrics']
                if isinstance(metrics, dict):
                    for key, value in metrics.items():
                        formatted_key = key.replace('_', ' ').title()
                        content.append(f"- **{formatted_key}:** {value}")
                content.append("")
            
            # Financial impact
            if 'financial_impact' in insights:
                content.extend(self._format_financial_impact(insights['financial_impact']))
            
            # Trends
            if 'trends' in insights:
                content.append("### Trends")
                trends = insights['trends']
                if isinstance(trends, str):
                    content.append(trends)
                elif isinstance(trends, dict):
                    for key, value in trends.items():
                        formatted_key = key.replace('_', ' ').title()
                        content.append(f"- **{formatted_key}:** {value}")
                content.append("")
        
        return content
    
    def _format_recommendations(self, recommendations: List[Any]) -> List[str]:
        """Format recommendations section"""
        content = ["## Recommendations", ""]
        
        if isinstance(recommendations, list):
            # Group by category
            categorized = {}
            for rec in recommendations:
                if isinstance(rec, dict):
                    category = rec.get('category', 'General').title()
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(rec)
                else:
                    if 'General' not in categorized:
                        categorized['General'] = []
                    categorized['General'].append(rec)
            
            # Format by category
            for category, recs in categorized.items():
                content.append(f"### {category} Recommendations")
                content.append("")
                
                for i, rec in enumerate(recs, 1):
                    if isinstance(rec, dict):
                        action = rec.get('action', str(rec))
                        impact = rec.get('expected_impact', '')
                        effort = rec.get('implementation_effort', '')
                        timeline = rec.get('timeline', '')
                        priority = rec.get('priority', '')
                        
                        content.append(f"#### {i}. {action}")
                        if impact:
                            content.append(f"**Expected Impact:** {impact}")
                        if effort:
                            content.append(f"**Implementation Effort:** {effort.title()}")
                        if timeline:
                            content.append(f"**Timeline:** {timeline}")
                        if priority:
                            priority_emoji = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(priority.lower(), '')
                            content.append(f"**Priority:** {priority_emoji} {priority.title()}")
                        content.append("")
                    else:
                        content.append(f"{i}. {rec}")
                        content.append("")
        
        return content
    
    def _format_financial_impact(self, financial_impact: Dict[str, Any]) -> List[str]:
        """Format financial impact section"""
        content = ["### Financial Impact", ""]
        
        if isinstance(financial_impact, dict):
            total_impact = financial_impact.get('total_impact', 0)
            currency = financial_impact.get('currency', 'INR')
            impact_type = financial_impact.get('impact_type', 'impact')
            
            content.append(f"**Total {impact_type.replace('_', ' ').title()}:** {currency} {total_impact:,.2f}")
            
            # Breakdown
            breakdown = financial_impact.get('breakdown', {})
            if breakdown:
                content.append("")
                content.append("**Breakdown:**")
                for key, value in breakdown.items():
                    formatted_key = key.replace('_', ' ').title()
                    content.append(f"- {formatted_key}: {currency} {value:,.2f}")
        
        content.append("")
        return content
    
    def _format_visualizations(self, visualizations: List[Dict[str, Any]]) -> List[str]:
        """Format visualizations section"""
        content = ["## Visualizations", ""]
        
        if isinstance(visualizations, list):
            for i, viz in enumerate(visualizations, 1):
                if isinstance(viz, dict):
                    title = viz.get('title', f'Visualization {i}')
                    viz_type = viz.get('type', 'chart')
                    
                    content.append(f"### {title}")
                    content.append(f"**Type:** {viz_type.replace('_', ' ').title()}")
                    
                    # Add placeholder for actual visualization
                    content.append("*[Visualization would be rendered here]*")
                    content.append("")
        
        return content
    
    def _format_generic_section(self, section_data: Any) -> List[str]:
        """Format generic section data"""
        content = []
        
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (list, dict)):
                    content.append(f"**{formatted_key}:**")
                    content.append(f"```json")
                    content.append(json.dumps(value, indent=2))
                    content.append("```")
                else:
                    content.append(f"**{formatted_key}:** {value}")
        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        formatted_key = key.replace('_', ' ').title()
                        content.append(f"- **{formatted_key}:** {value}")
                else:
                    content.append(f"- {item}")
        else:
            content.append(str(section_data))
        
        return content
    
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return dt_string


class PlainTextFormatter(BaseFormatter):
    """Format output as plain text"""
    
    def __init__(self, line_width: int = 80, indent_size: int = 2):
        """Initialize plain text formatter
        
        Args:
            line_width: Maximum line width for text wrapping
            indent_size: Number of spaces for indentation
        """
        self.line_width = line_width
        self.indent_size = indent_size
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as plain text string"""
        try:
            lines = []
            
            # Title
            report_type = data.get('report_type', 'Analysis Report').replace('_', ' ').title()
            lines.append("=" * len(report_type))
            lines.append(report_type)
            lines.append("=" * len(report_type))
            lines.append("")
            
            # Metadata
            generated_at = data.get('generated_at', datetime.now().isoformat())
            lines.append(f"Generated: {self._format_datetime(generated_at)}")
            
            if 'analysis_type' in data:
                analysis_type = data['analysis_type'].replace('_', ' ').title()
                lines.append(f"Analysis Type: {analysis_type}")
            
            lines.append("")
            
            # Executive Summary
            if 'executive_summary' in data:
                lines.append("EXECUTIVE SUMMARY")
                lines.append("-" * 17)
                lines.extend(self._wrap_text(data['executive_summary']))
                lines.append("")
            
            # Narrative Summary
            if 'narrative_summary' in data:
                lines.append("SUMMARY")
                lines.append("-" * 7)
                lines.extend(self._wrap_text(data['narrative_summary']))
                lines.append("")
            
            # Key Performance Indicators
            if 'key_performance_indicators' in data:
                lines.extend(self._format_kpis_text(data['key_performance_indicators']))
            
            # Key Findings
            if 'key_findings' in data:
                lines.extend(self._format_findings_text(data['key_findings']))
            
            # Recommendations
            if 'recommendations' in data:
                lines.extend(self._format_recommendations_text(data['recommendations']))
            elif 'strategic_recommendations' in data:
                lines.extend(self._format_recommendations_text(data['strategic_recommendations']))
            
            # Additional sections
            additional_sections = [
                ('critical_issues', 'CRITICAL ISSUES'),
                ('trends_overview', 'TRENDS OVERVIEW'),
                ('risk_assessment', 'RISK ASSESSMENT')
            ]
            
            for key, title in additional_sections:
                if key in data and data[key]:
                    lines.append(title)
                    lines.append("-" * len(title))
                    lines.extend(self._format_generic_text(data[key]))
                    lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting plain text: {e}")
            return f"ERROR: Plain text formatting failed: {str(e)}"
    
    def get_content_type(self) -> str:
        """Get plain text content type"""
        return "text/plain"
    
    def _wrap_text(self, text: str, indent: int = 0) -> List[str]:
        """Wrap text to specified line width"""
        if not text:
            return [""]
        
        words = text.split()
        lines = []
        current_line = " " * indent
        
        for word in words:
            if len(current_line + word) <= self.line_width:
                if current_line.strip():
                    current_line += " " + word
                else:
                    current_line = " " * indent + word
            else:
                if current_line.strip():
                    lines.append(current_line)
                current_line = " " * indent + word
        
        if current_line.strip():
            lines.append(current_line)
        
        return lines if lines else [""]
    
    def _format_kpis_text(self, kpis: Dict[str, Any]) -> List[str]:
        """Format KPIs as plain text"""
        lines = ["KEY PERFORMANCE INDICATORS"]
        lines.append("-" * 28)
        
        if isinstance(kpis, dict):
            for key, value in kpis.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (int, float)):
                    if 'rate' in key or 'percentage' in key:
                        lines.append(f"  {formatted_key}: {value:.1f}%")
                    elif 'amount' in key or 'value' in key or 'cost' in key:
                        lines.append(f"  {formatted_key}: ₹{value:,.2f}")
                    else:
                        lines.append(f"  {formatted_key}: {value:,.0f}")
                else:
                    lines.append(f"  {formatted_key}: {value}")
        
        lines.append("")
        return lines
    
    def _format_findings_text(self, findings: List[Any]) -> List[str]:
        """Format findings as plain text"""
        lines = ["KEY FINDINGS"]
        lines.append("-" * 12)
        
        if isinstance(findings, list):
            for i, finding in enumerate(findings, 1):
                if isinstance(finding, dict):
                    finding_text = finding.get('finding', str(finding))
                    impact = finding.get('impact', '')
                    affected = finding.get('affected_items', finding.get('affected_orders', 0))
                    
                    lines.append(f"{i}. {finding_text}")
                    if impact:
                        lines.extend(self._wrap_text(f"Impact: {impact}", self.indent_size))
                    if affected:
                        lines.append(f"   Affected Items: {affected:,}")
                    lines.append("")
                else:
                    lines.extend(self._wrap_text(f"{i}. {finding}"))
                    lines.append("")
        
        return lines
    
    def _format_recommendations_text(self, recommendations: List[Any]) -> List[str]:
        """Format recommendations as plain text"""
        lines = ["RECOMMENDATIONS"]
        lines.append("-" * 15)
        
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                if isinstance(rec, dict):
                    action = rec.get('action', str(rec))
                    impact = rec.get('expected_impact', '')
                    effort = rec.get('implementation_effort', '')
                    timeline = rec.get('timeline', '')
                    priority = rec.get('priority', '')
                    
                    lines.append(f"{i}. {action}")
                    if impact:
                        lines.extend(self._wrap_text(f"Expected Impact: {impact}", self.indent_size))
                    if effort:
                        lines.append(f"   Implementation Effort: {effort.title()}")
                    if timeline:
                        lines.append(f"   Timeline: {timeline}")
                    if priority:
                        lines.append(f"   Priority: {priority.title()}")
                    lines.append("")
                else:
                    lines.extend(self._wrap_text(f"{i}. {rec}"))
                    lines.append("")
        
        return lines
    
    def _format_generic_text(self, data: Any) -> List[str]:
        """Format generic data as plain text"""
        lines = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (list, dict)):
                    lines.append(f"{formatted_key}:")
                    lines.append(json.dumps(value, indent=2))
                else:
                    lines.append(f"{formatted_key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        formatted_key = key.replace('_', ' ').title()
                        lines.append(f"  {formatted_key}: {value}")
                else:
                    lines.append(f"  - {item}")
        else:
            lines.extend(self._wrap_text(str(data)))
        
        return lines
    
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return dt_string


class HTMLFormatter(BaseFormatter):
    """Format output as HTML"""
    
    def __init__(self, include_css: bool = True, responsive: bool = True):
        """Initialize HTML formatter
        
        Args:
            include_css: Whether to include embedded CSS
            responsive: Whether to include responsive design CSS
        """
        self.include_css = include_css
        self.responsive = responsive
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as HTML string"""
        try:
            html_parts = []
            
            # HTML header
            html_parts.append("<!DOCTYPE html>")
            html_parts.append("<html lang='en'>")
            html_parts.append("<head>")
            html_parts.append("<meta charset='UTF-8'>")
            if self.responsive:
                html_parts.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
            
            report_type = data.get('report_type', 'Analysis Report').replace('_', ' ').title()
            html_parts.append(f"<title>{report_type}</title>")
            
            # CSS
            if self.include_css:
                html_parts.append("<style>")
                html_parts.append(self._get_css())
                html_parts.append("</style>")
            
            html_parts.append("</head>")
            html_parts.append("<body>")
            
            # Content
            html_parts.append("<div class='container'>")
            
            # Header
            html_parts.append(f"<header><h1>{report_type}</h1>")
            
            generated_at = data.get('generated_at', datetime.now().isoformat())
            html_parts.append(f"<p class='metadata'>Generated: {self._format_datetime(generated_at)}</p>")
            
            if 'analysis_type' in data:
                analysis_type = data['analysis_type'].replace('_', ' ').title()
                html_parts.append(f"<p class='metadata'>Analysis Type: {analysis_type}</p>")
            
            html_parts.append("</header>")
            
            # Executive Summary
            if 'executive_summary' in data:
                html_parts.append("<section class='executive-summary'>")
                html_parts.append("<h2>Executive Summary</h2>")
                html_parts.append(f"<p>{data['executive_summary']}</p>")
                html_parts.append("</section>")
            
            # Key Performance Indicators
            if 'key_performance_indicators' in data:
                html_parts.extend(self._format_kpis_html(data['key_performance_indicators']))
            
            # Key Findings
            if 'key_findings' in data:
                html_parts.extend(self._format_findings_html(data['key_findings']))
            
            # Recommendations
            if 'recommendations' in data:
                html_parts.extend(self._format_recommendations_html(data['recommendations']))
            elif 'strategic_recommendations' in data:
                html_parts.extend(self._format_recommendations_html(data['strategic_recommendations']))
            
            # Additional sections
            additional_sections = [
                ('critical_issues', 'Critical Issues'),
                ('trends_overview', 'Trends Overview'),
                ('risk_assessment', 'Risk Assessment')
            ]
            
            for key, title in additional_sections:
                if key in data and data[key]:
                    html_parts.append(f"<section class='{key.replace('_', '-')}'>")
                    html_parts.append(f"<h2>{title}</h2>")
                    html_parts.extend(self._format_generic_html(data[key]))
                    html_parts.append("</section>")
            
            html_parts.append("</div>")  # Close container
            html_parts.append("</body>")
            html_parts.append("</html>")
            
            return "\n".join(html_parts)
            
        except Exception as e:
            logger.error(f"Error formatting HTML: {e}")
            return f"<html><body><h1>Error</h1><p>HTML formatting failed: {str(e)}</p></body></html>"
    
    def get_content_type(self) -> str:
        """Get HTML content type"""
        return "text/html"
    
    def _get_css(self) -> str:
        """Get embedded CSS styles"""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        header h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .metadata {
            color: #7f8c8d;
            font-size: 0.9em;
            margin: 5px 0;
        }
        section {
            margin: 30px 0;
        }
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .kpi-card {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .kpi-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #2980b9;
        }
        .kpi-label {
            font-size: 0.9em;
            color: #7f8c8d;
        }
        .finding {
            background: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 10px 0;
        }
        .recommendation {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .priority-urgent { border-left: 4px solid #e74c3c; }
        .priority-high { border-left: 4px solid #f39c12; }
        .priority-medium { border-left: 4px solid #f1c40f; }
        .priority-low { border-left: 4px solid #27ae60; }
        .rec-meta {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 10px;
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .container { padding: 15px; }
            .kpi-grid { grid-template-columns: 1fr; }
        }
        """
    
    def _format_kpis_html(self, kpis: Dict[str, Any]) -> List[str]:
        """Format KPIs as HTML"""
        html = ["<section class='kpis'>", "<h2>Key Performance Indicators</h2>", "<div class='kpi-grid'>"]
        
        if isinstance(kpis, dict):
            for key, value in kpis.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (int, float)):
                    if 'rate' in key or 'percentage' in key:
                        formatted_value = f"{value:.1f}%"
                    elif 'amount' in key or 'value' in key or 'cost' in key:
                        formatted_value = f"₹{value:,.2f}"
                    else:
                        formatted_value = f"{value:,.0f}"
                else:
                    formatted_value = str(value)
                
                html.append(f"<div class='kpi-card'>")
                html.append(f"<div class='kpi-value'>{formatted_value}</div>")
                html.append(f"<div class='kpi-label'>{formatted_key}</div>")
                html.append("</div>")
        
        html.extend(["</div>", "</section>"])
        return html
    
    def _format_findings_html(self, findings: List[Any]) -> List[str]:
        """Format findings as HTML"""
        html = ["<section class='findings'>", "<h2>Key Findings</h2>"]
        
        if isinstance(findings, list):
            for i, finding in enumerate(findings, 1):
                html.append("<div class='finding'>")
                if isinstance(finding, dict):
                    finding_text = finding.get('finding', str(finding))
                    impact = finding.get('impact', '')
                    affected = finding.get('affected_items', finding.get('affected_orders', 0))
                    
                    html.append(f"<h3>{i}. {finding_text}</h3>")
                    if impact:
                        html.append(f"<p><strong>Impact:</strong> {impact}</p>")
                    if affected:
                        html.append(f"<p><strong>Affected Items:</strong> {affected:,}</p>")
                else:
                    html.append(f"<p>{i}. {finding}</p>")
                html.append("</div>")
        
        html.append("</section>")
        return html
    
    def _format_recommendations_html(self, recommendations: List[Any]) -> List[str]:
        """Format recommendations as HTML"""
        html = ["<section class='recommendations'>", "<h2>Recommendations</h2>"]
        
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                if isinstance(rec, dict):
                    action = rec.get('action', str(rec))
                    impact = rec.get('expected_impact', '')
                    effort = rec.get('implementation_effort', '')
                    timeline = rec.get('timeline', '')
                    priority = rec.get('priority', 'medium')
                    
                    priority_class = f"priority-{priority.lower()}"
                    html.append(f"<div class='recommendation {priority_class}'>")
                    html.append(f"<h3>{i}. {action}</h3>")
                    
                    if impact:
                        html.append(f"<p><strong>Expected Impact:</strong> {impact}</p>")
                    
                    meta_info = []
                    if effort:
                        meta_info.append(f"Effort: {effort.title()}")
                    if timeline:
                        meta_info.append(f"Timeline: {timeline}")
                    if priority:
                        priority_emoji = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(priority.lower(), '')
                        meta_info.append(f"Priority: {priority_emoji} {priority.title()}")
                    
                    if meta_info:
                        html.append(f"<div class='rec-meta'>{' | '.join(meta_info)}</div>")
                    
                    html.append("</div>")
                else:
                    html.append(f"<div class='recommendation'><p>{i}. {rec}</p></div>")
        
        html.append("</section>")
        return html
    
    def _format_generic_html(self, data: Any) -> List[str]:
        """Format generic data as HTML"""
        html = []
        
        if isinstance(data, dict):
            html.append("<ul>")
            for key, value in data.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (list, dict)):
                    html.append(f"<li><strong>{formatted_key}:</strong><pre>{json.dumps(value, indent=2)}</pre></li>")
                else:
                    html.append(f"<li><strong>{formatted_key}:</strong> {value}</li>")
            html.append("</ul>")
        elif isinstance(data, list):
            html.append("<ul>")
            for item in data:
                if isinstance(item, dict):
                    html.append("<li>")
                    for key, value in item.items():
                        formatted_key = key.replace('_', ' ').title()
                        html.append(f"<strong>{formatted_key}:</strong> {value}<br>")
                    html.append("</li>")
                else:
                    html.append(f"<li>{item}</li>")
            html.append("</ul>")
        else:
            html.append(f"<p>{data}</p>")
        
        return html
    
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return dt_string


class OutputFormatters:
    """Main class for managing multiple output formatters"""
    
    def __init__(self):
        """Initialize output formatters"""
        self.formatters = {
            'json': JSONFormatter(),
            'markdown': MarkdownFormatter(),
            'text': PlainTextFormatter(),
            'html': HTMLFormatter()
        }
    
    def format(self, data: Dict[str, Any], format_type: str = 'json') -> str:
        """Format data using specified formatter
        
        Args:
            data: Data to format
            format_type: Type of formatter to use
            
        Returns:
            Formatted string
        """
        formatter = self.formatters.get(format_type.lower())
        if not formatter:
            available_formats = ', '.join(self.formatters.keys())
            raise ValueError(f"Unknown format type '{format_type}'. Available formats: {available_formats}")
        
        return formatter.format(data)
    
    def get_content_type(self, format_type: str) -> str:
        """Get content type for specified format
        
        Args:
            format_type: Type of formatter
            
        Returns:
            Content type string
        """
        formatter = self.formatters.get(format_type.lower())
        if not formatter:
            return "text/plain"
        
        return formatter.get_content_type()
    
    def get_available_formats(self) -> List[str]:
        """Get list of available format types
        
        Returns:
            List of available format type names
        """
        return list(self.formatters.keys())
    
    def add_formatter(self, name: str, formatter: BaseFormatter):
        """Add a custom formatter
        
        Args:
            name: Name for the formatter
            formatter: Formatter instance
        """
        self.formatters[name.lower()] = formatter
    
    def remove_formatter(self, name: str):
        """Remove a formatter
        
        Args:
            name: Name of formatter to remove
        """
        if name.lower() in self.formatters:
            del self.formatters[name.lower()]
