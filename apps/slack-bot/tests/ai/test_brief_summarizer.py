import pytest
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.bot.ai.brief_summarizer import summarize_brief, BriefSummarizationError

@pytest.mark.unit


def test_summarize_brief_mock(monkeypatch):
    # Force le mode mock
    from src.bot.ai import openai_client
    monkeypatch.setattr(openai_client, "get_ai_client", lambda mock=False: openai_client.OpenAIClient(mock=True))
    text = "Brief test pour Revolver.bot. Objectif : valider la synthèse IA."
    result = summarize_brief(text)
    assert result["success"] is True
    assert "titre" in result["content"]
    assert "objectifs" in result["content"]
    assert isinstance(result["content"]["objectifs"], list)
    assert "kpis" in result["content"]
    assert isinstance(result["content"]["kpis"], list)
    assert "insights" in result["content"]
    assert "resume" in result["content"]

@pytest.mark.unit


def test_summarize_brief_empty():
    with pytest.raises(BriefSummarizationError):
        summarize_brief("") 