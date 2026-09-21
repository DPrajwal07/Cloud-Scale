# CloudScale Backend API

Independent FastAPI backend service powering the CloudScale infrastructure simulation and telemetry engine.

## Features
- **Simulation Engine**: Authoritative real-time simulation of CPU, memory, request volume, response latency, and dynamic node scaling.
- **REST API Endpoints**: Full suite of metrics, resources, auto-scaling policy, load test toggling, audit events, and insights.
- **CORS Configured**: Secure cross-origin resource sharing configurable for Vercel production frontend origin or local dev.
- **Interactive Documentation**: Built-in Swagger UI at `/docs`.

## Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service metadata & status descriptor |
| `GET` | `/api/health` | Health check endpoint (`{"status": "healthy"}`) |
| `GET` | `/api/metrics` | Live telemetry (CPU, Memory, Requests, Latency, Instances, History) |
| `GET` | `/api/resources` | Virtual compute instances details & load |
| `GET` | `/api/autoscaling` | Current auto-scaling configuration and thresholds |
| `POST` | `/api/autoscaling` | Update auto-scaling policy |
| `POST` | `/api/load-test` | Toggle synthetic load testing (`{"enabled": true/false}`) |
| `GET` | `/api/activity` | Infrastructure event log stream |
| `GET` | `/api/insights` | Workload recommendations & status |
| `GET` | `/docs` | Interactive OpenAPI Swagger UI |

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Development Server
```bash
uvicorn main:app --reload --port 8000
```
The API will be available at `http://127.0.0.1:8000`.

## Environment Variables
- `FRONTEND_URL` *(optional)*: Allowed frontend origin for production (e.g. `https://cloudscale-frontend.vercel.app`). Can be a single origin or comma-separated list. Defaults to allowing standard local origins.

## Vercel Deployment

1. Set the root directory in Vercel to `cloudscale-backend` (or create a new Vercel project with `cloudscale-backend` as project root).
2. Framework Preset: **Other**.
3. Environment Variables:
   - Add `FRONTEND_URL` pointing to your Vercel frontend domain (e.g. `https://cloudscale-frontend.vercel.app`).
4. Deploy!
