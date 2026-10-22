# Cognium Risk Profiler frontend

React, TypeScript, Vite, and Tailwind CSS frontend for the FastAPI service.

## Run locally

Start the backend from the repository root:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

In another terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (typically `http://localhost:5173`). The Vite
development server proxies `/api` requests to `http://127.0.0.1:8000`.

For a separately hosted API, set `VITE_API_BASE_URL` in a local `.env` file.
The natural-language recommendation endpoint also requires `GEMINI_API_KEY` in
`backend/.env`.

## Build

```bash
npm run build
npm run preview
```
