# run.py - Place in project root
import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    print("=" * 60)
    print("🚀 Starting CarePlus Dashboard...")
    print(f"📍 Working directory: {os.getcwd()}")
    print("🌐 Server will run at: http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )