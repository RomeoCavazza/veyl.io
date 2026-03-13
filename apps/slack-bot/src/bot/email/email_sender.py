"""
Envoi d'emails
Module spécialisé pour l'envoi SMTP
"""

# Standard library imports
import logging
import smtplib
import ssl
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

from .email_config import EmailConfig

logger = logging.getLogger(__name__)

class EmailSender:
    """Service d'envoi d'emails spécialisé"""

    def __init__(self, config: EmailConfig):
        self.config = config
        self.server = None
        self._connect()

    def _connect(self):
        """Établit la connexion SMTP"""
        try:
            if self.config.use_ssl:
                self.server = smtplib.SMTP_SSL(
                    self.config.smtp_server,
                    self.config.smtp_port
                )
            else:
                self.server = smtplib.SMTP(
                    self.config.smtp_server,
                    self.config.smtp_port
                )
                if self.config.use_tls:
                    self.server.starttls()

            self.server.login(self.config.username, self.config.password)
            logger.info("✅ Email server connection established")

        except Exception as e:
            logger.error(f"❌ Failed to connect to email server: {e}")
            raise

    def send_email(self,
                   to: List[str],
                   subject: str,
                   body: str,
                   from_name: str = "Revolver AI Bot",
                   attachments: Optional[List[str]] = None,
                   html_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Envoie un email - refactorisé pour réduire la complexité

        Args:
            to: Liste des destinataires
            subject: Sujet de l'email
            body: Corps de l'email (texte)
            from_name: Nom de l'expéditeur
            attachments: Liste des chemins de fichiers à attacher
            html_body: Corps HTML alternatif

        Returns:
            Résultat de l'envoi
        """
        try:
            # Étape 1: Initialisation du résultat
            result = _initialize_email_result(to)

            # Étape 2: Création du message email
            msg = _create_email_message(self, to, subject, from_name)

            # Étape 3: Ajout du corps de l'email
            _add_email_body(msg, body, html_body)

            # Étape 4: Ajout des pièces jointes
            _add_email_attachments(self, msg, attachments)

            # Étape 5: Envoi du message
            return _send_email_message(self, msg, to, result)

        except Exception as e:
            return _handle_email_error(e, result)

def _initialize_email_result(to: List[str]) -> Dict[str, Any]:
    """Initialise le dictionnaire de résultat d'envoi d'email"""
    return {
        'success': False,
        'recipients': to,
        'timestamp': datetime.now().isoformat(),
        'message_id': None
    }

def _create_email_message(sender, to: List[str], subject: str, from_name: str):
    """Crée le message email avec les en-têtes"""
    msg = MIMEMultipart()
    msg['From'] = f"{from_name} <{sender.config.username}>"
    msg['To'] = ', '.join(to)
    msg['Subject'] = subject
    return msg

def _add_email_body(msg, body: str, html_body: Optional[str]):
    """Ajoute le corps de l'email (texte et/ou HTML)"""
    if html_body:
        msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

def _add_email_attachments(sender, msg, attachments: Optional[List[str]]):
    """Ajoute les pièces jointes au message"""
    if attachments:
        for attachment_path in attachments:
            sender._add_attachment(msg, attachment_path)

def _send_email_message(sender, msg, to: List[str], result: Dict[str, Any]) -> Dict[str, Any]:
    """Envoie le message email"""
    sender.server.sendmail(sender.config.username, to, msg.as_string())
    result['success'] = True
    logger.info(f"✅ Email sent successfully to {len(to)} recipients")
    return result

def _handle_email_error(error: Exception, result: Dict[str, Any]) -> Dict[str, Any]:
    """Gère les erreurs d'envoi d'email"""
    logger.error(f"❌ Failed to send email: {error}")
    result['error'] = str(error)
    return result

    def send_bulk_email(self,
                       recipients: List[Dict[str, Any]],
                       subject: str,
                       body: str,
                       from_name: str = "Revolver AI Bot",
                       batch_size: int = 50) -> Dict[str, Any]:
        """
        Envoie des emails en masse

        Args:
            recipients: Liste de dictionnaires avec 'email' et optionnellement 'name'
            subject: Sujet de l'email
            body: Corps de l'email
            from_name: Nom de l'expéditeur
            batch_size: Taille des lots

        Returns:
            Résultats de l'envoi en masse
        """
        results = {
            'total_recipients': len(recipients),
            'successful_sends': 0,
            'failed_sends': 0,
            'start_time': datetime.now().isoformat(),
            'batches': []
        }

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            batch_result = self._send_batch(batch, subject, body, from_name)
            results['batches'].append(batch_result)

            results['successful_sends'] += batch_result['successful']
            results['failed_sends'] += batch_result['failed']

        results['end_time'] = datetime.now().isoformat()
        results['success_rate'] = (results['successful_sends'] / results['total_recipients']) * 100

        logger.info(f"✅ Bulk email completed: {results['successful_sends']}/{results['total_recipients']} sent")

        return results

    def _send_batch(self, batch: List[Dict], subject: str, body: str, from_name: str) -> Dict[str, Any]:
        """Envoie un lot d'emails"""
        successful = 0
        failed = 0

        for recipient in batch:
            try:
                email = recipient['email']
                personalized_body = self._personalize_body(body, recipient)

                result = self.send_email(
                    to=[email],
                    subject=subject,
                    body=personalized_body,
                    from_name=from_name
                )

                if result['success']:
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"Failed to send to {recipient.get('email', 'unknown')}: {e}")
                failed += 1

        return {
            'batch_size': len(batch),
            'successful': successful,
            'failed': failed,
            'timestamp': datetime.now().isoformat()
        }

    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Ajoute une pièce jointe"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Attachment not found: {file_path}")

            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{path.name}"')
                msg.attach(part)

        except Exception as e:
            logger.error(f"Failed to add attachment {file_path}: {e}")
            raise

    def _personalize_body(self, body: str, recipient: Dict[str, Any]) -> str:
        """Personnalise le corps de l'email"""
        personalized = body

        # Remplacer les variables de personnalisation
        if 'name' in recipient:
            personalized = personalized.replace('{{name}}', recipient['name'])
            personalized = personalized.replace('{{NAME}}', recipient['name'])

        if 'email' in recipient:
            personalized = personalized.replace('{{email}}', recipient['email'])

        return personalized

    def disconnect(self):
        """Ferme la connexion SMTP"""
        if self.server:
            try:
                self.server.quit()
                logger.info("✅ Email server connection closed")
            except Exception as e:
                logger.error(f"Error closing email connection: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# Fonction de compatibilité
def get_email_sender(config: EmailConfig) -> EmailSender:
    """Retourne un sender d'emails"""
    return EmailSender(config)
