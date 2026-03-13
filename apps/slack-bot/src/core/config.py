"""
Configuration management for Revolver AI Bot
Centralized configuration for all modules
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "revolver_bot")
    username: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")

@dataclass
class APIConfig:
    """API configuration"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    workers: int = int(os.getenv("WORKERS", "1"))

@dataclass
class SlackConfig:
    """Slack configuration"""
    bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    app_token: str = os.getenv("SLACK_APP_TOKEN", "")
    signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    channel_id: str = os.getenv("SLACK_CHANNEL_ID", "")

@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
    temperature: float = 0.7

@dataclass
class VeilleConfig:
    """Veille configuration"""
    rss_feeds: list = None
    social_platforms: list = None
    competitors: list = None
    update_frequency: int = 3600  # seconds

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.slack = SlackConfig()
        self.openai = OpenAIConfig()
        self.veille = VeilleConfig()
        
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Database
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", self.database.port))
        self.database.database = os.getenv("DB_NAME", self.database.database)
        self.database.username = os.getenv("DB_USER", self.database.username)
        self.database.password = os.getenv("DB_PASS", self.database.password)
        
        # API
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", self.api.port))
        self.api.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        self.api.workers = int(os.getenv("API_WORKERS", self.api.workers))
        
        # Slack
        self.slack.bot_token = os.getenv("SLACK_BOT_TOKEN", self.slack.bot_token)
        self.slack.app_token = os.getenv("SLACK_APP_TOKEN", self.slack.app_token)
        self.slack.signing_secret = os.getenv("SLACK_SIGNING_SECRET", self.slack.signing_secret)
        self.slack.channel_id = os.getenv("SLACK_CHANNEL_ID", self.slack.channel_id)
        
        # OpenAI
        self.openai.api_key = os.getenv("OPENAI_API_KEY", self.openai.api_key)
        self.openai.model = os.getenv("OPENAI_MODEL", self.openai.model)
        self.openai.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", self.openai.max_tokens))
        self.openai.temperature = float(os.getenv("OPENAI_TEMPERATURE", self.openai.temperature))
        
        # Veille
        rss_feeds = os.getenv("VEILLE_RSS_FEEDS", "")
        if rss_feeds:
            self.veille.rss_feeds = rss_feeds.split(",")
        
        social_platforms = os.getenv("VEILLE_SOCIAL_PLATFORMS", "")
        if social_platforms:
            self.veille.social_platforms = social_platforms.split(",")
        
        competitors = os.getenv("VEILLE_COMPETITORS", "")
        if competitors:
            self.veille.competitors = competitors.split(",")
        
        self.veille.update_frequency = int(os.getenv("VEILLE_UPDATE_FREQ", self.veille.update_frequency))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "password": "***" if self.database.password else ""
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
                "workers": self.api.workers
            },
            "slack": {
                "bot_token": "***" if self.slack.bot_token else "",
                "app_token": "***" if self.slack.app_token else "",
                "signing_secret": "***" if self.slack.signing_secret else "",
                "channel_id": self.slack.channel_id
            },
            "openai": {
                "model": self.openai.model,
                "max_tokens": self.openai.max_tokens,
                "temperature": self.openai.temperature,
                "api_key": "***" if self.openai.api_key else ""
            },
            "veille": {
                "rss_feeds": self.veille.rss_feeds,
                "social_platforms": self.veille.social_platforms,
                "competitors": self.veille.competitors,
                "update_frequency": self.veille.update_frequency
            }
        }

# Global configuration instance
config = Config()
