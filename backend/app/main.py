import time
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uuid
from backend.app.utils.logger import request_id_ctx_var
from backend.app.config import settings
from backend.app.routes.health import router as health_router
from backend.app.api.v1.router import api_router
from backend.app.utils.logger import logger

# Initialize production-ready FastAPI core gateway
app = FastAPI(
    title="AI SQL Query Agent API",
    description="FastAPI Backend gateway for the AI SQL Query Agent database orchestrator.",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    """Logs system startup parameters and metadata."""
    logger.info(
        f"Initializing API Gateway | Environment: {settings.app_env} | "
        f"Debug Mode: {settings.debug} | Execution Timeout: {settings.query_timeout_seconds}s"
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Returns standardized 400 Bad Request for validation errors."""
    return JSONResponse(
        status_code=400, content={"detail": str(exc), "error_type": "ValidationError"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400, content={"detail": str(exc), "error_type": "ValidationError"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Returns standardized 500 for unhandled exceptions."""
    logger.error(f"Unhandled system error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal system error occurred.",
            "error_type": "InternalError",
        },
    )


@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    """HTTP transaction middleware tracking method metrics, execution delays, and tracing."""
    request_id = str(uuid.uuid4())
    request_id_ctx_var.set(request_id)

    start_time = time.time()
    logger.info(f"HTTP REQUEST: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"HTTP RESPONSE: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Latency: {duration_ms:.2f}ms"
        )
        # Attach tracing header to response
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"HTTP ERROR: {request.method} {request.url.path} | Latency: {duration_ms:.2f}ms | Error: {str(e)}"
        )
        raise


# Register endpoints routers
app.include_router(health_router)
app.include_router(api_router)
