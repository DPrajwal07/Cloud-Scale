from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random
import os

app = FastAPI(title="CloudScale API", version="1.0.0", redirect_slashes=False)

# Configure CORS: Allow frontend origin via FRONTEND_URL or local development origins
frontend_url_env = os.getenv("FRONTEND_URL", "").strip()
configured_origins = [o.strip() for o in frontend_url_env.split(",") if o.strip()]

default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

allowed_origins = list(dict.fromkeys(configured_origins + default_origins))

if "*" in configured_origins or frontend_url_env == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Authoritative CloudScale simulation state
state = {
    "cpu": 42.0,
    "memory": 48.0,
    "requests": 620,
    "latency": 82,
    "instances": 2,
    "min_instances": 1,
    "max_instances": 5,
    "scale_up_threshold": 75,
    "scale_down_threshold": 30,
    "autoscaling": True,
    "load_test": False,
    "history": [],
    "events": []
}

def add_event(message: str, kind: str = "info"):
    event = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "kind": kind
    }
    state["events"].insert(0, event)
    state["events"] = state["events"][:30]

def tick():
    """Authoritative infrastructure telemetry simulation step"""
    if state["load_test"]:
        target = random.uniform(76, 94)
        state["requests"] = random.randint(1400, 2600)
    else:
        target = random.uniform(35, 65)
        state["requests"] = random.randint(350, 950)

    state["cpu"] += (target - state["cpu"]) * 0.28
    state["memory"] += (random.uniform(35, 65) - state["memory"]) * 0.18
    state["latency"] = max(35, int(45 + state["cpu"] * 1.15 + random.uniform(-10, 10)))

    if state["autoscaling"]:
        if state["cpu"] >= state["scale_up_threshold"] and state["instances"] < state["max_instances"]:
            state["instances"] += 1
            add_event(f"Instance {state['instances']:02d} launched — CPU threshold exceeded", "scale")
        elif state["cpu"] <= state["scale_down_threshold"] and state["instances"] > state["min_instances"]:
            state["instances"] -= 1
            add_event(f"Instance removed — workload returned to normal", "scale")

    point = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "cpu": round(state["cpu"], 1),
        "memory": round(state["memory"], 1),
        "requests": state["requests"],
        "latency": state["latency"],
        "instances": state["instances"]
    }
    state["history"].append(point)
    state["history"] = state["history"][-30:]

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "cloudscale-api",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "metrics": "/api/metrics"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/api")
@app.get("/api/")
def api_root():
    return {
        "status": "healthy",
        "service": "cloudscale-api",
        "version": "1.0.0",
        "health": "/api/health",
        "metrics": "/api/metrics"
    }

@app.get("/api/health")
@app.get("/api/health/")
@app.get("/health")
@app.get("/health/")
def health():
    return {
        "status": "healthy",
        "service": "cloudscale-api"
    }

@app.get("/api/metrics")
@app.get("/api/metrics/")
@app.get("/metrics")
@app.get("/metrics/")
def metrics():
    tick()
    return {
        "cpu": round(state["cpu"], 1),
        "memory": round(state["memory"], 1),
        "requests": state["requests"],
        "latency": state["latency"],
        "instances": state["instances"],
        "autoscaling": state["autoscaling"],
        "load_test": state["load_test"],
        "history": state["history"]
    }

@app.get("/api/resources")
@app.get("/api/resources/")
@app.get("/resources")
@app.get("/resources/")
def resources():
    return [
        {
            "id": f"cloudscale-{i:02d}",
            "status": "Healthy",
            "cpu": round(max(5, state["cpu"] + random.uniform(-12, 12)), 1),
            "memory": round(max(10, state["memory"] + random.uniform(-10, 10)), 1),
            "region": "ap-south-1",
            "type": "t3.small"
        }
        for i in range(1, state["instances"] + 1)
    ]

@app.get("/api/autoscaling")
@app.get("/api/autoscaling/")
@app.get("/autoscaling")
@app.get("/autoscaling/")
def autoscaling():
    return {
        "enabled": state["autoscaling"],
        "min_instances": state["min_instances"],
        "max_instances": state["max_instances"],
        "scale_up_threshold": state["scale_up_threshold"],
        "scale_down_threshold": state["scale_down_threshold"]
    }

class ScalingConfig(BaseModel):
    enabled: bool
    min_instances: int
    max_instances: int
    scale_up_threshold: float
    scale_down_threshold: float

@app.post("/api/autoscaling")
@app.post("/api/autoscaling/")
@app.post("/autoscaling")
@app.post("/autoscaling/")
def update_autoscaling(config: ScalingConfig):
    state["autoscaling"] = config.enabled
    state["min_instances"] = max(1, config.min_instances)
    state["max_instances"] = max(state["min_instances"], config.max_instances)
    state["scale_up_threshold"] = config.scale_up_threshold
    state["scale_down_threshold"] = config.scale_down_threshold
    add_event("Auto-scaling policy updated", "config")
    return {"success": True, **config.model_dump()}

class LoadConfig(BaseModel):
    enabled: bool

@app.post("/api/load-test")
@app.post("/api/load-test/")
@app.post("/load-test")
@app.post("/load-test/")
def load_test(config: LoadConfig):
    state["load_test"] = config.enabled
    add_event(
        "Synthetic load test started" if config.enabled else "Synthetic load test stopped",
        "load"
    )
    return {"success": True, "load_test": state["load_test"]}

@app.get("/api/activity")
@app.get("/api/activity/")
@app.get("/activity")
@app.get("/activity/")
def activity():
    return state["events"]

@app.get("/api/insights")
@app.get("/api/insights/")
@app.get("/insights")
@app.get("/insights/")
def insights():
    if state["cpu"] > 75:
        return {
            "severity": "warning",
            "title": "High workload detected",
            "message": f"CPU is at {state['cpu']:.0f}%. Auto-scaling is {'enabled' if state['autoscaling'] else 'disabled'}. Consider maintaining at least {min(state['instances'] + 1, state['max_instances'])} instances during peak traffic."
        }
    return {
        "severity": "success",
        "title": "Infrastructure operating normally",
        "message": "Current workload is within the configured operating range. No scaling intervention is required."
    }

# Export for Vercel ASGI runner
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
