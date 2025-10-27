from pydantic import BaseModel
from typing import List

class Block(BaseModel):
    x: int
    z: int
    y: int = 0
    block_type: str

class WorldSlice(BaseModel):
    name: str
    blocks: List[Block]
