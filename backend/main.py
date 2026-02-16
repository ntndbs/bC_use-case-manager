"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from db.database import init_db
from api.auth import router as auth_router
from api.transcripts import router as transcripts_router
from api.use_cases import router as use_cases_router
from api.chat import router as chat_router
from api.companies import router as companies_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    print("✅ Database initialized")
    yield
    print("👋 Shutting down")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api")
app.include_router(transcripts_router, prefix="/api")
app.include_router(use_cases_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(companies_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}