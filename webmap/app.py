from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config import STATIC_DIR, TEMPLATES_DIR
from core.logging import setupLogging

from api.tiles import router as tilesRouter
from api.chunks import router as chunksRouter, getTileManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    tileManager = getTileManager()
    tileManager.startWorkers()
    yield
    tileManager.stopWorkers()


def createApp() -> FastAPI:
    setupLogging()
    
    app = FastAPI(lifespan=lifespan)
    
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    
    app.include_router(tilesRouter)
    app.include_router(chunksRouter)
    
    @app.get("/")
    async def home(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    return app