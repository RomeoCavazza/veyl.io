import os

os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
os.environ["SLACK_SIGNING_SECRET"] = "whsec-0123456789abcdef0123456789abcdef"
os.environ["SERPAPI_API_KEY"] = "a" * 64
os.environ["GMAIL_USER"] = "bot@example.com"
os.environ["GMAIL_APP_PASSWORD"] = "a1b2c3d4e5f6g7h8"
os.environ["GOOGLE_SHEET_ID"] = "1A2B3C4D5E6F7G8H9I0JKLMNOPQR"
os.environ["HOST"] = "localhost"
os.environ["PORT"] = "8000"

