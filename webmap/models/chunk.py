from typing import List, Tuple

from pydantic import BaseModel


class BlockData(BaseModel):
    name: str
    coordinates: Tuple[int, int, int]
    
    @property
    def x(self) -> int:
        return self.coordinates[0]
    
    @property
    def y(self) -> int:
        return self.coordinates[1]
    
    @property
    def z(self) -> int:
        return self.coordinates[2]


class ChunkData(BaseModel):
    dimension: str
    blocks: List[BlockData]


class ChunkRequest(BaseModel):
    chunk: ChunkData