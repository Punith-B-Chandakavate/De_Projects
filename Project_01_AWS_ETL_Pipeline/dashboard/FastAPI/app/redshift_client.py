# app/redshift_client.py
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Import both clients
from app.mock_redshift_client import MockRedshiftDataClient
from app.real_redshift_client import RealRedshiftDataClient

# Choose which client to use based on settings
if settings.USE_MOCK_DATA:
    RedshiftDataClient = MockRedshiftDataClient
    print("🔧 Using MOCK Redshift client for local development")
else:
    try:
        # Test the real connection to Serverless
        test_client = RealRedshiftDataClient()
        test_client.execute_query("SELECT 1 as test", timeout=10)
        RedshiftDataClient = RealRedshiftDataClient
        print("🔗 Connected to REAL Redshift Serverless successfully!")
        print(f"   Workgroup: {settings.REDSHIFT_WORKGROUP}")
        print(f"   Database: {settings.REDSHIFT_DATABASE}")
    except Exception as e:
        print(f"⚠️ Failed to connect to real Redshift: {e}")
        print("🔄 Falling back to MOCK client")
        RedshiftDataClient = MockRedshiftDataClient