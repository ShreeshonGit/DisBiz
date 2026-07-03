from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1.brand_routes import router as brand_router_v1
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
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
    failure response structure: {"success": false, "message": "...", "errors": [...]}
    """
    errors = []
    for error in exc.errors():
        # Get path to parameter and make it readable
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Unknown error")
        errors.append(f"Field '{loc}': {msg}")
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation failed.",
            "errors": errors
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Catches HTTPException raised inside endpoints or by FastAPI middlewares.
    """
    detail = exc.detail
    errors = [detail] if isinstance(detail, str) else detail
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": "API request failed.",
            "errors": errors
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
            "errors": [str(exc)]
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
