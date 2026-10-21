from fastapi import FastAPI

app = FastAPI(
    title="Cognium Risk Profiler API",
    description="API for risk assessment and portfolio recommendations.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
