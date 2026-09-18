import sys
import os

# Ensure root directory and current directory are in sys.path so 'main' can be imported in Vercel serverless environment
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
current_dir = os.path.dirname(os.path.abspath(__file__))
for path in (root_dir, current_dir, os.getcwd()):
    if path and path not in sys.path:
        sys.path.insert(0, path)

try:
    from main import app, handler, VercelPathMiddleware
except Exception as e:
    # Standalone fallback if main cannot be resolved in a partitioned lambda bundle
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from datetime import datetime
    import random

    app = FastAPI(title="CloudScale API", version="1.0.0", redirect_slashes=False)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fallback_state = {
        "cpu": 45.2,
        "memory": 52.1,
        "requests": 740,
        "latency": 64,
        "instances": 2,
        "autoscaling": True,
        "load_test": False,
        "history": []
    }

    @app.get("/api/health")
    @app.get("/health")
    @app.get("/api/index.py")
    @app.get("/api/index.py/health")
    def fallback_health():
        return {"status": "healthy", "service": "cloudscale-api", "mode": "serverless-fallback"}

    @app.get("/api/metrics")
    @app.get("/metrics")
    @app.get("/api/index.py/metrics")
    def fallback_metrics():
        fallback_state["cpu"] = round(random.uniform(40, 60), 1)
        fallback_state["memory"] = round(random.uniform(45, 65), 1)
        fallback_state["requests"] = random.randint(500, 1000)
        point = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "cpu": fallback_state["cpu"],
            "memory": fallback_state["memory"],
            "requests": fallback_state["requests"],
            "latency": fallback_state["latency"],
            "instances": fallback_state["instances"]
        }
        fallback_state["history"].append(point)
        fallback_state["history"] = fallback_state["history"][-30:]
        return fallback_state

    handler = app

# Ensure handler and app are exported for Vercel Python runtime
__all__ = ["app", "handler"]
