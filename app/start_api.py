#!/usr/bin/env python3
"""Start the FastAPI server"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Order Lifecycle API server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")

    # Use import string for reload to work properly
    uvicorn.run(
        "app.api:app",  # Import string: module.file:app_variable
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info",
    )
