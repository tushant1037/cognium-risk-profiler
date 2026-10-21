# Backend

FastAPI service for the Cognium Risk Profiler.

## Run locally

Install dependencies and start the development server from this directory:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation
is available at `/docs`, and the health check is at `/health`.

## Run tests

```bash
uv run pytest
```
