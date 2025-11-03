from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path

from core.models import ChunkRequest
from core.tileRender import Tile


app = FastAPI()


WEB_DIR = Path(__file__).parent / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/tiles/{z}/{x}/{y}")
async def getTile(z: int, x: int, y: int):
    try:
        with open(f"assets/tiles/zoom-{z}/({x})-({y}).png", "rb") as f:
            tileData = f.read()

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tile not found")
    
    return Response(
        content=tileData,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"}
    )


@app.post("/api/chunk-data")
async def receiveChunkData(chunkData: ChunkRequest):
    try:
        dimension = chunkData.chunk.dimension
        blocks = chunkData.chunk.blocks
        
        print(f"Получены данные для измерения: {dimension}")
        print(f"Количество блоков: {len(blocks)}")
        
        for block in blocks:
            print(f"Блок: {block.name}, координаты: {block.coordinates}")
        
        Tile().generateTile(chunkData.chunk)

        return {"status": "success", "message": "Данные успешно получены"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обработки данных: {str(e)}")