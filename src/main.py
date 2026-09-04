from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.routers import ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup LLM clients here (e.g., initialize OpenAI library with API keys)
    yield
    # Cleanup logic

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Assistant API",
    version="1.0.0",
    description="Analyzes schedules and provides smart feedback using AI.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
