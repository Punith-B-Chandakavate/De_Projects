# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️ .env file not found at: {env_path}")

class Settings:
    # AWS Settings
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # Redshift Serverless Settings
    REDSHIFT_WORKGROUP = os.getenv("REDSHIFT_WORKGROUP", "default-workgroup")
    REDSHIFT_DATABASE = os.getenv("REDSHIFT_DATABASE", "dev")
    REDSHIFT_DB_USER = os.getenv("REDSHIFT_DB_USER", "awsuser")
    REDSHIFT_SCHEMA = os.getenv("REDSHIFT_SCHEMA", "public")
    
    # Mock Mode
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "True").lower() == "true"
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    CORS_ORIGINS = ["*"]
    APP_NAME = os.getenv("APP_NAME", "CarePlus Analytics")

settings = Settings()

# Print configuration
print("=" * 60)
print("🚀 CarePlus Dashboard Configuration:")
print(f"   - Mock Mode: {settings.USE_MOCK_DATA}")
print(f"   - Debug Mode: {settings.DEBUG}")
print(f"   - App Name: {settings.APP_NAME}")
if not settings.USE_MOCK_DATA:
    print(f"   - Redshift Workgroup: {settings.REDSHIFT_WORKGROUP}")
    print(f"   - Database: {settings.REDSHIFT_DATABASE}")
    print(f"   - Schema: {settings.REDSHIFT_SCHEMA}")
print("=" * 60)