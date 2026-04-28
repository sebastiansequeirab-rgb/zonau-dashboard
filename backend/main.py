"""
main.py — FastAPI backend for Zona U dashboard

Endpoints:
  POST /api/scrape   { username, password } → scraped data JSON

In production: also serves the compiled React frontend as static files.
Credentials are NEVER logged or stored — they're used only for the
in-memory Playwright session and discarded immediately after.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import asyncio

from scraper import scrape

# Suppress all request logs that could accidentally capture credentials
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

app = FastAPI(docs_url=None, redoc_url=None)  # disable docs in production

# Allow requests from the React dev server (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

# Thread pool for running synchronous Playwright in async FastAPI
_executor = ThreadPoolExecutor(max_workers=4)


class ScrapeRequest(BaseModel):
    username: str
    password: str


@app.post("/api/scrape")
async def api_scrape(req: ScrapeRequest):
    """
    Receives UCAB credentials, runs Playwright scraper, returns dashboard data.
    Credentials are used only within this request and never persisted.
    """
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña requeridos")

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            _executor,
            scrape,
            req.username,
            req.password,
        )
    except ValueError as e:
        # Login failure (bad credentials)
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al consultar el portal. Intenta de nuevo.")

    return result


# ── Static files (React build) ─────────────────────────────────────────────────
# In production the Dockerfile copies the React build to /app/dist
_dist = os.path.join(os.path.dirname(__file__), "dist")
if os.path.isdir(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="static")
