import urllib.parse
import boto3
import time

# Redshift Data API client
redshift = boto3.client(
    "redshift-data",
    region_name="ap-south-1"
    )

# Configuration
DATABASE = "careplus_db"
WORKGROUP_NAME = "default-workgroup"
IAM_ROLE = "arn:aws:iam::18303403:role/service-role/AmazonRedshift-CommandsAccessRole-20260644"

# Map S3 folder prefixes to Redshift tables
TABLE_MAPPING = {
    "support-logs/processed/": "support_logs",
    "support-tickets/processed/": "support_tickets"
}


def get_table_name(s3_key):
    for prefix, table in TABLE_MAPPING.items():
        if s3_key.startswith(prefix):
            return table
    return None


def lambda_handler(event, context):

    try:
        # Get S3 event details
        record = event["Records"][0]

        bucket_name = record["s3"]["bucket"]["name"]
        object_key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        print(f"Bucket: {bucket_name}")
        print(f"File: {object_key}")

        # Determine destination table
        table_name = get_table_name(object_key)

        if not table_name:
            return {
                "statusCode": 400,
                "message": f"No table mapping found for {object_key}"
            }

        # Build S3 file path
        s3_file_path = f"s3://{bucket_name}/{object_key}"

        # COPY command
        copy_sql = f"""
        COPY public.{table_name}
        FROM '{s3_file_path}'
        IAM_ROLE '{IAM_ROLE}'
        FORMAT AS PARQUET;
        """

        print(copy_sql)

        # Execute COPY
        response = redshift.execute_statement(
            WorkgroupName=WORKGROUP_NAME,
            Database=DATABASE,
            Sql=copy_sql
        )

        statement_id = response["Id"]

        print(f"COPY command submitted: {statement_id}")
        while True:
            result = redshift.describe_statement(
                Id=statement_id
            )

            status = result["Status"]
            print(f"Status: {status}")

            if status == "FINISHED":
                print("COPY completed successfully")
                break

            if status in ["FAILED", "ABORTED"]:
                print("COPY failed")
                print(result)
                raise Exception(result.get("Error"))

            time.sleep(5)


        return {
            "statusCode": 200,
            "table": table_name,
            "file": s3_file_path,
            "statement_id": statement_id
        }

    except Exception as e:
        print(f"Error: {str(e)}")

        return {
            "statusCode": 500,
            "error": str(e)
        }