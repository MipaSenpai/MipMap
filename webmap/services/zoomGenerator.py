import time

from pathlib import Path
from PIL import Image

from multiprocessing import Process

from core.config import GENERATE_ZOOM_INTERVAL, WORLDS_DIR
from core.logging import getLogger


logger = getLogger(__name__)


def zoomWorker(interval: int):
    generator = ZoomGenerator()
    generator.generateZooms()
    
    while True:
        time.sleep(interval)
        generator.generateZooms()


class ZoomGenerator:
    def __init__(self):
        self._tileSize = 256
        self._baseZoom = 4
        self._minZoom = 0
        self._zoomLevels = 5
        self._dimensions = ["Overworld", "Nether", "TheEnd"]
    
    def generateZooms(self):
        logger.info("Starting zoom generation...")
        
        for dimension in self._dimensions:
            dimensionPath = WORLDS_DIR / dimension / "tiles"
            dimensionPath.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Generating zooms for {dimension}...")
            targetZoom = max(self._minZoom, self._baseZoom - self._zoomLevels + 1)
            
            for zoom in range(self._baseZoom - 1, targetZoom - 1, -1):
                self._generateZoomLevel(zoom, dimensionPath)
        
        logger.info(f"Zoom generation completed ({self._zoomLevels} levels)")
    
    def _generateZoomLevel(self, zoom: int, basePath: Path):
        sourceZoom = zoom + 1
        sourcePath = basePath / f"zoom-{sourceZoom}"
        targetPath = basePath / f"zoom-{zoom}"
        
        sourcePath.mkdir(parents=True, exist_ok=True)
        targetPath.mkdir(parents=True, exist_ok=True)
        
        sourceTiles = list(sourcePath.glob("*.png"))
        tileCoords = set()
        
        for tilePath in sourceTiles:
            name = tilePath.stem
            try:
                x, y = map(lambda s: int(s.strip("()")), name.split(")-("))
                tileCoords.add((x // 2, y // 2))

            except:
                continue
        
        for targetX, targetY in tileCoords:
            self._generateTile(targetX, targetY, zoom, sourcePath, targetPath)
        
        logger.info(f"Generated {len(tileCoords)} tiles for zoom level {zoom}")
    
    def _generateTile(self, x: int, y: int, zoom: int, sourcePath: Path, targetPath: Path):
        targetImage = Image.new("RGBA", (self._tileSize, self._tileSize), (0, 0, 0, 0))
        
        for dx in range(2):
            for dy in range(2):
                sourceX = x * 2 + dx
                sourceY = y * 2 + dy
                sourceTilePath = sourcePath / f"({sourceX})-({sourceY}).png"
                
                if sourceTilePath.exists():
                    try:
                        sourceImage = Image.open(sourceTilePath)
                        resized = sourceImage.resize((self._tileSize // 2, self._tileSize // 2), Image.Resampling.LANCZOS)
                        targetImage.paste(resized, (dx * self._tileSize // 2, dy * self._tileSize // 2))

                    except Exception as e:
                        logger.error(f"Error processing tile {sourceTilePath}: {e}")
        
        if targetImage.getbbox():
            targetTilePath = targetPath / f"({x})-({y}).png"
            targetImage.save(targetTilePath, optimize=True)


class ZoomManager:
    def __init__(self):
        self._process = None
        self._interval = GENERATE_ZOOM_INTERVAL
    
    def start(self):
        if self._process and self._process.is_alive():
            logger.warning("Zoom generation process is already running")
            return
        
        self._process = Process(target=zoomWorker, args=(self._interval,))
        self._process.start()

        logger.info(f"Zoom generation process started (interval: {self._interval}s)")
    
    def stop(self):
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=5)

            if self._process.is_alive():
                self._process.kill()

            logger.info("Zoom generation process stopped")
