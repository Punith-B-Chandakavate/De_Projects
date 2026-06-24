import pyarrow.parquet as pq
import pandas as pd

table = pq.read_table("support_logs_2025-07-01.parquet")
print(table.schema)

""""
timestamp: timestamp[us]
log_level: large_string
component: large_string
ticket_id: large_string
session_id: large_string
ip: large_string
response_time: int64
cpu: double
event_type: large_string
error: bool
user_agent: large_string
message: large_string
debug: large_string
"""

table = pq.read_table("run-1781247152251-part-block-0-r-00000-snappy.parquet")
print(table.schema)

"""
ticket_id: string
created_at: timestamp[ns]
resolved_at: timestamp[ns]
agent: string
priority: string
num_interactions: int32
issue_category: string
channel: string
status: string
"""


