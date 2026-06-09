import os
import pandas as pd
import boto3
from io import StringIO
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import sys


# Project root directory
PROJECT_ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

sys.path.append(PROJECT_ROOT_DIR)

from config import AWS_CONFIG, S3_BUCKET, DB_CONFIG

S3_PREFIX = "support-tickets/raw/"
DATE_TRACKER_FILE = "date_tracker.txt"

# ---------- UTILITY FUNCTIONS ----------
def get_engine(config):
    """
    Creates and returns a SQLAlchemy engine for connecting to MySQL.

    Args:
        config (dict): Database connection configuration.

    Returns:
        sqlalchemy.Engine: Database engine instance.
    """
    return create_engine(f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}")

def upload_to_s3(df, bucket, key):
    """
    Converts a DataFrame to CSV format and uploads it to S3.

    Args:
        df (pd.DataFrame): Data to upload.
        bucket (str): Target S3 bucket.
        key (str): S3 object key.

    Returns:
        None
    """
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = boto3.client('s3', **AWS_CONFIG)
    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
    print(f"✅ Uploaded to s3://{bucket}/{key}")

def read_last_date(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            last_date = f.read().strip()
            if last_date:
                return last_date
    return "2025-06-30"  # Starting point before 1st July

def update_last_date(file_path, new_date):
    with open(file_path, 'w') as f:
        f.write(new_date)

def get_next_date(last_date_str):
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    next_date = last_date + timedelta(days=1)
    return next_date.strftime("%Y-%m-%d")

# ---------- MAIN INGESTION LOGIC ----------
def ingest_support_tickets_to_s3():
    """
    Executes the daily support ticket ingestion process.

    Workflow:
        1. Establish a connection to the MySQL database.
        2. Read the last successfully processed date from the tracker file.
        3. Calculate the next date that needs to be ingested.
        4. Fetch support ticket records created on that date.
        5. Validate whether data exists for the selected date.
        6. Upload the extracted data to the raw layer in Amazon S3.
        7. Update the tracker file with the newly processed date.

    Returns:
        str: Success message when data is uploaded successfully.
        None: If no records are found for the target date.

    Example:
        If the tracker file contains '2025-07-03':
            - The function processes data for '2025-07-04'
            - Uploads it to:
              support-tickets/raw/support_tickets_2025-07-04.csv
            - Updates the tracker file to '2025-07-04'


        Read Last Processed Date
                    │
                    ▼
        Calculate Next Date
                    │
                    ▼
        Extract Data From MySQL
                    │
                    ▼
        Check If Data Exists
                    │
                    ▼
        Upload CSV To S3
                    │
                    ▼
        Update Tracker File
    """
    engine = get_engine(DB_CONFIG)
    last_date = read_last_date(DATE_TRACKER_FILE)
    next_date = get_next_date(last_date)

    # Query only that day’s data
    query = f"""
        SELECT * FROM support_tickets
        WHERE DATE(created_at) = '{next_date}';
    """
    df = pd.read_sql(query, engine)
    print(df.shape)
    print(df.head())

    if df.empty:
        print(f"⚠️ No data found for {next_date}. Skipping upload.")
        return None

    # Upload to S3
    s3_key = f"{S3_PREFIX}support_tickets_{next_date}.csv"
    upload_to_s3(df, S3_BUCKET, s3_key)

    # Update date tracker
    update_last_date(DATE_TRACKER_FILE, next_date)
    print(f"📅 Updated tracker to {next_date}")
    return 'Data uploaded to S3 successfully'

# Run
if __name__ == "__main__":
    ingest_support_tickets_to_s3()
