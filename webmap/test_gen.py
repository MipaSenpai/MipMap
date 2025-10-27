from pathlib import Path
from core.models import WorldSlice, Block
from core.texture_manager import TextureManager
from core.title_render import TitleRender
import math

TEXTURE_DIR = Path("assets/textures/block")
if not TEXTURE_DIR.exists():
    raise FileNotFoundError("Папка не найдена крч")

# init
tm = TextureManager(TEXTURE_DIR)
render = TitleRender(tm)

# === 2. Генерация фигур ===

def make_spiral(center_x: int, center_z: int, turns: int = 3, step: float = 0.5) -> list[Block]:
    blocks = []
    angle = 0.0
    radius = 0.0
    block_id = 0
    block_types = ["grass_block", "dirt", "sand", "stone", "oak_log"]
    while angle < turns * 2 * math.pi:
        x = int(center_x + radius * math.cos(angle))
        z = int(center_z + radius * math.sin(angle))
        y = int(radius / 2)  # высота растёт с радиусом
        block_type = block_types[block_id % len(block_types)]
        blocks.append(Block(x=x, z=z, y=y, block_type=block_type))
        angle += 0.3
        radius += step
        block_id += 1
    return blocks

def make_island(center_x: int, center_z: int, radius: int = 8) -> list[Block]:
    blocks = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            dist = math.sqrt(dx*dx + dz*dz)
            if dist <= radius:
                x, z = center_x + dx, center_z + dz
                if dist <= radius * 0.3:
                    block_type = "water"
                elif dist <= radius * 0.6:
                    block_type = "sand"
                elif dist <= radius * 0.8:
                    block_type = "grass_block"
                else:
                    block_type = "stone"
                y = max(0, int(3 * (1 - dist / radius)))
                blocks.append(Block(x=x, z=z, y=y, block_type=block_type))
    return blocks

# === 3. Сборка мира ===
blocks = []
blocks.extend(make_island(0, 0, radius=10))
blocks.extend(make_spiral(25, 0, turns=4, step=0.7))

world = WorldSlice(name="demo_world", blocks=blocks)

# === 4. Рендеринг тайлов ===
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

for zoom in [0, 1, 2]:
    # Определим границы мира
    xs = [b.x for b in blocks]
    zs = [b.z for b in blocks]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)

    scale = 16 / (2 ** zoom)
    tile_min_x = int((min_x * scale) // 256)
    tile_max_x = int((max_x * scale) // 256)
    tile_min_z = int((min_z * scale) // 256)
    tile_max_z = int((max_z * scale) // 256)

    for tx in range(tile_min_x, tile_max_x + 1):
        for tz in range(tile_min_z, tile_max_z + 1):
            img = render.render_title(blocks, title_x=tx, title_y=tz, zoom=zoom)
            path = output_dir / f"tile_z{zoom}_x{tx}_y{tz}.png"
            img.save(path)
            print(f"✅ Сохранён: {path}")
