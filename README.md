# Cognium Risk Profiler

## Demo

[![Watch the Cognium Risk Profiler demo](https://img.youtube.com/vi/3IGnOUSstfw/hqdefault.jpg)](https://youtu.be/3IGnOUSstfw?si=uW5CYgr7ZF4rGrvv)

Click the thumbnail to watch the demo on YouTube.

The
backend is a FastAPI service managed with `uv`; the frontend is a React, Vite,
TypeScript, and Tailwind CSS app managed with `npm`.

## Prerequisites

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) for backend
  dependency and environment management
- Node.js 20.19+ or 22.12+, with `npm`, for the frontend

Install the package managers with Homebrew:

```bash
brew install uv
brew install node
```

## Run locally

Run the backend and frontend in separate terminal windows.

### 1. Install backend packages and start the API

From the repository root:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

`uv sync` creates the backend virtual environment and installs the packages
declared in `backend/pyproject.toml` and pinned in `backend/uv.lock`. The API
will be available at `http://127.0.0.1:8000`; interactive documentation is at
`http://127.0.0.1:8000/docs`, and the health check is at
`http://127.0.0.1:8000/api/v1/health`.

Natural-language recommendations use Gemini. To enable them, add gemini api key
to `backend/.env`:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
```

The API's other features can be used without configuring this key.

### 2. Install frontend packages and start the web app

In a second terminal, from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

`npm ci` installs the exact frontend dependencies recorded in
`frontend/package-lock.json`. Open the local URL printed by Vite, typically
`http://localhost:5173`. During local development, Vite proxies `/api` requests
to the backend at `http://127.0.0.1:8000`, so keep the backend running as well.


## Build and test

Build the frontend for production from `frontend/`:

```bash
npm run build
npm run preview
```

Run the backend tests from `backend/`:

```bash
uv run pytest
```
