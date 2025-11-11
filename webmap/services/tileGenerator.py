from pathlib import Path

from PIL import Image, ImageEnhance

from models.chunk import ChunkData, BlockData


class TextureLoader:
    _texturePath = Path("assets/textures/blocks")
    
    def __init__(self):
        self._textureCache = {}
        self._texturePath.mkdir(parents=True, exist_ok=True)
    
    def getTexture(self, block: BlockData) -> Image.Image:
        textureName = f"{block.name.removeprefix('minecraft:')}.png"
        textureFile = self._texturePath / textureName
        
        if textureName not in self._textureCache:
            if textureFile.exists():
                try:
                    self._textureCache[textureName] = Image.open(textureFile)
                except:
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


class TileRenderer:
    def __init__(self):
        self._tileSize = 256
        self._blockSize = 16
        self._tilesPath = Path("assets/tiles/zoom-4")

        self._textureLoader = TextureLoader()
        self._tilesPath.mkdir(parents=True, exist_ok=True)
        
        self._minHeight = -64
        self._maxHeight = 320
        self._seaLevel = 63

    def generateTile(self, chunk: ChunkData) -> None:
        tileMap = {}
        heightMap = {}
        blockDataMap = {}
        blocks = chunk.blocks

        for block in blocks:
            tileX = (block.x * self._blockSize) // self._tileSize
            tileY = (block.z * self._blockSize) // self._tileSize
            tileKey = (tileX, tileY)

            tileBlockX = (block.x * self._blockSize) % self._tileSize
            tileBlockY = (block.z * self._blockSize) % self._tileSize

            if tileKey not in tileMap:
                tilePath = self._tilesPath / f"({tileX})-({tileY}).png"
                tileMap[tileKey] = self._loadTile(tilePath)
                heightMap[tileKey] = {}
                blockDataMap[tileKey] = {}

            blockKey = (tileBlockX, tileBlockY)
            heightMap[tileKey][blockKey] = block.y
            blockDataMap[tileKey][blockKey] = block

        for tileKey in tileMap.keys():
            for blockKey, block in blockDataMap[tileKey].items():
                texture = self._textureLoader.getTexture(block)
                
                heightTexture = self._applyHeightShading(
                    texture, 
                    block.y, 
                    blockKey,
                    heightMap[tileKey]
                )
                
                tileMap[tileKey].paste(heightTexture, blockKey)

        self._saveTiles(tileMap)

    def _loadTile(self, tilePath: Path) -> Image.Image:
        if tilePath.exists():
            return Image.open(tilePath)
        else:
            return Image.new("RGBA", (self._tileSize, self._tileSize), (0, 0, 0, 0))

    def _applyHeightShading(self, texture: Image.Image, height: int, blockPos: tuple, heightMap: dict) -> Image.Image:
        shadedTexture = texture.copy()
        
        if height < self._seaLevel:
            depth_factor = (self._seaLevel - height) / (self._seaLevel - self._minHeight)
            brightness = 0.3 + (1 - depth_factor) * 0.5
            shadedTexture = self._adjustBrightness(shadedTexture, brightness)
            
            blue_intensity = int(depth_factor * 80)
            shadedTexture = self._addColorTint(shadedTexture, (0, 30, blue_intensity, 40))
            
        elif height < 100:
            brightness = 0.9
            shadedTexture = self._adjustBrightness(shadedTexture, brightness)
            
        elif height < 150:
            brightness = 1.0 + (height - 100) / 50 * 0.2
            shadedTexture = self._adjustBrightness(shadedTexture, brightness)
            
        else:
            mountain_factor = (height - 150) / (self._maxHeight - 150)
            brightness = 1.2 + mountain_factor * 0.3
            shadedTexture = self._adjustBrightness(shadedTexture, brightness)
            
            if height > 200:
                whiteness = min(mountain_factor * 0.4, 0.4)
                white_alpha = int(whiteness * 120)
                shadedTexture = self._addColorTint(shadedTexture, (255, 255, 255, white_alpha))
        
        aoFactor = self._calculateAmbientOcclusion(blockPos, height, heightMap)
        shadedTexture = self._adjustBrightness(shadedTexture, aoFactor)
        
        lightingFactor = self._calculateDirectionalLighting(blockPos, height, heightMap)
        shadedTexture = self._adjustBrightness(shadedTexture, lightingFactor)
        
        if height % 20 == 0 and height > self._minHeight:
            shadedTexture = self._addContourLine(shadedTexture)
        
        return shadedTexture
    
    def _calculateAmbientOcclusion(self, blockPos: tuple, height: int, heightMap: dict) -> float:
        x, y = blockPos
        neighbors = [
            (x - self._blockSize, y),
            (x + self._blockSize, y),
            (x, y - self._blockSize),
            (x, y + self._blockSize),
            (x - self._blockSize, y - self._blockSize),
            (x + self._blockSize, y - self._blockSize),
            (x - self._blockSize, y + self._blockSize),
            (x + self._blockSize, y + self._blockSize),
        ]
        
        occlusion = 0
        validNeighbors = 0
        
        for nx, ny in neighbors:
            if (nx, ny) in heightMap:
                neighborHeight = heightMap[(nx, ny)]
                heightDiff = neighborHeight - height
                
                if heightDiff > 0:
                    occlusion += min(heightDiff / 10.0, 0.15)

                elif heightDiff < 0:
                    occlusion -= min(abs(heightDiff) / 20.0, 0.05)
                
                validNeighbors += 1
        
        if validNeighbors > 0:
            occlusion /= validNeighbors
        
        return max(0.6, min(1.2, 1.0 - occlusion))
    
    def _calculateDirectionalLighting(self, blockPos: tuple, height: int, heightMap: dict) -> float:
        x, y = blockPos
        
        lightDirection = [
            (x - self._blockSize, y - self._blockSize),
            (x - self._blockSize, y),
            (x, y - self._blockSize),
        ]
        
        shadowFactor = 0
        
        for nx, ny in lightDirection:
            if (nx, ny) in heightMap:
                neighborHeight = heightMap[(nx, ny)]
                heightDiff = neighborHeight - height
                
                if heightDiff > 0:
                    shadowFactor += min(heightDiff / 8.0, 0.2)
        
        return max(0.7, 1.0 - shadowFactor / len(lightDirection))
    
    def _addContourLine(self, texture: Image.Image) -> Image.Image:
        contour = Image.new('RGBA', texture.size, (0, 0, 0, 30))
        if texture.mode != 'RGBA':
            texture = texture.convert('RGBA')
        return Image.alpha_composite(texture, contour)
    
    def _adjustBrightness(self, image: Image.Image, factor: float) -> Image.Image:
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    def _addColorTint(self, image: Image.Image, tint_color: tuple) -> Image.Image:
        tint = Image.new('RGBA', image.size, tint_color)
        
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        return Image.alpha_composite(image, tint)
    
    def _saveTiles(self, tileMap: dict) -> None:
        for tileKey, tileImage in tileMap.items():
            tileX, tileY = tileKey
            tilePath = self._tilesPath / f"({tileX})-({tileY}).png"
            tileImage.save(tilePath)