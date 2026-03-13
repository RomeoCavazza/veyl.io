from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    slack_app_token: str = Field(default="", alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(default="", alias="SLACK_SIGNING_SECRET")
    gmail_user: str = Field(default="", alias="GMAIL_USER")
    gmail_app_password: str = Field(default="", alias="GMAIL_APP_PASSWORD")
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")
    google_sheet_id: str = Field(default="", alias="GOOGLE_SHEET_ID")
    env: str = Field(default="development", alias="ENV")

    # Configuration Apify pour scraping professionnel
    APIFY_TOKEN: str = Field(default='', alias="APIFY_TOKEN")

    # Configuration Google Vertex AI
    VERTEX_PROJECT_ID: str = Field(default='', alias="VERTEX_PROJECT_ID")
    VERTEX_API_KEY: str = Field(default='', alias="VERTEX_API_KEY")

    # Configuration OSINT
    SHODAN_API_KEY: str = Field(default='', alias="SHODAN_API_KEY")
    CENSYS_API_ID: str = Field(default='', alias="CENSYS_API_ID")
    CENSYS_API_SECRET: str = Field(default='', alias="CENSYS_API_SECRET")
    SECURITYTRAILS_API_KEY: str = Field(default='', alias="SECURITYTRAILS_API_KEY")

    # Configuration proxy/Tor
    TOR_PROXY: str = Field(default='', alias="TOR_PROXY")  # "socks5://127.0.0.1:9050"

    # Configuration scraping avancé
    ENABLE_SELENIUM_FALLBACK: bool = Field(default=True, alias="ENABLE_SELENIUM_FALLBACK")
    DOWNLOAD_MEDIA: bool = Field(default=True, alias="DOWNLOAD_MEDIA")
    MEDIA_DIR: str = Field(default='downloads/media', alias="MEDIA_DIR")

    model_config = SettingsConfigDict(env_file="secrets/.env", populate_by_name=True)
