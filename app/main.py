"""FastAPI application entry point."""

from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_PORT}")
    print(f"📊 Environment: {settings.APP_ENV}")
    print(f"🌐 Timezone: {settings.TIMEZONE}")

    # Initialize monitoring
    if settings.SENTRY_DSN:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        )
        print("📡 Sentry initialized")

    # Initialize Langfuse
    if settings.LANGFUSE_ENABLED and settings.LANGFUSE_PUBLIC_KEY:
        from langfuse import Langfuse

        try:
            langfuse = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST,
            )
            print("🔍 Langfuse initialized")
        except Exception as e:
            print(f"⚠️  Langfuse initialization failed: {e}")

    yield

    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de Atendimento com IA para Clínica ESPE",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app": settings.APP_NAME,
            "version": "0.1.0",
            "environment": settings.APP_ENV,
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "0.1.0",
        "docs": "/docs",
    }


# API routes (to be implemented)
# app.include_router(health.router, prefix="/api/v1", tags=["health"])
# app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
# app.include_router(internal.router, prefix="/api/v1/internal", tags=["internal"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
    )
