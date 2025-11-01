from pydantic import BaseModel, validator
from typing import List, Tuple

class Block(BaseModel):
    coordinates: Tuple[int, int, int]
    name: str

    @validator('name')
    def normalize_name(cls, v):
        # Убираем "minecraft:" для удобства текстур
        if v.startswith("minecraft:"):
            return v[len("minecraft:"):]
        return v

class WorldData(BaseModel):
    blocks: List[Block]
