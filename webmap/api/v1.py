from fastapi import APIRouter, Response
from core.models import WorldSlice
from core.texture_manager import TextureManager
from core.tile_renderer import TileRenderer
from pathlib import Path
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

TEXTURE_DIR = Path("assets/textures/blocks")
texture_manager = TextureManager(TEXTURE_DIR)
tile_renderer = TileRenderer(texture_manager)

worlds = {}

@router.post("/worlds")
async def upload_world(world: WorldSlice):
    world_id = str(uuid.uuid4())
    worlds[world_id] = world.blocks
    return {"world_id": world_id}

@router.get("/tiles/{world_id}/{z}/{x}/{y}.png")
async def get_tile(world_id: str, z: int, x: int, y: int):
    if world_id not in worlds:
        return Response(status_code=404, content="World not found")

    blocks = worlds[world_id]
    try:
        img = tile_renderer.render_tile(blocks, tile_x=x, tile_y=y, zoom=z)
    except Exception:
        logger.exception("Tile render error")
        return Response(status_code=500, content="Render failed")

    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")
