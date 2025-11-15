from fastapi import APIRouter, HTTPException, Response
from pathlib import Path

from models.player import PlayersRequest
from services.playerService import PlayerManager
from core.logging import getLogger


logger = getLogger(__name__)
router = APIRouter(prefix="/api", tags=["players"])


playerManager = PlayerManager()


@router.post("/players-data")
async def receivePlayersData(playersData: PlayersRequest):
    playerManager.updatePlayers(playersData)
    return {"status": "success", "message": "Players data received successfully"}


@router.get("/players")
async def getPlayersData():
    return {"status": "success", "players": playerManager.players}


@router.get("/players/{player_name}/skin.png")
async def getPlayerSkin(player_name: str):
    try:
        skinPath = Path("data/skins") / f"{player_name}.png"
        if not skinPath.exists():
            skinPath = Path("data/skins/default.png")
        
        with open(skinPath, "rb") as f:
            skinData = f.read()
        
        return Response(
            content=skinData,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Skin not found")
