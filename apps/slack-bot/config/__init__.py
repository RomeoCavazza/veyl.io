from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    slack_app_token: str = Field(..., alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., alias="SLACK_SIGNING_SECRET")
    gmail_user: str = Field(..., alias="GMAIL_USER")
    gmail_app_password: str = Field(..., alias="GMAIL_APP_PASSWORD")
    serpapi_api_key: str = Field(..., alias="SERPAPI_API_KEY")
    google_sheet_id: str = Field(..., alias="GOOGLE_SHEET_ID")
    env: str = Field(default="development", alias="ENV")

    model_config = SettingsConfigDict(
        env_file="secrets/.env",
        populate_by_name=True,
    )

settings = Settings()
