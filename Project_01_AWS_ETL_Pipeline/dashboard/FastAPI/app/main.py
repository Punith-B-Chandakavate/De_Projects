# app/main.py
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings
from app.config import settings

# Import routes
from app.routes import support_tickets, support_logs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CarePlus Analytics Dashboard",
    description="Dashboard for Support Tickets and Logs - Redshift Serverless",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Setup static files
static_dir = PROJECT_ROOT / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ Static files mounted from: {static_dir}")
else:
    static_dir.mkdir(parents=True, exist_ok=True)
    (static_dir / "css").mkdir(parents=True, exist_ok=True)
    (static_dir / "js").mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Setup templates
templates_dir = PROJECT_ROOT / "templates"
if not templates_dir.exists():
    templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Include routers
app.include_router(support_tickets.router)
app.include_router(support_logs.router)

# Simple dashboard endpoint - NO DICT PASSED
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page - Minimal version"""
    try:
        # Create a simple HTML page directly
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CarePlus Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
            <style>
                body { background-color: #f5f7fa; padding-top: 70px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
                .navbar { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .navbar-brand .badge { font-size: 0.6rem; vertical-align: middle; margin-left: 5px; }
                .dashboard-card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .dashboard-card:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.15); }
                .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }
                .metric-item { background: white; padding: 15px 10px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; cursor: default; }
                .metric-item:hover { transform: scale(1.05); }
                .metric-value { font-size: 1.8rem; font-weight: bold; color: #2c3e50; }
                .metric-label { color: #7f8c8d; font-size: 0.85rem; margin-top: 5px; }
                .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-top: 20px; }
                .chart-container { position: relative; height: 300px; margin: 20px 0; }
                .table-container { overflow-x: auto; margin-top: 20px; }
                .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500; display: inline-block; }
                .status-Open { background-color: #fff3cd; color: #856404; }
                .status-Resolved { background-color: #d4edda; color: #155724; }
                .status-Escalated { background-color: #f8d7da; color: #721c24; }
                .priority-Critical { color: #e74c3c; font-weight: bold; }
                .priority-High { color: #f39c12; font-weight: bold; }
                .priority-Medium { color: #3498db; font-weight: bold; }
                .priority-Low { color: #27ae60; font-weight: bold; }
                .page-section { display: none; animation: fadeIn 0.5s; }
                .page-section.active { display: block; }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
                .loading-spinner { text-align: center; padding: 50px; }
                .loading-spinner .spinner-border { width: 3rem; height: 3rem; }
                @media (max-width: 768px) { .metric-grid { grid-template-columns: repeat(2, 1fr); } .chart-grid { grid-template-columns: 1fr; } }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark fixed-top">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#">
                        <i class="bi bi-graph-up-arrow"></i> CarePlus Analytics
                        <span class="badge bg-success ms-2">Live</span>
                        <span class="badge bg-warning ms-1">Mock Data</span>
                    </a>
                    <div class="d-flex">
                        <span class="navbar-text me-3" id="lastUpdate">
                            <i class="bi bi-clock"></i> Last update: <span id="updateTime">Just now</span>
                        </span>
                        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                    </div>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                <a class="nav-link active" href="#" data-page="tickets">
                                    <i class="bi bi-ticket"></i> Support Tickets
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" data-page="logs">
                                    <i class="bi bi-file-text"></i> Support Logs
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            <div class="container-fluid mt-5 pt-3">
                <div id="dashboardContent">
                    <div class="text-center loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p>Loading dashboard data...</p>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="/static/js/dashboard.js"></script>
            <script src="/static/js/tickets.js"></script>
            <script src="/static/js/logs.js"></script>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('DOM loaded, initializing dashboard...');
                    if (typeof Dashboard !== 'undefined') {
                        window.dashboard = new Dashboard();
                        console.log('Dashboard initialized successfully');
                    } else {
                        console.error('Dashboard class not defined');
                        document.getElementById('dashboardContent').innerHTML = `
                            <div class="alert alert-danger">
                                <i class="bi bi-exclamation-triangle"></i>
                                Error: Dashboard not initialized. Please check console.
                            </div>
                        `;
                    }
                });
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return HTMLResponse(f"""
        <html>
            <head>
                <title>Dashboard Error</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="alert alert-danger">
                        <h4>Error loading dashboard</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                </div>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mock-data" if settings.USE_MOCK_DATA else "redshift-serverless",
        "using_mock": settings.USE_MOCK_DATA
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1",
        port=port, 
        reload=settings.DEBUG
    )