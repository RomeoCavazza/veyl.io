"""
Orchestrateur Email Principal
Coordonne tous les modules email
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .email_config import EmailConfig, get_default_email_config
from .email_templates import EmailTemplate, get_email_template_manager
from .email_sender import EmailSender, get_email_sender
from .newsletter_manager import NewsletterManager, get_newsletter_manager

logger = logging.getLogger(__name__)

class EmailOrchestrator:
    """Orchestrateur principal pour les fonctionnalités email"""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or get_default_email_config()
        self.template_manager = get_email_template_manager()
        self.sender = get_email_sender(self.config)
        self.newsletter_manager = get_newsletter_manager(self.config, self.template_manager)

    def send_newsletter(self,
                       title: str,
                       content: Dict[str, Any],
                       recipients: List[str]) -> Dict[str, Any]:
        """
        Envoie une newsletter complète

        Args:
            title: Titre de la newsletter
            content: Contenu de la newsletter
            recipients: Liste des destinataires

        Returns:
            Résultat de l'envoi
        """
        logger.info(f"🎯 Sending newsletter: {title}")

        try:
            # Créer la newsletter
            newsletter = self.newsletter_manager.create_newsletter(
                title=title,
                content=content,
                recipients=recipients
            )

            # L'envoyer immédiatement
            result = self.newsletter_manager.send_newsletter(newsletter['id'])

            logger.info("✅ Newsletter sent successfully" if result['success'] else "❌ Newsletter send failed")

            return result

        except Exception as e:
            logger.error(f"Newsletter orchestration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'title': title
            }

    def send_report(self,
                   title: str,
                   report_data: Dict[str, Any],
                   recipients: List[str],
                   attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Envoie un rapport

        Args:
            title: Titre du rapport
            report_data: Données du rapport
            recipients: Liste des destinataires
            attachments: Pièces jointes (optionnel)

        Returns:
            Résultat de l'envoi
        """
        logger.info(f"📊 Sending report: {title}")

        try:
            # Rendre le template
            html_content = self.template_manager.render_report({
                'title': title,
                'sections': report_data.get('sections', []),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            # Envoyer
            result = self.sender.send_email(
                to=recipients,
                subject=f"Report: {title}",
                body=self._extract_report_text(report_data),
                html_body=html_content,
                attachments=attachments
            )

            logger.info("✅ Report sent successfully" if result['success'] else "❌ Report send failed")

            return result

        except Exception as e:
            logger.error(f"Report send failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'title': title
            }

    def send_alert(self,
                  title: str,
                  message: str,
                  recipients: List[str],
                  alert_type: str = "info") -> Dict[str, Any]:
        """
        Envoie une alerte

        Args:
            title: Titre de l'alerte
            message: Message d'alerte
            recipients: Liste des destinataires
            alert_type: Type d'alerte (info, warning, error)

        Returns:
            Résultat de l'envoi
        """
        logger.info(f"🚨 Sending alert: {title}")

        try:
            # Rendre le template
            html_content = self.template_manager.render_alert({
                'title': title,
                'message': message,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'alert_type': alert_type
            })

            # Envoyer
            result = self.sender.send_email(
                to=recipients,
                subject=f"ALERT: {title}",
                body=message,
                html_body=html_content
            )

            logger.info("✅ Alert sent successfully" if result['success'] else "❌ Alert send failed")

            return result

        except Exception as e:
            logger.error(f"Alert send failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'title': title
            }

    def _extract_report_text(self, report_data: Dict[str, Any]) -> str:
        """Extrait le contenu texte d'un rapport"""
        text_parts = []

        for section in report_data.get('sections', []):
            text_parts.append(f"{section.get('title', '')}")
            text_parts.append(f"{section.get('content', '')}")

        return '\n\n'.join(text_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques générales"""
        return {
            'config_valid': self.config.test_connection(),
            'newsletters_count': len(self.newsletter_manager.list_newsletters()),
            'templates_count': len(self.template_manager.list_templates()),
            'timestamp': datetime.now().isoformat()
        }

# Fonctions de compatibilité pour l'ancien code
def send_newsletter(title: str, content: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
    """Fonction de compatibilité"""
    orchestrator = EmailOrchestrator()
    return orchestrator.send_newsletter(title, content, recipients)

def send_report(title: str, report_data: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
    """Fonction de compatibilité"""
    orchestrator = EmailOrchestrator()
    return orchestrator.send_report(title, report_data, recipients)

def send_alert(title: str, message: str, recipients: List[str]) -> Dict[str, Any]:
    """Fonction de compatibilité"""
    orchestrator = EmailOrchestrator()
    return orchestrator.send_alert(title, message, recipients)
