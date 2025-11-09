from fastapi import APIRouter, HTTPException, Response

from core.config import TILE_CACHE_MAX_AGE


router = APIRouter(prefix="/api", tags=["tiles"])


@router.get("/tiles/{z}/{x}/{y}")
async def getTile(z: int, x: int, y: int):
    try:
        with open(f"assets/tiles/zoom-{z}/({x})-({y}).png", "rb") as f:
            tileData = f.read()

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tile not found")
    
    return Response(
        content=tileData,
        media_type="image/png",
        headers={"Cache-Control": f"public, max-age={TILE_CACHE_MAX_AGE}"}
    )
