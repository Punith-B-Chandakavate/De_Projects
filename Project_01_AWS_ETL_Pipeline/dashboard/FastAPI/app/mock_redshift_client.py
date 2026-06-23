# app/mock_redshift_client.py
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class MockRedshiftDataClient:
    """Mock Redshift client for local development"""
    
    def __init__(self):
        logger.info("🔧 Using Mock Redshift Client for local development")
        self.agents = ["Sneha", "Kavya", "Rohit", "Ananya", "Arjun"]
        self.channels = ["Chat", "Web Form", "Email", "Phone"]
        self.categories = ["Payment Failure", "Account Locked", "Bug Report", "Login Issue", "Feature Request"]
        self.priorities = ["Low", "Medium", "High", "Critical"]
        self.statuses = ["Open", "Resolved", "Escalated"]
        self.log_levels = ["INFO", "DEBUG", "WARNING", "ERROR"]
        self.user_agents = ["PostmanRuntime/7.32.2", "curl/7.68.0", "Mozilla/5.0 (Windows NT 10.0)", 
                           "Mobile-Safari/537.36", "Python-urllib/3.9"]
        
    def execute_query(self, query: str, wait: bool = True, timeout: int = 300) -> List[Dict]:
        logger.info(f"Mock query executed: {query[:100]}...")
        return [{"result": "mock_data"}]
    
    def get_ticket_dashboard(self) -> Dict[str, Any]:
        return {
            "kpis": {
                "total_tickets": 856,
                "open_tickets": 67,
                "resolved_tickets": 750,
                "active_agents": 5,
                "avg_interactions": 4.5
            },
            "charts": {
                "by_agent": [{"name": a, "count": random.randint(20, 150)} for a in self.agents],
                "by_channel": [{"channel": c, "count": random.randint(50, 200)} for c in self.channels],
                "by_priority": [{"priority": p, "count": random.randint(10, 300)} for p in self.priorities],
                "by_status": [{"status": s, "count": random.randint(50, 400)} for s in self.statuses],
                "resolution_by_category": [{"category": c, "avg_time": round(random.uniform(30, 150), 2)} for c in self.categories]
            },
            "tables": {
                "detailed_tickets": [
                    {
                        "ticket_id": f"TCK070{i:04d}",
                        "agent": random.choice(self.agents),
                        "channel": random.choice(self.channels),
                        "issue_category": random.choice(self.categories),
                        "priority": random.choice(self.priorities),
                        "status": random.choice(self.statuses),
                        "interactions": random.randint(1, 10),
                        "resolution_minutes": random.randint(10, 300) if random.random() > 0.3 else None,
                        "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                        "resolved_at": (datetime.now() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d %H:%M:%S') if random.random() > 0.3 else None
                    } for i in range(1, 21)
                ],
                "agent_performance": [
                    {"agent": a, "tickets_handled": random.randint(20, 150), 
                     "resolved_count": random.randint(10, 100), 
                     "avg_resolution_minutes": round(random.uniform(30, 120), 2)} for a in self.agents
                ]
            }
        }
    
    def get_log_dashboard(self, days: int = 30) -> Dict[str, Any]:
        return {
            "kpis": {
                "total_logs": 2450,
                "error_logs": 45,
                "warning_logs": 120,
                "avg_cpu": 45.5,
                "avg_response_time": 750
            },
            "charts": {
                "cpu_trend": [{"date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
                              "avg_cpu": round(random.uniform(20, 80), 2)} for i in range(30, 0, -1)],
                "response_trend": [{"date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
                                   "avg_response": round(random.uniform(100, 1500), 2)} for i in range(30, 0, -1)],
                "log_levels": [{"level": l, "count": random.randint(100, 2000)} for l in self.log_levels],
                "user_agents": [{"user_agent": ua, "count": random.randint(50, 1000)} for ua in self.user_agents[:5]],
                "response_distribution": [
                    {"response_time_range": "0-500ms", "count": random.randint(100, 500)},
                    {"response_time_range": "500-1000ms", "count": random.randint(100, 400)},
                    {"response_time_range": "1000-1500ms", "count": random.randint(50, 300)},
                    {"response_time_range": ">1500ms", "count": random.randint(10, 100)}
                ],
                "logs_by_ticket": [{"ticket_id": f"TCK070{i:04d}", "log_count": random.randint(1, 20),
                                  "error_count": random.randint(0, 5), "warning_count": random.randint(0, 10)} 
                                 for i in range(1, 11)]
            }
        }