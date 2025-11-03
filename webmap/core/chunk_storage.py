# core/chunk_storage.py
import msgpack
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Папки
CHUNKS_DIR = Path("data/chunks")
TILE_CACHE_DIR = Path("data/tile_cache")

# Пул для диска
_executor = ThreadPoolExecutor(max_workers=4)

def _get_chunk_path(dimension: str, chunk_x: int, chunk_z: int) -> Path:
    return CHUNKS_DIR / dimension / str(chunk_x) / f"{chunk_z}.msgpack"

def _load_chunk_sync(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"blocks": {}}
    try:
        with open(path, "rb") as f:
            return msgpack.unpackb(f.read(), raw=False)
    except Exception:
        return {"blocks": {}}

def _save_chunk_sync(path: Path, data: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(msgpack.packb(data, use_bin_type=True))

async def get_blocks_in_region(
    dimension: str,
    x_min: int, x_max: int,
    z_min: int, z_max: int
) -> List[Tuple[int, int, int, str]]:
    blocks = []
    min_cx = x_min // 16
    max_cx = x_max // 16
    min_cz = z_min // 16
    max_cz = z_max // 16

    loop = asyncio.get_event_loop()
    for cx in range(min_cx, max_cx + 1):
        for cz in range(min_cz, max_cz + 1):
            path = _get_chunk_path(dimension, cx, cz)
            chunk_data = await loop.run_in_executor(_executor, _load_chunk_sync, path)
            for local_key, name in chunk_data.get("blocks", {}).items():
                lx, y, lz = map(int, local_key.split(","))
                gx = cx * 16 + lx
                gz = cz * 16 + lz
                if x_min <= gx <= x_max and z_min <= gz <= z_max:
                    blocks.append((gx, y, gz, name))
    return blocks

async def update_blocks(dimension: str, blocks: List[Tuple[int, int, int, str]]):
    chunks_to_update: Dict[Tuple[int, int], Dict[str, str]] = {}
    for x, y, z, name in blocks:
        cx = x // 16
        cz = z // 16
        lx = x % 16
        lz = z % 16
        key = (cx, cz)
        if key not in chunks_to_update:
            chunks_to_update[key] = {}
        chunks_to_update[key][f"{lx},{y},{lz}"] = name

    loop = asyncio.get_event_loop()
    for (cx, cz), block_dict in chunks_to_update.items():
        path = _get_chunk_path(dimension, cx, cz)
        current = await loop.run_in_executor(_executor, _load_chunk_sync, path)
        current["blocks"].update(block_dict)
        await loop.run_in_executor(_executor, _save_chunk_sync, path, current)

# ============ НОВОЕ: ТОЧЕЧНАЯ ИНВАЛИДАЦИЯ КЭША ============

def _get_tiles_for_block(x: int, z: int, min_zoom: int = 1, max_zoom: int = 5) -> Set[Tuple[int, int, int]]:
    """
    Возвращает все тайлы (zoom, tx, ty), которые могут отображать блок (x, z).
    Учитывает, что текстура может выходить за границы тайла.
    """
    tiles = set()
    for zoom in range(min_zoom, max_zoom + 1):
        scale = 2 ** zoom  # пикселей на блок
        # Пиксельная позиция блока
        px = x * scale
        pz = z * scale
        # Основной тайл
        base_tx = int(px // 256)
        base_ty = int(pz // 256)
        # Добавляем 3x3 вокруг — на случай выхода текстуры за границы
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                tiles.add((zoom, base_tx + dx, base_ty + dy))
    return tiles

def invalidate_cache_for_blocks(blocks: List[Tuple[int, int, int, str]]):
    """
    Удаляет из кэша ТОЛЬКО тайлы, которые зависят от переданных блоков.
    """
    affected_tiles = set()
    for x, y, z, name in blocks:
        affected_tiles.update(_get_tiles_for_block(x, z))

    for zoom, tx, ty in affected_tiles:
        cache_file = TILE_CACHE_DIR / str(zoom) / str(tx) / f"{ty}.webp"
        if cache_file.exists():
            cache_file.unlink()
