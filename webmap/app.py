from fastapi import FastAPI, HTTPException

from core.models import ChunkRequest
from core.tileRender import Tile


app = FastAPI()


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