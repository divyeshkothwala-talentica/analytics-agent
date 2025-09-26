"""
Insight Generation & Human-Readable Output Package

This package transforms raw MongoDB query results into human-readable insights
with actionable recommendations using OpenAI GPT for narrative generation.
"""

from .processor import ResultProcessor
from .templates import InsightTemplates
from .narrator import NarrativeGenerator
from .visualizer import VisualizationDataPrep
from .reporter import ReportGenerator
from .recommender import RecommendationEngine
from .formatters import OutputFormatters

__all__ = [
    'ResultProcessor',
    'InsightTemplates', 
    'NarrativeGenerator',
    'VisualizationDataPrep',
    'ReportGenerator',
    'RecommendationEngine',
    'OutputFormatters'
]
