from PIL import Image
from typing import List
from .models import Block

TILE_SIZE = 256

class TileRenderer:
    def __init__(self, texture_manager):
        self.tm = texture_manager

    def render_tile(self, blocks: List[Block], tile_x: int, tile_y: int, zoom: int) -> Image.Image:
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        if zoom < 0:
            zoom = 0
        scale = 16 / (2 ** zoom)  # px per block

        for block in blocks:
            px_global = block.x * scale
            pz_global = -block.z * scale

            tile_left = tile_x * TILE_SIZE
            tile_top = tile_y * TILE_SIZE

            px = int(px_global - tile_left)
            pz = int(pz_global - tile_top)

            if not (0 <= px < TILE_SIZE and 0 <= pz < TILE_SIZE):
                continue

            block_px = max(1, int(16 / (2 ** zoom)))
            texture = self.tm.get_texture(block.block_type)

            if texture is None:
                texture = Image.new("RGBA", (block_px, block_px), (255, 0, 255, 128))
            else:
                if texture.size != (block_px, block_px):
                    texture = texture.resize((block_px, block_px), Image.NEAREST)

            img.paste(texture, (px, pz), texture)

            if block.y > 0:
                shadow = Image.new("RGBA", (block_px, block_px), (0, 0, 0, 64))
                offset = min(2, block_px // 4)
                img.paste(shadow, (px + offset, pz + offset), shadow)

        return img
