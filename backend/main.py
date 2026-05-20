"""AI 考研数学助教 — Backend Server

A FastAPI application that provides an AI-powered math tutor for 考研数学
(Chinese Graduate Entrance Exam Mathematics), powered by Xiaomi MiMo API.

Usage:
    pip install -r requirements.txt
    python -m backend.main
    # Or: uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import HOST, PORT
from .api.routes import router
from .models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI 考研数学助教",
    description="智能考研数学辅导系统 — 基于小米 MiMo 大模型",
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

# API routes
app.include_router(router)

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
