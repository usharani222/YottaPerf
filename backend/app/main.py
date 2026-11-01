from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.models.employee import Role

# Import all API routers
from backend.app.api.auth import router as auth_router
from backend.app.api.employees import router as employees_router
from backend.app.api.cycles import router as cycles_router
from backend.app.api.goals import router as goals_router
from backend.app.api.check_ins import router as checkins_router
from backend.app.api.feedback import router as feedback_router
from backend.app.api.reviews import router as reviews_router
from backend.app.api.development import router as devplan_router
from backend.app.api.anomalies import router as anomalies_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.audit import router as audit_router
from backend.app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup
    Base.metadata.create_all(bind=engine)
    try:
        from alembic import command
        from alembic.config import Config
        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
    except Exception:
        pass
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Employee Performance Management, Goal/OKR, Feedback, and Anomaly Tracking Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development and container networking
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "type": type(exc).__name__}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "HEALTHY", "service": "YottaPerf API", "version": "1.0.0"}


# Register Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(employees_router, prefix=settings.API_V1_STR)
app.include_router(cycles_router, prefix=settings.API_V1_STR)
app.include_router(goals_router, prefix=settings.API_V1_STR)
app.include_router(checkins_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(reviews_router, prefix=settings.API_V1_STR)
app.include_router(devplan_router, prefix=settings.API_V1_STR)
app.include_router(anomalies_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8001, reload=True)
