from typing import List

from pydantic import BaseModel


class Player(BaseModel):
    name: str
    xuid: str
    skin: str
    skinShape: List[int]
    dimension: str

    x: float
    y: float
    z: float


class PlayersRequest(BaseModel):
    players: List[Player]
