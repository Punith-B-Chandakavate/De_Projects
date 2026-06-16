-- ============================================================
-- Create Database
-- ============================================================
CREATE DATABASE careplus_db;

-- Connect to careplus_db before running the remaining queries


-- ============================================================
-- Create support_logs Table
-- ============================================================
CREATE TABLE public.support_logs (
    timestamp       TIMESTAMP,
    log_level       VARCHAR(20),
    component       VARCHAR(100),
    ticket_id       VARCHAR(50),
    session_id      VARCHAR(50),
    ip              VARCHAR(45),
    response_time   BIGINT,
    cpu             DOUBLE PRECISION,
    event_type      VARCHAR(50),
    error           BOOLEAN,
    user_agent      VARCHAR(300),
    message         VARCHAR(1000),
    debug           VARCHAR(1000)
);

-- Load support logs data from Amazon S3
COPY public.support_logs
FROM 's3://careplus-data-demo-store/support-logs/processed/'
IAM_ROLE 'arn:aws:iam::183631303403:role/service-role/AmazonRedshift-CommandsAccessRole-20260616T120544'
FORMAT AS PARQUET
REGION 'ap-south-1';

-- Verify loaded data
SELECT *
FROM public.support_logs;


-- ============================================================
-- Create support_tickets Table
-- ============================================================
CREATE TABLE public.support_tickets (
    ticket_id           VARCHAR(50),
    created_at          TIMESTAMP,
    resolved_at         TIMESTAMP,
    agent               VARCHAR(100),
    priority            VARCHAR(20),
    num_interactions    BIGINT,
    issue_category      VARCHAR(100),
    channel             VARCHAR(50),
    status              VARCHAR(20)
);

-- Load support tickets data from Amazon S3
COPY public.support_tickets
FROM 's3://careplus-data-demo-store/support-tickets/processed/'
IAM_ROLE 'arn:aws:iam::183631303403:role/service-role/AmazonRedshift-CommandsAccessRole-20260616T120544'
FORMAT AS PARQUET
REGION 'ap-south-1';

-- Verify loaded data
SELECT *
FROM public.support_tickets;