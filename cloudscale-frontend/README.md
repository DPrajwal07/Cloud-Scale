# CloudScale Frontend

Independent Vercel frontend project hosting the CloudScale Landing Page and interactive Telemetry & Scaling Dashboard.

## Overview
- **Landing Page**: Modern, responsive landing page featuring live hero telemetry streaming from the FastAPI backend.
- **Interactive Dashboard**: SPA for real-time workload monitoring, resource telemetry graphs, automated scaling policy controls, and synthetic load testing.
- **Architecture**: Communicates via HTTPS REST API with the independent `cloudscale-backend` service.

## Project Structure
```
cloudscale-frontend/
├── index.html               # Public landing page
├── css/
│   └── styles.css           # Global typography, themes, and animations
├── js/
│   ├── config.js            # Centralized API URL configuration
│   └── main.js              # Landing page interactivity & telemetry
├── dashboard/
│   ├── index.html           # Monitoring SPA
│   └── ...                  # Brand icons & logos
├── assets/
│   └── images/              # Media assets & badges
└── vercel.json              # Static routing rules
```

## Local Development
Serve the frontend using any static HTTP server (e.g. Python, Serve, or VS Code Live Server):

```bash
# Using Python
python3 -m http.server 3000

# Or using npx serve
npx serve . -p 3000
```
Then navigate to:
- Landing Page: `http://localhost:3000`
- Dashboard: `http://localhost:3000/dashboard/index.html`

During local development, `js/config.js` automatically targets `http://127.0.0.1:8000`.

## Connecting to Backend
In `js/config.js`:
- In local development, the API defaults to `http://127.0.0.1:8000`.
- In production, it defaults to your deployed backend Vercel URL (e.g. `https://cloudscale-backend.vercel.app`).
- You can override the backend URL dynamically in the browser console:
  ```javascript
  localStorage.setItem('cloudscale_api_url', 'https://your-backend-url.vercel.app');
  ```

## Vercel Deployment

1. Set the root directory in Vercel to `cloudscale-frontend` (or create a new Vercel project with `cloudscale-frontend` as project root).
2. Framework Preset: **Other** (Static site).
3. Update `DEFAULT_PROD_URL` in `js/config.js` to point to your deployed `cloudscale-backend` Vercel domain.
4. Deploy!
