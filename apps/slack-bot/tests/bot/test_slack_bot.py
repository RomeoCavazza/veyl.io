"""
Tests pour les fonctionnalités Slack consolidées
Après refactorisation: slack_handler.py + slack_bot_class.py
"""

import pytest
from unittest.mock import Mock, patch

def test_slack_handler_import():
    """Test que slack_handler s'importe correctement"""
    from src.bot import slack_handler
    assert hasattr(slack_handler, 'handle_veille_command')
    assert hasattr(slack_handler, 'handle_analyse_command')
    assert hasattr(slack_handler, 'handle_slack_event')

def test_slack_bot_class_import():
    """Test que slack_bot_class s'importe correctement"""
    try:
        from src.bot.slack_bot_class import SlackBot
        assert True
    except ImportError:
        # slack_bolt peut ne pas être installé
        pytest.skip("slack_bolt not available")

def test_slack_stub_compatibility():
    """Test que le stub slack_bot fonctionne"""
    from src.bot import slack_bot
    assert hasattr(slack_bot, 'handle_veille_command')
    assert hasattr(slack_bot, 'start_slack_listener')
    assert hasattr(slack_bot, 'main')