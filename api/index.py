import sys
import traceback
from fastapi import FastAPI

try:
    from backend.app.main import app
except Exception as e:
    tb = traceback.format_exc()
    print("CRITICAL IMPORT ERROR IN API/INDEX.PY:", file=sys.stderr)
    print(tb, file=sys.stderr)
    
    app = FastAPI(title="Fallback Debug App")
    
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    def debug_route(path_name: str):
        return {
            "error": "Failed to import application backend.",
            "exception": str(e),
            "traceback": tb.split("\n")
        }
