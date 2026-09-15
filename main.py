import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.index import app, state, tick, add_event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/", include_in_schema=False)
def local_root():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "healthy",
        "service": "cloudscale-api",
        "version": "1.0.0",
        "health": "/api/health",
        "metrics": "/api/metrics"
    }

if os.path.exists(os.path.join(BASE_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(BASE_DIR, "css")), name="css")
if os.path.exists(os.path.join(BASE_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(BASE_DIR, "js")), name="js")
if os.path.exists(os.path.join(BASE_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "assets")), name="assets")
if os.path.exists(os.path.join(BASE_DIR, "dashboard")):
    app.mount("/dashboard", StaticFiles(directory=os.path.join(BASE_DIR, "dashboard"), html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
