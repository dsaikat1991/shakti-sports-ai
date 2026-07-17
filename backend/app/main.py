import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


def _cors_allowed_origins() -> list[str]:
    """
    Environment-driven CORS allowlist (Milestone C low-risk cleanup -
    previously hardcoded to the local Vite dev port only, which meant
    CORS would silently reject every request from any deployed
    environment). Set CORS_ALLOWED_ORIGINS to a comma-separated list of
    exact origins (e.g. "https://app.example.com,https://staging.example.com")
    to override the development-only default below.

    Deliberately never resolves to a wildcard: this API sets
    allow_credentials=True (the frontend's Supabase-authenticated
    requests need it), and per the CORS spec, a browser combining
    allow_origins=["*"] with credentialed requests is either rejected
    outright or - depending on the middleware - silently downgraded to
    echoing back whatever Origin header the request actually sent, which
    would let any site make authenticated requests against this API.
    Explicit origins only, always.
    """
    raw = os.getenv("CORS_ALLOWED_ORIGINS")

    if raw:
        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    else:
        # Development default - matches the frontend's Vite dev server,
        # which is hardcoded to port 5173 (see docs/ENGINEERING_HANDOFF.md).
        origins = ["http://localhost:5173"]

    if "*" in origins:
        raise RuntimeError(
            'CORS_ALLOWED_ORIGINS must not include "*" - this API requires '
            "allow_credentials=True for Supabase-authenticated requests, and "
            "a wildcard origin combined with credentials effectively allows "
            "any site to make authenticated requests against it. List exact "
            "origins instead, comma-separated."
        )

    return origins


app = FastAPI(
    title="Shakti Motion Intelligence API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Shakti Motion Intelligence API",
        "status": "running",
    }