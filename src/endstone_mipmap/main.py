import asyncio
import multiprocessing as mp

from endstone.plugin import Plugin
from endstone.block import BlockFace
from endstone.event import event_handler, ChunkLoadEvent, PlayerJoinEvent, PlayerQuitEvent

from .commands.loadmap import LoadmapCommand
from .core import ChunksSender, PlayersSender, BatchTracker


def startChunkSender(queue: mp.Queue, resultQueue: mp.Queue, config: dict) -> None:
    sender = ChunksSender(config, resultQueue)
    asyncio.run(sender.run(queue))


def startPlayersSender(queue: mp.Queue, config: dict) -> None:
    sender = PlayersSender(config)
    asyncio.run(sender.run(queue))


class Map(Plugin):
    api_version = "0.10"

    commands = {
        "loadmap": {
            "description": "Map loading control",
            "usages": [
                "/loadmap",
                "/loadmap <minX: int> <minZ: int> <maxX: int> <maxZ: int>",
                "/loadmap status",
                "/loadmap help"
            ],
            "aliases": ["lm"],
            "permissions": ["mipmap.command.loadmap"],
        }
    }
    
    permissions = {
        "mipmap.command.loadmap": {
            "description": "Permission for map loading control",
            "default": "console", 
        }
    }

    def on_load(self) -> None:
        self.logger.info("        ___                       ___         ___           ___           ___    ")
        self.logger.info("       /\  \                     /\  \       /\  \         /\  \         /\  \   ")
        self.logger.info("      |::\  \       ___         /::\  \     |::\  \       /::\  \       /::\  \  ")
        self.logger.info("      |:|:\  \     /\__\       /:/\:\__\    |:|:\  \     /:/\:\  \     /:/\:\__\ ")
        self.logger.info("    __|:|\:\  \   /:/__/      /:/ /:/  /  __|:|\:\  \   /:/ /::\  \   /:/ /:/  / ")
        self.logger.info("   /::::|_\:\__\ /::\  \     /:/_/:/  /  /::::|_\:\__\ /:/_/:/\:\__\ /:/_/:/  /  ")
        self.logger.info("   \:\~~\  \/__/ \/\:\  \__  \:\/:/  /   \:\~~\  \/__/ \:\/:/  \/__/ \:\/:/  /   ")
        self.logger.info("    \:\  \          \:\/\__\  \::/__/     \:\  \        \::/__/       \::/__/    ")
        self.logger.info("     \:\  \          \::/  /   \:\  \      \:\  \        \:\  \        \:\  \    ")
        self.logger.info("      \:\__\         /:/  /     \:\__\      \:\__\        \:\__\        \:\__\   ")
        self.logger.info("       \/__/         \/__/       \/__/       \/__/         \/__/         \/__/   ")
        self.logger.info("                                                                                 ")

    def on_enable(self) -> None:
        self.save_default_config()
        self.register_events(self)
        self.get_command("loadmap").executor = LoadmapCommand(self)

        self.batchTracker = BatchTracker(self)

        self._chunksQueue = mp.Queue()
        self._resultQueue = mp.Queue()
        self._playersQueue = mp.Queue()
        
        self._chunkDataSenderProcess = mp.Process(
            target=startChunkSender, 
            args=(self._chunksQueue, self._resultQueue, self.config)
        )
        self._chunkDataSenderProcess.start()
        
        self._scheduleResultProcessing()
        
        self._playerDataSenderProcess = mp.Process(
            target=startPlayersSender,
            args=(self._playersQueue, self.config)
        )
        self._playerDataSenderProcess.start()
        
        self._schedulePlayersUpdate()

    def on_disable(self) -> None:
        if hasattr(self, '_chunkDataSenderProcess'):
            self._chunkDataSenderProcess.terminate()
            self._chunkDataSenderProcess.join(timeout=5)
        
        if hasattr(self, '_playerDataSenderProcess'):
            self._playerDataSenderProcess.terminate()
            self._playerDataSenderProcess.join(timeout=5)

    @event_handler
    def loadChunk(self, event: ChunkLoadEvent):
        chunkData = self._getСhunkData(event)
        
        chunkData["chunkX"] = event.chunk.x
        chunkData["chunkZ"] = event.chunk.z
        
        self._chunksQueue.put(chunkData)
    
    @event_handler
    def onPlayerJoin(self, event: PlayerJoinEvent):
        self._sendPlayers()
    
    @event_handler
    def onPlayerQuit(self, event: PlayerQuitEvent):
        self._sendPlayers()

    def _scheduleResultProcessing(self) -> None:
        self.server.scheduler.run_task(self, self._processResults, 1)
    
    def _processResults(self) -> None:
        while not self._resultQueue.empty():
            try:
                result = self._resultQueue.get_nowait()
                status, chunkX, chunkZ = result
                
                if status == "success":
                    self.batchTracker.chunkProcessed(chunkX, chunkZ)
                    
            except:
                break
        
        self._scheduleResultProcessing()
    
    def _schedulePlayersUpdate(self) -> None:
        self.server.scheduler.run_task(self, self._sendPlayers, delay=100)
    
    def _sendPlayers(self) -> None:
        if not self.config.get("sendPlayers"):
            return
        
        players = []
        
        for player in self.server.online_players:
            skin = player.skin.image
                        
            players.append({
                "name": player.name,
                "skin": skin.tobytes().hex(),
                "skinShape": list(skin.shape),
                "dimension": player.dimension.name,
                "x": player.location.x,
                "y": player.location.y,
                "z": player.location.z
            })
        
        playerData = {"players": players}
        self._playersQueue.put(playerData)
        
        self._schedulePlayersUpdate()

    def _getСhunkData(self, event: ChunkLoadEvent) -> dict:
        world = event.chunk.dimension
        chunkX = event.chunk.x
        chunkZ = event.chunk.z
        
        chunkStartX = chunkX * 16
        chunkStartZ = chunkZ * 16
        chunkEndX = chunkStartX + 16
        chunkEndZ = chunkStartZ + 16

        blocksData = []
        blacklist: dict = self.config.get("blacklist")

        for x in range(chunkStartX, chunkEndX):
            for z in range(chunkStartZ, chunkEndZ):                
                block = world.get_highest_block_at(x, z)
                blockType = block.data.type

                while blockType in blacklist.get("blocks") and block.y > -64:
                    block = block.get_relative(BlockFace.DOWN, 1)
                    blockType = block.data.type

                blocksData.append({
                    "name": blockType,
                    "coordinates": [block.x, block.y, block.z]
                })
        
        chunkData = {
            "chunk": {
                "dimension": world.name,
                "blocks": blocksData
            }
        }

        return chunkData