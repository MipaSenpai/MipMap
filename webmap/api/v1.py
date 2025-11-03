# api/v1.py
from fastapi import APIRouter, Response
from core.models import WorldData, Block
from core.texture_manager import TextureManager
from core.tile_renderer import TileRenderer
from core.chunk_storage import (
    update_blocks,
    get_blocks_in_region,
    invalidate_cache_for_blocks
)
from pathlib import Path
from PIL import Image
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

TEXTURE_DIR = Path("assets/textures/blocks")
texture_manager = TextureManager(TEXTURE_DIR)
tile_renderer = TileRenderer(texture_manager)

TILE_CACHE_DIR = Path("data/tile_cache")
TILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Диапазон поддерживаемых уровней zoom
MIN_ZOOM = 1
MAX_ZOOM = 5

@router.post("/worlds")
async def update_world(data: WorldData):
    block_tuples = [
        (b.coordinates[0], b.coordinates[1], b.coordinates[2], b.name)
        for b in data.blocks
    ]
    await update_blocks("overworld", block_tuples)
    invalidate_cache_for_blocks(block_tuples)  # Точечная очистка кэша
    return {"status": "ok", "updated": len(block_tuples)}

@router.get("/tiles/{z}/{x}/{y}.webp")
async def get_tile(z: int, x: int, y: int):
    # Проверка допустимого zoom
    if z < MIN_ZOOM or z > MAX_ZOOM:
        return Response(status_code=404)

    cache_file = TILE_CACHE_DIR / str(z) / str(x) / f"{y}.webp"

    # Если кэш существует — используем его
    if cache_file.exists():
        # Открываем файл и отправляем с заголовками, запрещающими браузерный кэш
        try:
            with open(cache_file, "rb") as f:
                image_data = f.read()
            return Response(
                content=image_data,
                media_type="image/webp",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )
        except Exception:
            logger.exception("Error reading cached tile")
            pass  # Переходим к генерации

    # Генерация тайла
    try:
        scale = 2 ** z  # пикселей на блок
        tile_size = 256

        # Пиксельные границы тайла в мировой системе
        px_min = x * tile_size
        pz_min = y * tile_size
        px_max = px_min + tile_size
        pz_max = pz_min + tile_size

        # Преобразуем в блоковые координаты
        x_min = int(px_min // scale)
        x_max = int(px_max // scale) + 1
        z_min = int(pz_min // scale)
        z_max = int(pz_max // scale) + 1

        # Загружаем блоки из нужного региона
        raw_blocks = await get_blocks_in_region("overworld", x_min, x_max, z_min, z_max)

        # Создаём изображение
        if not raw_blocks:
            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        else:
            blocks = [Block(coordinates=(x, y, z), name=name) for (x, y, z, name) in raw_blocks]
            img = tile_renderer.render_tile(blocks, tile_x=x, tile_y=y, zoom=z)

        # Сохраняем в кэш
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        img.save(cache_file, format="WEBP", lossless=True)

        # Отправляем с заголовками без кэширования
        with open(cache_file, "rb") as f:
            image_data = f.read()

        return Response(
            content=image_data,
            media_type="image/webp",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )

    except Exception:
        logger.exception("Tile render error")
        return Response(status_code=500, content="Render failed")
