# api/v1.py
from fastapi import APIRouter, Response
from core.models import WorldData
from core.texture_manager import TextureManager
from core.tile_renderer import TileRenderer
from core.chunk_storage import update_blocks, get_blocks_in_region
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

TEXTURE_DIR = Path("assets/textures/blocks")
texture_manager = TextureManager(TEXTURE_DIR)
tile_renderer = TileRenderer(texture_manager)

@router.post("/worlds")
async def update_world(data: WorldData):
    block_tuples = [
        (b.coordinates[0], b.coordinates[1], b.coordinates[2], b.name)
        for b in data.blocks
    ]
    await update_blocks("overworld", block_tuples)
    return {"status": "ok", "updated": len(block_tuples)}

@router.get("/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int):
    try:
        scale = 2 ** z  # zoom=0 → 1px/block, zoom=4 → 16px/block
        tile_size_px = 256

        # Мировые пиксельные границы тайла
        px_min = x * tile_size_px
        pz_min = y * tile_size_px
        px_max = px_min + tile_size_px
        pz_max = pz_min + tile_size_px

        # Переводим в блоковые координаты
        x_min = int(px_min // scale) - 1
        x_max = int(px_max // scale) + 1
        z_min = int(pz_min // scale) - 1
        z_max = int(pz_max // scale) + 1

        # Получаем только нужные блоки
        raw_blocks = await get_blocks_in_region("overworld", x_min, x_max, z_min, z_max)

        if not raw_blocks:
            from PIL import Image
            from io import BytesIO
            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            buf = BytesIO()
            img.save(buf, format="PNG")
            return Response(buf.getvalue(), media_type="image/png")

        from core.models import Block
        blocks = [Block(coordinates=(x, y, z), name=name) for (x, y, z, name) in raw_blocks]

        img = tile_renderer.render_tile(blocks, tile_x=x, tile_y=y, zoom=z)

        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG")
        return Response(buf.getvalue(), media_type="image/png")

    except Exception:
        logger.exception("Tile render error")
        return Response(status_code=500, content="Render failed")
