# Replace the duplicated FastAPI initialization in the existing app.py with this.
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .routes import build_router

BASE_DIR = Path(__file__).resolve().parent
OPENBB_PROVIDER = os.getenv("OPENBB_PROVIDER", "yfinance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # OpenBB should be initialized once, synchronously, during application startup.
    # This avoids a first-request race when OpenBB builds/loads its extensions.
    from openbb import obb  # noqa: F401

    yield


app = FastAPI(
    title="Investment Research Workbench — AI Analysis",
    version="0.3.0",
    lifespan=lifespan,
)

app.include_router(build_router(OPENBB_PROVIDER))


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")
