from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Minecraft Map Viewer")

# Подключаем статику и шаблоны
web_dir = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")
templates = Jinja2Templates(directory=web_dir / "templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Подключаем API
from api.v1 import router as api_router
app.include_router(api_router, prefix="/api/v1")
