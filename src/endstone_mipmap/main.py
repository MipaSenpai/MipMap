import asyncio
import multiprocessing as mp

from endstone.plugin import Plugin
from endstone.event import event_handler, ChunkLoadEvent

from .sender import ChunkSender
from .commands.loadmap import LoadmapCommand


def startChunkSender(queue: mp.Queue, config: dict) -> None:
    sender = ChunkSender(config)
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

        self._chunksQueue = mp.Queue()
        self._chunkDataSenderProcess = mp.Process(target=startChunkSender, args=(self._chunksQueue, self.config))
        self._chunkDataSenderProcess.start()

    def on_disable(self) -> None:
        if hasattr(self, '_chunkDataSenderProcess'):
            self._chunkDataSenderProcess.terminate()
            self._chunkDataSenderProcess.join(timeout=5)

    @event_handler
    def loadChunk(self, event: ChunkLoadEvent):
        chunkData = self._getСhunkData(event)
        self._chunksQueue.put(chunkData)

    def _getСhunkData(self, event: ChunkLoadEvent) -> dict:
        world = event.chunk.dimension
        chunkX = event.chunk.x
        chunkZ = event.chunk.z
        
        chunkStartX = chunkX * 16
        chunkStartZ = chunkZ * 16
        chunkEndX = chunkStartX + 16
        chunkEndZ = chunkStartZ + 16

        blocksData = []

        for x in range(chunkStartX, chunkEndX):
            for z in range(chunkStartZ, chunkEndZ):                
                block = world.get_highest_block_at(x, z)
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