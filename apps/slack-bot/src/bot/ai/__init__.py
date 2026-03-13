"""
AI module for Revolver AI Bot.
Provides intelligent analysis, synthesis, and content generation using OpenAI.
"""

# Lazy imports pour éviter les timeouts lors des tests

def get_ai_analysis_result_class():
    """Get AI analysis result class with lazy loading."""
    from .openai_client import AIAnalysisResult
    return AIAnalysisResult

__all__ = ['get_ai_client', 'get_openai_client_class', 'get_ai_analysis_result_class']
