"""
Module de monitoring pour le bot Revolver.AI
"""

# from .coverage import calculate_coverage, analyze_coverage_trends
from .core import MonitoringManager
from .alerts import AlertManager

__all__ = [
    'MonitoringManager',
    'AlertManager',
    # 'calculate_coverage',
    # 'analyze_coverage_trends'
]
