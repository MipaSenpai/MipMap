from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager

from core.config import STATIC_DIR, TEMPLATES_DIR
from core.logging import setupLogging

from api.tiles import router as tilesRouter
from api.chunks import router as chunksRouter, getTileManager
from api.players import router as playersRouter
from api.config import router as configRouter

from services.zoomGenerator import ZoomManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    tileManager = getTileManager()
    tileManager.startWorkers()
    
    zoomManager = ZoomManager()
    zoomManager.start()
    
    yield
    
    tileManager.stopWorkers()
    zoomManager.stop()


def createApp() -> FastAPI:
    setupLogging()
    
    app = FastAPI(lifespan=lifespan)
    
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    
    app.include_router(tilesRouter)
    app.include_router(chunksRouter)
    app.include_router(playersRouter)
    app.include_router(configRouter)
    
    @app.get("/")
    async def home(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    return app