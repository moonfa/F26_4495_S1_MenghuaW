import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
# Load .env BEFORE importing routes/database: DATABASE_URL may live there.
load_dotenv()

from .routes import build_router
from .step6.routes import router as history_router
BASE_DIR=Path(__file__).resolve().parent
OPENBB_PROVIDER=os.getenv("OPENBB_PROVIDER","yfinance")

@asynccontextmanager
async def lifespan(app:FastAPI):
    from openbb import obb  # noqa: F401
    yield

app=FastAPI(title="Investment Research Workbench — Step 6",version="0.6.0",lifespan=lifespan)
app.include_router(build_router(OPENBB_PROVIDER))
app.include_router(history_router)

@app.get("/")
def home()->FileResponse:
    return FileResponse(BASE_DIR/"static"/"index.html")
