from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.api.main import router
from app.core.db import init_db

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db() # initialize the database on startup
    yield

app = FastAPI(lifespan=lifespan, title="Check API", version="1.0.0")

app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
