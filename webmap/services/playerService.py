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

    def _getFacePlayer(self, player: Player) -> str:
        defaultSkinPath = self.skinsPath / "default.png"
        
        try:
            skinBytes = bytes.fromhex(player.skin)
            skinArray = np.frombuffer(skinBytes, dtype=np.uint8)
            skinImage = skinArray.reshape(tuple(player.skinShape))
            
            image = Image.fromarray(skinImage)
            width, height = image.size
            
            if width != 64 or height not in (64, 32):
                return str(defaultSkinPath)
            
            skinPath = self.skinsPath / f"{player.name}.png"
            face = image.crop((8, 8, 16, 16))
            face.save(skinPath)
            
            return str(skinPath)
            
        except Exception:
            return str(defaultSkinPath)

    def updatePlayers(self, playersData: PlayersRequest):
        self._players = [
            {
                "x": player.x,
                "y": player.y,
                "z": player.z,
                "name": player.name,
                "dimension": player.dimension,
                "skin": self._getFacePlayer(player)
            }
            for player in playersData.players
        ]
