from fastapi import APIRouter

from core.config import MAP_SIZE, MAP_UPDATE_INTERVAL, MAP_DEFAULT_WORLD


router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
async def getConfig():
    return {
        "mapSize": MAP_SIZE,
        "updateInterval": MAP_UPDATE_INTERVAL,
        "defaultWorld": MAP_DEFAULT_WORLD,
    }
