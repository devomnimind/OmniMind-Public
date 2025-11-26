import sys
import os
import uvicorn

# Add current directory to sys.path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    try:
        # Import the app
        from web.backend.main import app

        uvicorn.run(app, host="127.0.0.1", port=8001)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
