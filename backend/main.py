"""
FastAPI main application entry point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.routers import jobs, search, sources, export, subscriptions
from backend.utils.seed_sources import seed_sources

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_sources()
    yield

app = FastAPI(
    title="Job Intelligence Perú API",
    description="Plataforma de inteligencia de mercado laboral peruano",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Job Intelligence Perú"}
