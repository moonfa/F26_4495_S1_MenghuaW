import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .routes import build_router

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OPENBB_PROVIDER = os.getenv("OPENBB_PROVIDER", "yfinance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize OpenBB once on the main thread before request handling.
    from openbb import obb  # noqa: F401
    yield


app = FastAPI(
    title="Investment Research Workbench — Slice 2 — AI Analysis",
    version="0.3.0",
    lifespan=lifespan,
)

app.include_router(build_router(OPENBB_PROVIDER))


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")
