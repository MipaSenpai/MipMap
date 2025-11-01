# api/v1.py
from fastapi import APIRouter, Response
from core.models import WorldData, Block
from core.texture_manager import TextureManager
from core.tile_renderer import TileRenderer
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

TEXTURE_DIR = Path("assets/textures/blocks")
texture_manager = TextureManager(TEXTURE_DIR)
tile_renderer = TileRenderer(texture_manager)

# Храним ТОЛЬКО присланные блоки: ключ = (x, y, z), значение = имя блока
known_blocks = {}  # {(x, y, z): "block_name"}

def _blocks_as_list():
    """Преобразует known_blocks в список Block для рендерера."""
    return [
        Block(coordinates=(x, y, z), name=name)
        for (x, y, z), name in known_blocks.items()
    ]

@router.post("/worlds")
async def update_world(data: WorldData):
    """Добавляет или обновляет указанные блоки. Не удаляет старые."""
    for block in data.blocks:
        x, y, z = block.coordinates
        known_blocks[(x, y, z)] = block.name
    return {
        "status": "ok",
        "total_blocks": len(known_blocks),
        "updated": len(data.blocks)
    }

@router.get("/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int):
    if not known_blocks:
        # Возвращаем прозрачный тайл, если нет данных
        from PIL import Image
        from io import BytesIO
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return Response(buf.getvalue(), media_type="image/png")

    try:
        blocks_list = _blocks_as_list()
        img = tile_renderer.render_tile(blocks_list, tile_x=x, tile_y=y, zoom=z)
    except Exception:
        logger.exception("Tile render error")
        return Response(status_code=500, content="Render failed")

    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")
