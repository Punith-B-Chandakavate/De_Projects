import boto3
import pandas as pd
import re
import pyarrow as pa
from pyarrow import parquet as pq
import io

def save_parquet_to_s3(df, bucket, key):
    """
        Converts a Pandas DataFrame into Parquet format and uploads it to the specified S3 location.
        Used to store processed data efficiently for analytics and downstream processing.

    """
    table = pa.Table.from_pandas(df, preserve_index=False)
    parquet_buffer = io.BytesIO()
    pq.write_table(table, parquet_buffer)

    # Upload to S3
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket, Key=key, Body=parquet_buffer.getvalue())
    print(f"✅ Parquet saved to s3://{bucket}/{key}")


def read_log_from_s3(bucket, key):
    """
    Reads a log file from an S3 bucket and returns its content as a UTF-8 string.
    Serves as the data ingestion step for the ETL pipeline.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    log_content = response['Body'].read().decode('utf-8')
    return log_content


LOG_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(?P<log_level>[A-Za-z0-9_]+)\] '
    r'(?P<component>[^\s]+) - TicketID=(?P<ticket_id>[^\s]+) SessionID=(?P<session_id>[^\s]+)\s*'
    r'IP=(?P<ip>.*?) \| ResponseTime=(?P<response_time>-?\d+)ms \| CPU=(?P<cpu>[\d.]+)% \| '
    r'EventType=(?P<event_type>.*?) \| Error=(?P<error>\w+)\s*'
    r'UserAgent="(?P<user_agent>.*?)"\s*'
    r'Message="(?P<message>.*?)"\s*'
    r'Debug="(?P<debug>.*?)"\s*'
    r'TraceID=(?P<trace_id>.*)'
)


def split_log_entries(content):
    """
    Splits the raw log content into individual log records using --- as the separator.
    Prepares the logs for parsing and structured extraction.
    """
    return [entry.strip() for entry in content.split("---") if entry.strip()]


def parse_log_entries(entries):
    """
    Extracts structured fields from each log entry using a regular expression pattern.
    Returns the parsed records as a Pandas DataFrame.
    """
    parsed_records = []

    for entry in entries:
        match = LOG_PATTERN.search(entry)
        if match:
            parsed_records.append(match.groupdict())

    return pd.DataFrame(parsed_records)


def convert_data_types(df):
    """
    Converts columns to appropriate data types such as datetime, integer, float, and boolean.
    Ensures the dataset is ready for validation and analysis.
    """
    df = df.copy()

    df["response_time"] = df["response_time"].astype(int)
    df["cpu"] = df["cpu"].astype(float)

    df["error"] = (
        df["error"]
        .str.lower()
        .map({"true": True, "false": False})
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    return df


def clean_response_time(df):
    """
    Removes records with negative response times, which are considered invalid.
    Improves data quality by filtering out corrupted metrics.
    """
    return df[df["response_time"] >= 0].copy()


def standardize_log_levels(df):
    """
    Normalizes inconsistent log level values such as INF0, DEBG, and warnING.
    Ensures log levels follow a consistent naming convention.
    """

    log_level_mapping = {
        "INF0": "INFO",
        "DEBG": "DEBUG",
        "warnING": "WARNING",
        "EROR": "ERROR"
    }

    df = df.copy()
    df["log_level"] = df["log_level"].replace(log_level_mapping)

    return df


def remove_duplicates(df):
    """
    Removes duplicate log records from the dataset.
    Prevents duplicate entries from affecting reporting and analytics.
    """
    return df.drop_duplicates()


def drop_unused_columns(df):
    """
    Drops unnecessary columns such as trace_id that are not required for analysis.
    Reduces storage usage and simplifies the final dataset.
    """
    return df.drop(columns=["trace_id"])


def clean_support_logs(file_path):
    """
    Executes the complete ETL workflow, including parsing, cleaning, validation, and deduplication.
    Returns a fully processed DataFrame ready for storage.
    """
    entries = split_log_entries(file_path)

    df = parse_log_entries(entries)

    df = drop_unused_columns(df)

    df = convert_data_types(df)

    df = clean_response_time(df)

    df = standardize_log_levels(df)

    df = remove_duplicates(df)

    return df


# Manually triggered
def lambda_handler(event, context):
    """
    AWS Lambda handler for processing support log files.

    When invoked manually (for example, through the AWS Lambda Console's
    Test feature or a direct Lambda invocation), the function reads a
    specified log file from S3, cleans and transforms the data, converts
    it to Parquet format, and stores the processed output in the
    designated S3 location.
    """
    bucket = 'careplus-data-demo-store'
    key = 'support-logs/raw/support_logs_2025-07-01.log'
    log_content = read_log_from_s3(bucket, key)

    cleaned_df = clean_support_logs(log_content)

    print(cleaned_df.head())
    print(f"\nFinal Shape: {cleaned_df.shape}")

    output_file_name = 'support_logs_2025-07-01.parquet'
    output_key = f'support-logs/processed/{output_file_name}'
    save_parquet_to_s3(cleaned_df, bucket, output_key)


# Automatically triggered
def lambda_handler(event, context):
    """
    AWS Lambda entry point for the automated ETL pipeline.

    This function is triggered whenever a new log file is uploaded to the
    S3 raw data folder. It reads the log file, cleans and transforms the
    data into a structured format, converts it to Parquet, and stores the
    processed output in the designated S3 processed folder for analytics
    and downstream processing.
    """
    # Extract S3 bucket and object details from the event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    # Read raw log file from S3
    log_content = read_log_from_s3(bucket, key)

    # Clean and transform log data into a DataFrame
    cleaned_df = clean_support_logs(log_content)

    print(cleaned_df.head())
    print(f"\nFinal Shape: {cleaned_df.shape}")

    # Generate output path for processed Parquet file
    output_file_name = key.split('/')[2].replace('.log', '.parquet')
    output_key = f'support-logs/processed/{output_file_name}'

    # Save processed data back to S3 in Parquet format
    save_parquet_to_s3(cleaned_df, bucket, output_key)


