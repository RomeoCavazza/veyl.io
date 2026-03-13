from .openai_client import get_ai_client

class BriefSummarizationError(Exception):
    pass

def summarize_brief(text: str) -> dict:
    """Envoie le texte à OpenAI pour obtenir un résumé structuré. Lève une exception si erreur."""
    if not text or not text.strip():
        raise BriefSummarizationError("Le texte à résumer est vide.")
    client = get_ai_client(mock=False)
    result = client.analyze_brief(text)
    if not result.success:
        raise BriefSummarizationError(f"Erreur OpenAI: {result.error_message}")
    return result.to_dict()
