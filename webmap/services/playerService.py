import aiohttp
import aiofiles

import numpy as np

from PIL import Image
from pathlib import Path

from models.player import PlayersRequest, Player
from core.logging import getLogger


logger = getLogger(__name__)


class PlayerManager:
    def __init__(self):
        self._players = []

        self.skinsPath = Path("data/skins")
        self.skinsPath.mkdir(exist_ok=True)

    @property
    def players(self):
        return self._players

    async def _getFacePlayerXuid(self, player: Player) -> str:
        skinPath = self.skinsPath / f"{player.name}.png"
        defaultSkinPath = self.skinsPath / "default.png"

        url = f"https://persona-secondary.franchise.minecraft-services.net/api/v1.0/profile/xuid/{player.xuid}/image/head"

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    
                    async with aiofiles.open(skinPath, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            await file.write(chunk)
                    
                    return str(skinPath)

        except:
            return str(defaultSkinPath)
                    

    async def _getFacePlayer(self, player: Player) -> str:
        skinBytes = bytes.fromhex(player.skin)
        skinArray = np.frombuffer(skinBytes, dtype=np.uint8)
        skinImage = skinArray.reshape(tuple(player.skinShape))
        
        image = Image.fromarray(skinImage)
        width, height = image.size
        
        if width != 64 or height not in (64, 32):
            return await self._getFacePlayerXuid(player)
        
        else:
            skinPath = self.skinsPath / f"{player.name}.png"
            face = image.crop((8, 8, 16, 16))
            face.save(skinPath)
            
            return str(skinPath)
            
    async def updatePlayers(self, playersData: PlayersRequest):
        self._players = [
            {
                "x": player.x,
                "y": player.y,
                "z": player.z,
                "name": player.name,
                "dimension": player.dimension,
                "skin": await self._getFacePlayer(player)
            }
            for player in playersData.players
        ]
