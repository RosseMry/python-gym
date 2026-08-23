"""Python Gym backend entrypoint.

Run locally with:

    uv run uvicorn app.main:app --reload
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import exercises, notes, progress
from app.models.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Ensure the SQLite schema exists before serving requests."""
    init_db()
    yield


app = FastAPI(title="Python Gym", version="0.1.0", lifespan=lifespan)

# The frontend runs on a different local port (Vite default 5173),
# so CORS needs to allow it during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercises.router)
app.include_router(progress.router)
app.include_router(notes.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Simple liveness check."""
    return {"status": "ok"}
