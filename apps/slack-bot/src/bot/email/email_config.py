"""
Configuration Email
Module spécialisé pour la configuration SMTP
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailConfig:
    """Configuration Email spécialisée"""

    def __init__(self,
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 username: str = None,
                 password: str = None,
                 use_tls: bool = True,
                 use_ssl: bool = False):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username or os.getenv("EMAIL_USERNAME")
        self.password = password or os.getenv("EMAIL_PASSWORD")
        self.use_tls = use_tls
        self.use_ssl = use_ssl

        self._validate_config()

    def _validate_config(self):
        """Valide la configuration"""
        if not self.username or not self.password:
            raise ValueError(
                "Email credentials not configured. "
                "Set EMAIL_USERNAME and EMAIL_PASSWORD environment variables."
            )

        if self.use_ssl and self.use_tls:
            raise ValueError("Cannot use both SSL and TLS simultaneously")

        if self.use_ssl:
            self.smtp_port = 465
        elif self.use_tls:
            self.smtp_port = 587
        else:
            self.smtp_port = 25

    def get_connection_params(self) -> dict:
        """Retourne les paramètres de connexion"""
        return {
            'server': self.smtp_server,
            'port': self.smtp_port,
            'username': self.username,
            'password': self.password,
            'use_tls': self.use_tls,
            'use_ssl': self.use_ssl
        }

    def test_connection(self) -> bool:
        """Teste la connexion SMTP"""
        try:
            import smtplib
            import ssl

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            server.login(self.username, self.password)
            server.quit()

            logger.info("✅ Email configuration test successful")
            return True

        except Exception as e:
            logger.error(f"❌ Email configuration test failed: {e}")
            return False

    @classmethod
    def from_env(cls) -> 'EmailConfig':
        """Crée une configuration depuis les variables d'environnement"""
        return cls(
            smtp_server=os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587")),
            username=os.getenv("EMAIL_USERNAME"),
            password=os.getenv("EMAIL_PASSWORD"),
            use_tls=os.getenv("EMAIL_USE_TLS", "true").lower() == "true",
            use_ssl=os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
        )

# Fonctions utilitaires
def get_default_email_config() -> EmailConfig:
    """Retourne la configuration email par défaut"""
    return EmailConfig.from_env()

def validate_email_config(config: EmailConfig) -> bool:
    """Valide une configuration email"""
    return config.test_connection()
