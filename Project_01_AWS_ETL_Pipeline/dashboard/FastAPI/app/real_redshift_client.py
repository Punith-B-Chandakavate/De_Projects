# app/real_redshift_client.py
import boto3
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)

class RealRedshiftDataClient:
    """Real Redshift Serverless client using boto3 Data API"""
    
    def __init__(self):
        try:
            self.client = boto3.client(
                'redshift-data',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            self.workgroup_name = settings.REDSHIFT_WORKGROUP
            self.database = settings.REDSHIFT_DATABASE
            self.db_user = settings.REDSHIFT_DB_USER
            self.schema = settings.REDSHIFT_SCHEMA
            logger.info(f"✅ Real Redshift Serverless client initialized for workgroup: {self.workgroup_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redshift client: {e}")
            raise
        
    def execute_query(self, query: str, wait: bool = True, timeout: int = 300) -> List[Dict]:
        """Execute a SQL query using Redshift Data API for Serverless"""
        try:
            response = self.client.execute_statement(
                WorkgroupName=self.workgroup_name,
                Database=self.database,
                DbUser=self.db_user,
                Sql=query,
                StatementName=f"dashboard_query_{int(time.time())}"
            )
            
            query_id = response['Id']
            logger.info(f"📊 Query executed with ID: {query_id}")
            
            if not wait:
                return [{"query_id": query_id, "status": "submitted"}]
            
            return self.wait_for_query_results(query_id, timeout)
            
        except ClientError as e:
            logger.error(f"❌ Redshift Data API error: {e}")
            if "WorkgroupNotFound" in str(e):
                raise Exception(f"Workgroup '{self.workgroup_name}' not found. Please check your workgroup name.")
            elif "AccessDenied" in str(e):
                raise Exception("Access denied. Please check your IAM permissions.")
            else:
                raise

    def wait_for_query_results(self, query_id: str, timeout: int = 300) -> List[Dict]:
        """Wait for query to complete and fetch results"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Query {query_id} timed out after {timeout} seconds")
            
            try:
                response = self.client.describe_statement(Id=query_id)
                status = response['Status']
                
                if status == 'FAILED':
                    error = response.get('Error', 'Unknown error')
                    raise Exception(f"Query failed: {error}")
                
                if status == 'FINISHED':
                    return self.fetch_results(query_id)
                
                time.sleep(1)
            except ClientError as e:
                logger.error(f"❌ Error checking query status: {e}")
                raise

    def fetch_results(self, query_id: str) -> List[Dict]:
        """Fetch results from a completed query"""
        try:
            response = self.client.get_statement_result(Id=query_id)
            
            columns = [col['name'] for col in response.get('ColumnMetadata', [])]
            records = response.get('Records', [])
            
            results = []
            for record in records:
                row = {}
                for i, col_name in enumerate(columns):
                    value = None
                    if i < len(record):
                        value = record[i].get('stringValue') or \
                               record[i].get('longValue') or \
                               record[i].get('doubleValue') or \
                               record[i].get('booleanValue') or \
                               record[i].get('blobValue') or \
                               None
                    row[col_name] = value
                results.append(row)
            
            logger.info(f"✅ Fetched {len(results)} rows from Redshift")
            return results
            
        except ClientError as e:
            logger.error(f"❌ Error fetching results: {e}")
            raise

    # ============= SUPPORT TICKET QUERIES =============
    
    def get_ticket_dashboard(self) -> Dict[str, Any]:
        """Get complete ticket dashboard data from Redshift Serverless"""
        try:
            # KPI Query
            kpi_query = f"""
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_tickets,
                    COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_tickets,
                    COUNT(DISTINCT agent) as active_agents,
                    COALESCE(AVG(num_interactions), 0) as avg_interactions
                FROM {self.schema}.support_tickets
            """
            
            # Analytics Queries
            by_agent = f"""
                SELECT agent as name, COUNT(*) as count
                FROM {self.schema}.support_tickets
                GROUP BY agent ORDER BY count DESC
            """
            
            by_channel = f"""
                SELECT channel, COUNT(*) as count
                FROM {self.schema}.support_tickets
                GROUP BY channel ORDER BY count DESC
            """
            
            by_priority = f"""
                SELECT priority, COUNT(*) as count
                FROM {self.schema}.support_tickets
                GROUP BY priority ORDER BY count DESC
            """
            
            by_status = f"""
                SELECT status, COUNT(*) as count
                FROM {self.schema}.support_tickets
                GROUP BY status
            """
            
            resolution_by_category = f"""
                SELECT issue_category as category, 
                       COALESCE(AVG(DATEDIFF(minute, created_at, resolved_at)), 0) as avg_time
                FROM {self.schema}.support_tickets
                WHERE resolved_at IS NOT NULL AND status = 'Resolved'
                GROUP BY issue_category ORDER BY avg_time DESC
            """
            
            detailed_tickets = f"""
                SELECT ticket_id, agent, channel, issue_category, priority, status, 
                       num_interactions as interactions,
                       DATEDIFF(minute, created_at, resolved_at) as resolution_minutes,
                       TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at,
                       TO_CHAR(resolved_at, 'YYYY-MM-DD HH24:MI:SS') as resolved_at
                FROM {self.schema}.support_tickets
                ORDER BY created_at DESC LIMIT 100
            """
            
            agent_performance = f"""
                SELECT agent, COUNT(*) as tickets_handled,
                       COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_count,
                       COALESCE(AVG(DATEDIFF(minute, created_at, resolved_at)), 0) as avg_resolution_minutes
                FROM {self.schema}.support_tickets
                GROUP BY agent ORDER BY tickets_handled DESC
            """
            
            logger.info("📊 Fetching ticket dashboard data from Redshift Serverless...")
            
            kpi_data = self.execute_query(kpi_query)
            kpi_data = kpi_data[0] if kpi_data else {}
            
            return {
                "kpis": {
                    "total_tickets": int(kpi_data.get("total_tickets", 0)),
                    "open_tickets": int(kpi_data.get("open_tickets", 0)),
                    "resolved_tickets": int(kpi_data.get("resolved_tickets", 0)),
                    "active_agents": int(kpi_data.get("active_agents", 0)),
                    "avg_interactions": round(float(kpi_data.get("avg_interactions", 0)), 2)
                },
                "charts": {
                    "by_agent": self.execute_query(by_agent),
                    "by_channel": self.execute_query(by_channel),
                    "by_priority": self.execute_query(by_priority),
                    "by_status": self.execute_query(by_status),
                    "resolution_by_category": self.execute_query(resolution_by_category)
                },
                "tables": {
                    "detailed_tickets": self.execute_query(detailed_tickets),
                    "agent_performance": self.execute_query(agent_performance)
                }
            }
        except Exception as e:
            logger.error(f"❌ Error fetching ticket dashboard: {e}")
            raise

    # ============= SUPPORT LOG QUERIES =============
    
    def get_log_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Get complete log dashboard data from Redshift Serverless"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # KPI Query
            kpi_query = f"""
                SELECT 
                    COUNT(*) as total_logs,
                    COUNT(CASE WHEN log_level = 'ERROR' THEN 1 END) as error_logs,
                    COUNT(CASE WHEN log_level = 'WARNING' THEN 1 END) as warning_logs,
                    COALESCE(AVG(cpu), 0) as avg_cpu,
                    COALESCE(AVG(response_time), 0) as avg_response_time
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
            """
            
            # Analytics Queries
            cpu_trend = f"""
                SELECT DATE(timestamp) as date, COALESCE(AVG(cpu), 0) as avg_cpu
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
                GROUP BY DATE(timestamp) ORDER BY date
            """
            
            response_trend = f"""
                SELECT DATE(timestamp) as date, COALESCE(AVG(response_time), 0) as avg_response
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
                GROUP BY DATE(timestamp) ORDER BY date
            """
            
            log_levels = f"""
                SELECT log_level as level, COUNT(*) as count
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
                GROUP BY log_level ORDER BY count DESC
            """
            
            user_agents = f"""
                SELECT user_agent, COUNT(*) as count
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
                GROUP BY user_agent ORDER BY count DESC LIMIT 10
            """
            
            response_distribution = f"""
                SELECT 
                    CASE 
                        WHEN response_time < 500 THEN '0-500ms'
                        WHEN response_time < 1000 THEN '500-1000ms'
                        WHEN response_time < 1500 THEN '1000-1500ms'
                        ELSE '>1500ms'
                    END as response_time_range,
                    COUNT(*) as count
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
                GROUP BY 
                    CASE 
                        WHEN response_time < 500 THEN '0-500ms'
                        WHEN response_time < 1000 THEN '500-1000ms'
                        WHEN response_time < 1500 THEN '1000-1500ms'
                        ELSE '>1500ms'
                    END
                ORDER BY count DESC
            """
            
            logs_by_ticket = f"""
                SELECT ticket_id, COUNT(*) as log_count, 
                       COUNT(CASE WHEN log_level = 'ERROR' THEN 1 END) as error_count,
                       COUNT(CASE WHEN log_level = 'WARNING' THEN 1 END) as warning_count
                FROM {self.schema}.support_logs
                WHERE timestamp >= '{since_date}'
                GROUP BY ticket_id
                ORDER BY log_count DESC LIMIT 20
            """
            
            logger.info(f"📊 Fetching log dashboard data from Redshift Serverless (last {days} days)...")
            
            kpi_data = self.execute_query(kpi_query)
            kpi_data = kpi_data[0] if kpi_data else {}
            
            return {
                "kpis": {
                    "total_logs": int(kpi_data.get("total_logs", 0)),
                    "error_logs": int(kpi_data.get("error_logs", 0)),
                    "warning_logs": int(kpi_data.get("warning_logs", 0)),
                    "avg_cpu": round(float(kpi_data.get("avg_cpu", 0)), 2),
                    "avg_response_time": round(float(kpi_data.get("avg_response_time", 0)), 2)
                },
                "charts": {
                    "cpu_trend": self.execute_query(cpu_trend),
                    "response_trend": self.execute_query(response_trend),
                    "log_levels": self.execute_query(log_levels),
                    "user_agents": self.execute_query(user_agents),
                    "response_distribution": self.execute_query(response_distribution),
                    "logs_by_ticket": self.execute_query(logs_by_ticket)
                }
            }
        except Exception as e:
            logger.error(f"❌ Error fetching log dashboard: {e}")
            raise