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

## Natural-language recommendations

`POST /api/recommend/natural-language` accepts a JSON body such as
`{"prompt":"Find low-cost US equity ETFs, exclude crypto, and prefer ESG funds"}`.
Gemini parses the request into filters constrained to values in `universe.json`.
Instruments and per-instrument justifications come only from deterministic
filtering of that dataset; Gemini generates only the explanatory narrative.
Set `GEMINI_API_KEY` in `backend/.env` to enable this endpoint.

## Run tests

```bash
uv run pytest
```
