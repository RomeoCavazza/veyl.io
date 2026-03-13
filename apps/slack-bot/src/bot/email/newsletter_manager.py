"""
Gestionnaire de Newsletters
Module spécialisé pour la gestion des newsletters
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from .email_config import EmailConfig
from .email_templates import EmailTemplate
from .email_sender import EmailSender

logger = logging.getLogger(__name__)

class NewsletterManager:
    """Gestionnaire de newsletters spécialisé"""

    def __init__(self, config: EmailConfig, template_manager: Optional[EmailTemplate] = None):
        self.config = config
        self.template_manager = template_manager or EmailTemplate()
        self.sender = EmailSender(config)
        self.newsletters_dir = Path("data/newsletters")
        self.newsletters_dir.mkdir(exist_ok=True)

    def create_newsletter(self,
                         title: str,
                         content: Dict[str, Any],
                         recipients: List[str],
                         schedule_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Crée une newsletter

        Args:
            title: Titre de la newsletter
            content: Contenu de la newsletter
            recipients: Liste des destinataires
            schedule_time: Date d'envoi programmé

        Returns:
            Informations de la newsletter créée
        """
        newsletter_id = f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        newsletter_data = {
            'id': newsletter_id,
            'title': title,
            'content': content,
            'recipients': recipients,
            'created_at': datetime.now().isoformat(),
            'schedule_time': schedule_time.isoformat() if schedule_time else None,
            'status': 'draft'
        }

        # Sauvegarder la newsletter
        self._save_newsletter(newsletter_data)

        logger.info(f"✅ Newsletter created: {newsletter_id}")

        return newsletter_data

    def send_newsletter(self, newsletter_id: str) -> Dict[str, Any]:
        """
        Envoie une newsletter

        Args:
            newsletter_id: ID de la newsletter

        Returns:
            Résultat de l'envoi
        """
        try:
            # Charger la newsletter
            newsletter_data = self._load_newsletter(newsletter_id)

            if newsletter_data['status'] != 'draft':
                raise ValueError(f"Newsletter {newsletter_id} is not in draft status")

            # Rendre le template
            html_content = self.template_manager.render_newsletter({
                'title': newsletter_data['title'],
                'content': self._format_newsletter_content(newsletter_data['content']),
                'date': datetime.now().strftime('%Y-%m-%d')
            })

            # Envoyer
            result = self.sender.send_email(
                to=newsletter_data['recipients'],
                subject=newsletter_data['title'],
                body=self._extract_text_content(newsletter_data['content']),
                html_body=html_content
            )

            # Mettre à jour le statut
            newsletter_data['status'] = 'sent' if result['success'] else 'failed'
            newsletter_data['sent_at'] = datetime.now().isoformat()
            newsletter_data['send_result'] = result

            self._save_newsletter(newsletter_data)

            logger.info(f"✅ Newsletter {newsletter_id} sent to {len(newsletter_data['recipients'])} recipients")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to send newsletter {newsletter_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'newsletter_id': newsletter_id
            }

    def schedule_newsletter(self, newsletter_id: str, schedule_time: datetime) -> bool:
        """
        Programme l'envoi d'une newsletter

        Args:
            newsletter_id: ID de la newsletter
            schedule_time: Date d'envoi

        Returns:
            Succès de la programmation
        """
        try:
            newsletter_data = self._load_newsletter(newsletter_id)
            newsletter_data['schedule_time'] = schedule_time.isoformat()
            newsletter_data['status'] = 'scheduled'

            self._save_newsletter(newsletter_data)

            logger.info(f"✅ Newsletter {newsletter_id} scheduled for {schedule_time}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to schedule newsletter {newsletter_id}: {e}")
            return False

    def get_newsletter_stats(self, newsletter_id: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une newsletter

        Args:
            newsletter_id: ID de la newsletter

        Returns:
            Statistiques de la newsletter
        """
        try:
            newsletter_data = self._load_newsletter(newsletter_id)

            stats = {
                'newsletter_id': newsletter_id,
                'title': newsletter_data['title'],
                'status': newsletter_data['status'],
                'recipients_count': len(newsletter_data['recipients']),
                'created_at': newsletter_data['created_at'],
                'sent_at': newsletter_data.get('sent_at'),
                'scheduled_time': newsletter_data.get('schedule_time')
            }

            # Statistiques d'envoi si disponibles
            if 'send_result' in newsletter_data:
                send_result = newsletter_data['send_result']
                stats.update({
                    'send_success': send_result.get('success', False),
                    'send_timestamp': send_result.get('timestamp'),
                    'recipients_reached': len(send_result.get('recipients', []))
                })

            return stats

        except Exception as e:
            logger.error(f"Failed to get newsletter stats: {e}")
            return {'error': str(e)}

    def list_newsletters(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Liste les newsletters

        Args:
            status_filter: Filtre par statut (optionnel)

        Returns:
            Liste des newsletters
        """
        try:
            newsletters = []

            for newsletter_file in self.newsletters_dir.glob("*.json"):
                newsletter_data = self._load_newsletter(newsletter_file.stem)

                if status_filter and newsletter_data.get('status') != status_filter:
                    continue

                newsletters.append({
                    'id': newsletter_data['id'],
                    'title': newsletter_data['title'],
                    'status': newsletter_data['status'],
                    'created_at': newsletter_data['created_at'],
                    'recipients_count': len(newsletter_data['recipients'])
                })

            # Trier par date de création (plus récent en premier)
            newsletters.sort(key=lambda x: x['created_at'], reverse=True)

            return newsletters

        except Exception as e:
            logger.error(f"Failed to list newsletters: {e}")
            return []

    def _save_newsletter(self, newsletter_data: Dict[str, Any]):
        """Sauvegarde une newsletter"""
        newsletter_file = self.newsletters_dir / f"{newsletter_data['id']}.json"

        with open(newsletter_file, 'w', encoding='utf-8') as f:
            json.dump(newsletter_data, f, indent=2, ensure_ascii=False, default=str)

    def _load_newsletter(self, newsletter_id: str) -> Dict[str, Any]:
        """Charge une newsletter"""
        newsletter_file = self.newsletters_dir / f"{newsletter_id}.json"

        if not newsletter_file.exists():
            raise FileNotFoundError(f"Newsletter {newsletter_id} not found")

        with open(newsletter_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _format_newsletter_content(self, content: Dict[str, Any]) -> str:
        """Formate le contenu de la newsletter en HTML"""
        html_parts = []

        # Optimisation : utilisation de list comprehensions
        if 'sections' in content:
            html_parts.extend([
                f"<h2>{section.get('title', '')}</h2>",
                f"<div>{section.get('content', '')}</div>"
                for section in content['sections']
            ])

        if 'articles' in content:
            html_parts.extend([
                f"<h3>{article.get('title', '')}</h3>",
                f"<p>{article.get('summary', '')}</p>"
                for article in content['articles']
            ])

        return '\n'.join(html_parts)

    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """Extrait le contenu texte de la newsletter"""
        text_parts = []

        if 'sections' in content:
            for section in content['sections']:
                text_parts.append(f"{section.get('title', '')}")
                text_parts.append(f"{section.get('content', '')}")

        return '\n\n'.join(text_parts)

# Fonction de compatibilité
def get_newsletter_manager(config: EmailConfig) -> NewsletterManager:
    """Retourne un gestionnaire de newsletters"""
    return NewsletterManager(config)
