from fastapi import APIRouter, HTTPException, Response

from core.config import TILE_CACHE_MAX_AGE, WORLDS_DIR


router = APIRouter(prefix="/api", tags=["tiles"])


@router.get("/tiles/{dimension}/{z}/{x}/{y}")
async def getTile(dimension: str, z: int, x: int, y: int):
    try:
        tilePath = WORLDS_DIR / dimension / "tiles" / f"zoom-{z}" / f"({x})-({y}).png"
        with open(tilePath, "rb") as f:
            tileData = f.read()

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tile not found")
    
    return Response(
        content=tileData,
        media_type="image/png",
        headers={"Cache-Control": f"public, max-age={TILE_CACHE_MAX_AGE}"}
    )
