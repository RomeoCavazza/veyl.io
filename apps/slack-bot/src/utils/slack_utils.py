from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .logger_v2 import logger

def get_slack_client():
    """Retourne une instance du client Slack."""
    token = "xoxb-your-token"  # À remplacer par le vrai token
    return WebClient(token=token)

def send_message(channel_id: str, text: str, thread_ts: str = None) -> bool:
    """Envoie un message sur Slack."""
    try:
        client = get_slack_client()
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
        return response["ok"]
    except SlackApiError as e:
        logger.error(f"Erreur envoi message Slack: {e.response['error']}")
        return False

# Stub functions for tests
def handle_message(channel: str, message: str) -> dict:
    """Handle incoming message."""
    return {"status": "success", "channel": channel, "message": message}

def handle_command(channel: str, command: str, user: str) -> dict:
    """Handle incoming command."""
    return {"status": "success", "channel": channel, "command": command, "user": user}

def process_brief_command(channel: str, file_path: str) -> dict:
    """Process brief command."""
    return {"status": "success", "channel": channel, "file": file_path}

def generate_slides_command(channel: str, brief_data: str) -> dict:
    """Generate slides command."""
    return {"status": "success", "channel": channel, "brief": brief_data}

def run_veille_command(channel: str, sources: list) -> dict:
    """Run veille command."""
    return {"status": "success", "channel": channel, "sources": sources}
