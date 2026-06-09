import os
import boto3
import sys
from datetime import datetime, timedelta

# Project root directory
PROJECT_ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

sys.path.append(PROJECT_ROOT_DIR)

from config import AWS_CONFIG, S3_BUCKET

# Source log files location
SUPPORT_LOGS_SOURCE_DIR = os.path.join(
    PROJECT_ROOT_DIR,
    'datasets',
    'support-logs',
    'day-wise-logs-data'
)

# File used to track the last processed date
LOG_INGESTION_TRACKER_FILE = "log_date_tracker.txt"

# S3 destination prefix
S3_RAW_LOGS_PREFIX = 'support-logs/raw'

# ---------- UTILITY FUNCTIONS ----------
def read_last_date(file_path):
    """
    Reads the last successfully processed date from the tracker file.

    Args:
        file_path (str): Path to the tracker file.

    Returns:
        str: Last processed date in YYYY-MM-DD format.
             Returns '2025-06-30' if the tracker file does not exist.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
    return "2025-06-30"


def update_last_date(file_path, new_date):
    """
    Updates the tracker file with the latest processed date.

    Args:
        file_path (str): Path to the tracker file.
        new_date (str): Date to store in YYYY-MM-DD format.

    Returns:
        None
    """
    with open(file_path, 'w') as f:
        f.write(new_date)


def get_next_date(last_date_str):
    """
    Calculates the next date to be processed.

    Args:
        last_date_str (str): Previously processed date in YYYY-MM-DD format.

    Returns:
        str: Next date in YYYY-MM-DD format.
    """
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    next_date = last_date + timedelta(days=1)
    return next_date.strftime("%Y-%m-%d")


def upload_log_file_to_s3(file_path, bucket, key):
    """
    Uploads a support log file from the local filesystem to Amazon S3.

    Args:
        file_path (str): Full path of the log file.
        bucket (str): Target S3 bucket name.
        key (str): S3 object key (folder path + filename).

    Returns:
        None
    """
    s3 = boto3.client('s3', **AWS_CONFIG)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    s3.put_object(Bucket=bucket, Key=key, Body=content)
    print(f"✅ Uploaded log file to s3://{bucket}/{key}")


# ---------- MAIN INGESTION LOGIC ----------
def ingest_support_logs_to_s3():
    """
    Executes the daily support log ingestion process.

    Workflow:
        1. Read the last processed date from the tracker file.
        2. Calculate the next date to ingest.
        3. Build the expected log file path.
        4. Upload the log file to the raw S3 layer.
        5. Update the tracker file with the new date.

    Returns:
        None
    """
    last_date = read_last_date(LOG_INGESTION_TRACKER_FILE)
    next_date = get_next_date(last_date)

    file_name = f"support_logs_{next_date}.log"
    log_file_full_path = os.path.join(SUPPORT_LOGS_SOURCE_DIR, file_name)

    s3_key = f"{S3_RAW_LOGS_PREFIX}/support_logs_{next_date}.log"
    upload_log_file_to_s3(log_file_full_path, S3_BUCKET, s3_key)
    update_last_date(LOG_INGESTION_TRACKER_FILE, next_date)

    print(f"📅 Updated tracker to {next_date}")


# ---------- RUN ----------
if __name__ == "__main__":
    ingest_support_logs_to_s3()