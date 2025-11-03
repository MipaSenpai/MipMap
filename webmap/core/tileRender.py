from PIL import Image
from pathlib import Path

from core.models import ChunkData, BlockData


class TextureLoader:
    _textureCache = {}
    _texturePath = Path("assets/textures/blocks")
    
    def __init__(self):
        self._texturePath.mkdir(parents=True, exist_ok=True)
    
    def getTexture(self, block: BlockData) -> Image.Image:
        textureName = f"{block.name.removeprefix('minecraft:')}.png"
        textureFile = self._texturePath / textureName
        
        if textureName not in self._textureCache:
            if textureFile.exists():
                try:
                    self._textureCache[textureName] = Image.open(textureFile)
                except Exception as e:
                    self._textureCache[textureName] = self._getFallbackTexture()
            else:
                self._textureCache[textureName] = self._getFallbackTexture()
        
        return self._textureCache.get(textureName)
    
    def _getFallbackTexture(self) -> Image.Image:
        fallbackPath = self._texturePath / "bug.png"

        if fallbackPath.exists():
            return Image.open(fallbackPath)
        else:
            return Image.new("RGBA", (16, 16), (255, 0, 255, 255))


class Tile:
    _tilesPath = Path("assets/tiles/zoom-0")

    def __init__(self):
        self._tileSize = 256
        self._blockSize = 16

        self._textureLoader = TextureLoader()
        self._tilesPath.mkdir(parents=True, exist_ok=True)

    def generateTile(self, chunk: ChunkData) -> None:
        tileMap = {}
        blocks = chunk.blocks

        for block in blocks:
            tileX = (block.x * self._blockSize) // self._tileSize
            tileZ = (block.z * self._blockSize) // self._tileSize
            tileKey = (tileX, tileZ)

            tileBlockX = (block.x * self._blockSize) % self._tileSize
            tileBlockZ = (block.z * self._blockSize) % self._tileSize

            if tileKey not in tileMap:
                tilePath = self._tilesPath / f"({tileX})-({tileZ}).png"
                tileMap[tileKey] = self._loadTile(tilePath)

            texture = self._textureLoader.getTexture(block)
            tileMap[tileKey].paste(texture, (tileBlockX, tileBlockZ))

        self._saveTiles(tileMap)
        print(f"Обработано {len(blocks)} блоков, создано {len(tileMap)} тайлов")

    def _loadTile(self, tilePath: Path) -> Image.Image:
        if tilePath.exists():
            return Image.open(tilePath)
        else:
            return Image.new("RGBA", (self._tileSize, self._tileSize), (0, 0, 0, 0))

    def _saveTiles(self, tileMap: dict) -> None:
        for tileKey, tileImage in tileMap.items():
            tileX, tileZ = tileKey
            tilePath = self._tilesPath / f"({tileX})-({tileZ}).png"
            tileImage.save(tilePath)
            print(f"Сохранен тайл: {tilePath}")