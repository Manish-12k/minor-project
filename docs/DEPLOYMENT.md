# Deployment Guide

## 1. Backend deployment

The backend lives in `backend/` and uses Flask to expose the bot detection API.
It can also serve the React app from `backend/build` if the frontend has been built.

### Required files for hosting

- `backend/Procfile`
- `backend/runtime.txt`
- `backend/requirements.txt`

### Startup command

Use this command for free hosting platforms:

```bash
gunicorn ml_engine.inference.server:app --bind 0.0.0.0:$PORT
```

### Free hosting options

- **Render** free tier
- **Railway** free tier
- **Fly.io** free tier
- **Replit** free tier

### If you want one service for both frontend and backend

1. Build the frontend:

```bash
cd frontend
npm install
npm run build
```

2. Copy the React build into the backend folder:

```bash
cp -r build ../backend/build
```

3. Deploy the `backend/` folder.

## 2. Frontend-only deployment

If you choose to host the frontend separately, use one of these free platforms:

- Vercel
- Netlify
- GitHub Pages

### Vercel setup

This project is ready for Vercel as a static React site. The frontend uses `REACT_APP_API_URL` at build time to set the backend endpoint.

1. In Vercel, connect the `frontend` folder as the project root.
2. Use the build command:

```bash
npm install
npm run build
```

3. Use the output directory:

```bash
build
```

4. Add an environment variable in Vercel:

- Name: `REACT_APP_API_URL`
- Value: `https://<your-backend-host>/api`

5. Deploy.

If you do not set `REACT_APP_API_URL`, the frontend will use `http://localhost:8000` and will not connect to the deployed backend.

Then point the API calls in the frontend to your backend URL.

## 3. What you must do

- Make sure the model files exist in `backend/ml_engine/models/`
- Build the frontend before copying it into `backend/build`
- Deploy the backend from the `backend/` directory
- Use the provided `Procfile` and `runtime.txt`

## 4. Useful local commands

```bash
cd backend
python -m pip install -r requirements.txt
python ml_engine/inference/server.py
```

```bash
cd frontend
npm install
npm run build
```

```bash
cp -r frontend/build backend/build
```
