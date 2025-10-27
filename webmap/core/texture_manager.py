from pathlib import Path
from PIL import Image
from typing import Optional, Dict

class TextureManager:
    def __init__(self, texture_dir: Path):
        self.texture_dir = texture_dir
        self._cache: Dict[str, Image.Image] = {}

    def get_texture(self, block_name: str) -> Optional[Image.Image]:
        if block_name in self._cache:
            return self._cache[block_name]

        for name in [f"{block_name}_top", block_name]:
            path = self.texture_dir / f"{name}.png"
            if path.exists():
                try:
                    img = Image.open(path).convert("RGBA")
                    self._cache[block_name] = img
                    return img
                except Exception:
                    continue

        self._cache[block_name] = None
        return None
