# core/tile_renderer.py
from PIL import Image
from typing import List
from core.models import Block

TILE_SIZE = 256

class TileRenderer:
    def __init__(self, texture_manager):
        self.texture_manager = texture_manager

    def render_tile(self, blocks: List[Block], tile_x: int, tile_y: int, zoom: int) -> Image.Image:
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        scale = (2 ** zoom)  # размер блока в пикселях на этом zoom

        # Мировые пиксельные координаты
        tile_world_px_x = tile_x * TILE_SIZE
        tile_world_px_z = tile_y * TILE_SIZE

        for block in blocks:
            x, y_block, z = block.coordinates

            # Позиция блока в пикселях на текущем zoom-уровне
            block_px_x = x * scale
            block_px_z = z * scale

            # Локальные координаты внутри тайла (где рисовать)
            local_x = block_px_x - tile_world_px_x
            local_z = block_px_z - tile_world_px_z

            # Размер текстуры после масштабирования
            draw_size = int(scale)

            # Пропускаем блок, если он не попадает в тайл
            if local_x + draw_size <= 0 or local_x >= TILE_SIZE:
                continue
            if local_z + draw_size <= 0 or local_z >= TILE_SIZE:
                continue

            texture = self.texture_manager.get_texture(block.name)
            if texture is None:
                continue

            # Масштабируем текстуру до нужного размера
            if draw_size != 16:
                # Используем Image.NEAREST для пиксельного (не размытого) масштаба
                scaled_tex = texture.resize((draw_size, draw_size), Image.NEAREST)
            else:
                scaled_tex = texture

            # Обрезаем текстуру, если она выходит за границы тайла
            paste_x = int(local_x)
            paste_y = int(local_z)

            # Опционально: обрезка для безопасности
            crop_x1 = max(0, -paste_x)
            crop_y1 = max(0, -paste_y)
            crop_x2 = draw_size - max(0, paste_x + draw_size - TILE_SIZE)
            crop_y2 = draw_size - max(0, paste_y + draw_size - TILE_SIZE)

            if crop_x1 < crop_x2 and crop_y1 < crop_y2:
                cropped_tex = scaled_tex.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                final_x = max(0, paste_x)
                final_y = max(0, paste_y)
                img.alpha_composite(cropped_tex, (final_x, final_y))

        return img
