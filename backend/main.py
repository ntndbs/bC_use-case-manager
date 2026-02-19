"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.database import get_db, init_db
from api.auth import router as auth_router
from api.transcripts import router as transcripts_router
from api.use_cases import router as use_cases_router
from api.chat import router as chat_router
from api.companies import router as companies_router
from api.industries import router as industries_router

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
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Routers
app.include_router(auth_router, prefix="/api")
app.include_router(transcripts_router, prefix="/api")
app.include_router(use_cases_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(industries_router, prefix="/api")


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint with DB connectivity verification."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        return {"status": "unhealthy", "app": settings.app_name, "db": "unreachable"}
    return {"status": "healthy", "app": settings.app_name, "db": "ok"}