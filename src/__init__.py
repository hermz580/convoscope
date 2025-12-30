"""
ConvoScope - Privacy-first conversation analytics for Claude AI

A comprehensive toolkit for analyzing Claude AI conversations with deep insights
into quality, patterns, and evolution - all while keeping your data private and
processed locally.

Copyright (c) 2024 Herman Harp
Licensed under MIT License
"""

__version__ = "2.0.0"
__author__ = "Herman Harp"
__license__ = "MIT"

from .advanced_analyzer import AdvancedConversationAnalyzer
from .quality_analyzer import ConversationQualityAnalyzer
from .temporal_analyzer import TemporalEvolutionAnalyzer
from .visualization_generator import VisualizationGenerator

__all__ = [
    "AdvancedConversationAnalyzer",
    "ConversationQualityAnalyzer",
    "TemporalEvolutionAnalyzer",
    "VisualizationGenerator",
]
