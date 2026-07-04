import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.brand_routes import router as brand_router_v1
from app.api.v1.scraper_routes import router as scraper_router_v1
from app.api.v1.schedule_routes import router as schedule_router_v1
from app.api.v1.analytics_routes import router as analytics_router_v1
from app.scheduler.scheduler_engine import SchedulerEngine
from app.core.logging_config import setup_memory_logging
from app.utils.monitoring import record_api_request
import uvicorn
import time

from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set up memory logging handler
    setup_memory_logging()
    # Initialize and boot scheduler engine
    scheduler = SchedulerEngine()
    await scheduler.start()
    yield
    # Gracefully terminate loops
    await scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.middleware("http")
async def log_api_latency(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    # Filter out SSE / stream calls from averaging calculations
    if not request.url.path.endswith(("/stream", "/ws", "/logs/stream", "/scheduler/stream")):
        record_api_request(
            path=request.url.path,
            method=request.method,
            duration_ms=duration_ms,
            status_code=response.status_code
        )
    return response

@app.get("/api/v1/openapi.json", include_in_schema=False)
async def get_v1_openapi():
    return app.openapi()

@app.get("/api/v1/docs", include_in_schema=False)
async def get_v1_docs():
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title=app.title + " - API v1 Docs"
    )

@app.get("/api/v1/redoc", include_in_schema=False)
async def get_v1_redoc():
    return get_redoc_html(
        openapi_url="/api/v1/openapi.json",
        title=app.title + " - API v1 Redoc"
    )

# Configure CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register Versioned Routers
app.include_router(brand_router_v1, prefix=settings.API_V1_STR)
app.include_router(scraper_router_v1, prefix=settings.API_V1_STR)
app.include_router(schedule_router_v1, prefix=settings.API_V1_STR)
app.include_router(analytics_router_v1, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ---------------------------------------------------------
# GLOBAL EXCEPTION HANDLERS FOR STANDARD FAILURE FORMAT
# ---------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches Pydantic validation errors and formats them in the standard
    failure response structure: {"success": false, "message": "...", "error_code": "...", "details": {...}}
    """
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Unknown error")
        errors.append(f"Field '{loc}': {msg}")
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation failed.",
            "error_code": "VALIDATION_ERROR",
            "details": {"errors": errors}
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Catches HTTPException raised inside endpoints or by FastAPI middlewares.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "error_code": f"HTTP_{exc.status_code}_ERROR",
            "details": {"status_code": exc.status_code}
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to avoid raw stacktraces in JSON responses.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": {"error": str(exc)}
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
