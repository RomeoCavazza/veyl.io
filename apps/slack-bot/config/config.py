from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    slack_app_token: str = Field(..., alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., alias="SLACK_SIGNING_SECRET")
    gmail_user: str = Field(..., alias="GMAIL_USER")
    gmail_app_password: str = Field(..., alias="GMAIL_APP_PASSWORD")
    serpapi_api_key: str = Field(..., alias="SERPAPI_API_KEY")
    google_sheet_id: str = Field(..., alias="GOOGLE_SHEET_ID")
    env: str = Field(default="development", alias="ENV")

    # Configuration Apify pour scraping professionnel
    APIFY_TOKEN = os.getenv('APIFY_TOKEN', '')

    # Configuration Google Vertex AI
    VERTEX_PROJECT_ID = os.getenv('VERTEX_PROJECT_ID', '')
    VERTEX_API_KEY = os.getenv('VERTEX_API_KEY', '')

    # Configuration OSINT
    SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', '')
    CENSYS_API_ID = os.getenv('CENSYS_API_ID', '')
    CENSYS_API_SECRET = os.getenv('CENSYS_API_SECRET', '')
    SECURITYTRAILS_API_KEY = os.getenv('SECURITYTRAILS_API_KEY', '')

    # Configuration proxy/Tor
    TOR_PROXY = os.getenv('TOR_PROXY', '')  # "socks5://127.0.0.1:9050"

    # Configuration scraping avancé
    ENABLE_SELENIUM_FALLBACK = os.getenv('ENABLE_SELENIUM_FALLBACK', 'true').lower() == 'true'
    DOWNLOAD_MEDIA = os.getenv('DOWNLOAD_MEDIA', 'true').lower() == 'true'
    MEDIA_DIR = os.getenv('MEDIA_DIR', 'downloads/media')

    model_config = SettingsConfigDict(env_file="secrets/.env", populate_by_name=True)
