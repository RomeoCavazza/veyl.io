"""
Services unifiés pour Revolver AI Bot
Consolide tous les patterns répétitifs identifiés dans l'audit
"""

from .analysis_service import (
    AnalysisService,
    get_analysis_service,
    AnalysisResult,
    analyze_sentiment,
    analyze_trends,
    analyze_content,
    generate_insights
)

from .ai_service import (
    AIService,
    get_ai_service,
    AIRequest,
    AIResponse,
    AnalysisType
)

from .slack_handler_service import (
    SlackHandlerService,
    get_slack_handler_service,
    SlackCommandRequest,
    SlackCommandResponse,
    SlackCommand,
    handle_veille_command,
    handle_analyse_command,
    handle_slack_event
)

__all__ = [
    # Service d'analyse
    'AnalysisService',
    'get_analysis_service',
    'AnalysisResult',
    'analyze_sentiment',
    'analyze_trends',
    'analyze_content',
    'generate_insights',

    # Service IA
    'AIService',
    'get_ai_service',
    'AIRequest',
    'AIResponse',
    'AnalysisType',

    # Service Slack
    'SlackHandlerService',
    'get_slack_handler_service',
    'SlackCommandRequest',
    'SlackCommandResponse',
    'SlackCommand',
    'handle_veille_command',
    'handle_analyse_command',
    'handle_slack_event'
]