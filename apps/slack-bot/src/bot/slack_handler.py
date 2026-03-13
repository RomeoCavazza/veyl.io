"""
Slack event handling functionality.
"""
from typing import Dict, Any
import os
from .orchestrator import process_brief, run_analyse, run_veille
from src.utils.logger_v2 import logger

def handle_veille_command() -> str:
    """Handle veille command from Slack."""
    try:
        output_path = os.getenv("VEILLE_OUTPUT_PATH", "veille_output.csv")
        result = run_veille(topics=["tech", "ai", "innovation"], output_path=output_path)
        
        if result.get("status") == "success":
            # Extract items from results
            items = []
            for topic_result in result.get("results", []):
                for article in topic_result.get("articles", []):
                    items.append({
                        "id": len(items),
                        "title": article.get("title", ""),
                        "url": article.get("url", "")
                    })
            
            return f"✅ Veille terminée. {len(items)} items sauvegardés dans {output_path}"
        else:
            return f"❌ Erreur lors de la veille: {result.get('error', 'Unknown error')}"
        
    except Exception as e:
        logger.error(f"Error in veille command: {e}")
        return f"❌ Erreur lors de la veille: {e}"

def handle_analyse_command() -> str:
    """Handle analyse command from Slack."""
    try:
        run_analyse("data.csv")
        return "✅ Analyse terminée."
        
    except Exception as e:
        logger.error(f"Error in analyse command: {e}")
        return f"❌ Erreur lors de l'analyse: {e}"

def simulate_upload() -> None:
    """Simulate file upload for testing."""
    print("Simulating file upload...")
    print("'titre': 'STATIC'")
    print("'content': 'Test content'")

async def handle_slack_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a Slack event.
    
    Args:
        event_data: Event data from Slack
        
    Returns:
        Response data
    """
    try:
        text = event_data.get('text', '').lower()
        event_data.get('user')
        
        # Process commands
        if text.startswith('!brief'):
            # Extract brief path
            parts = text.split()
            if len(parts) < 2:
                return {
                    "type": "error",
                    "message": "Please provide a brief path"
                }
                
            brief_path = parts[1]
            result = process_brief(brief_path)
            
            return {
                "type": "brief_processed",
                "result": result
            }
            
        elif text.startswith('!analyse'):
            # Extract data path
            parts = text.split()
            if len(parts) < 2:
                return {
                    "type": "error",
                    "message": "Please provide a data path"
                }
                
            data_path = parts[1]
            result = run_analyse(data_path)
            
            return {
                "type": "analysis_complete",
                "result": result
            }
            
        elif text.startswith('!veille'):
            # Extract topics
            parts = text.split()
            if len(parts) < 2:
                return {
                    "type": "error",
                    "message": "Please provide topics for technology watch"
                }
                
            topics = parts[1:]
            result = run_veille(topics)
            
            return {
                "type": "veille_complete",
                "result": result
            }
            
        else:
            return {
                "type": "message",
                "message": "I don't understand that command"
            }
            
    except Exception as e:
        logger.error(f"Error handling Slack event: {e}")
        return {
            "type": "error",
            "error": str(e)
        }

async def handle_message_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a message event."""
    try:
        text = event_data.get('text', '').lower()
        event_data.get('user')
        
        # Process commands
        if text.startswith('!brief'):
            # Extract brief path
            parts = text.split()
            if len(parts) < 2:
                return {
                    "type": "error",
                    "message": "Please provide a brief path"
                }
                
            brief_path = parts[1]
            result = process_brief(brief_path)
            
            return {
                "type": "brief_processed",
                "result": result
            }
            
        elif text.startswith('!analyse'):
            # Extract data path
            parts = text.split()
            if len(parts) < 2:
                return {
                    "type": "error",
                    "message": "Please provide a data path"
                }
                
            data_path = parts[1]
            result = run_analyse(data_path)
            
            return {
                "type": "analysis_complete",
                "result": result
            }
            
        elif text.startswith('!veille'):
            # Extract topics
            parts = text.split()
            if len(parts) < 2:
                return {
                    "type": "error",
                    "message": "Please provide topics for technology watch"
                }
                
            topics = parts[1:]
            result = run_veille(topics)
            
            return {
                "type": "veille_complete",
                "result": result
            }
            
        else:
            return {
                "type": "message",
                "message": "I don't understand that command"
            }
            
    except Exception as e:
        logger.error(f"Error handling message event: {e}")
        return {
            "type": "error",
            "error": str(e)
        }

async def handle_mention_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle an app mention event."""
    try:
        event_data.get('text', '').lower()
        event_data.get('user')
        
        # Process mention
        return {
            "type": "message",
            "message": "Hi! I'm here to help. Use !brief, !analyse, or !veille commands."
        }
        
    except Exception as e:
        logger.error(f"Error handling mention event: {e}")
        return {
            "type": "error",
            "error": str(e)
        }

__all__ = ['handle_slack_event', 'handle_veille_command', 'handle_analyse_command', 'simulate_upload']
