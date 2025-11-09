from fastapi import APIRouter, HTTPException

from models.chunk import ChunkRequest
from services.tileService import TileQueueManager
from core.logging import getLogger


router = APIRouter(prefix="/api", tags=["chunks"])
logger = getLogger(__name__)


tileManager = TileQueueManager()


@router.post("/chunk-data")
async def receiveChunkData(chunkData: ChunkRequest):
    try:    
        queueSize = tileManager.addTask(chunkData.chunk)
        
        logger.info(f"Task added to queue. Queue size: {queueSize}")

        return {
            "status": "success", 
            "message": "The data has been successfully received and added to the processing queue.",
            "queueSize": queueSize
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data processing error: {str(e)}")


def getTileManager() -> TileQueueManager:
    return tileManager
