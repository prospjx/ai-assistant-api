import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from src.routers import ai

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "handler", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "handler"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup LLM clients here (e.g., initialize OpenAI library with API keys)
    yield
    # Cleanup logic


app = FastAPI(
    title="AI Assistant API",
    version="1.0.0",
    description="Analyzes schedules and provides smart feedback using AI.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception:
        status_code = "500"
        raise
    finally:
        duration = time.time() - start_time
        path = request.url.path
        REQUEST_COUNT.labels(
            method=request.method, handler=path, status=status_code
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, handler=path).observe(duration)
    return response


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(ai.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
