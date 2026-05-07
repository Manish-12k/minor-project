# Backend Deployment and Local Startup

This backend is a Flask API server for the bot detection system.
It is designed to run from the `backend` folder and can optionally serve the React frontend build from `backend/build`.

## Local setup

1. Install Python dependencies:

```powershell
cd backend
python -m pip install -r requirements.txt
```

2. Start the backend locally:

```powershell
python ml_engine\inference\server.py
```

3. Test the health endpoint:

```powershell
curl http://localhost:8000/health
```

## Frontend build for a single-service deployment

If you want the backend to serve the React app too:

1. Build the frontend:

```powershell
cd ..\frontend
npm install
npm run build
```

2. Copy the build output into the backend folder:

```powershell
robocopy build ..\backend\build /e
```

3. Start the backend again.

Now `http://localhost:8000/` will serve the React app.

## Deploying on a free platform

This repo is ready for free Python hosting platforms such as Render, Railway, or Fly.io.

### Recommended configuration

- Root directory: `backend`
- Start command: `gunicorn ml_engine.inference.server:app --bind 0.0.0.0:$PORT`
- Python runtime: `python-3.11.17`
- Requirements file: `requirements.txt`

### Important notes

- The backend expects the ML model files to exist at:
  - `backend/ml_engine/models/xgboost_bot_detector_latest.pkl`
  - `backend/ml_engine/models/scaler_latest.pkl`

- If you want a single deployed service, build the frontend and copy `frontend/build` into `backend/build` before deploying.

- If you prefer separate hosting, deploy the frontend on Vercel/Netlify and the backend on Render/Railway, then update the frontend API base URL accordingly.
