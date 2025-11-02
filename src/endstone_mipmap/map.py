import asyncio
import aiohttp
import multiprocessing as mp

from endstone.plugin import Plugin
from endstone.event import event_handler, ChunkLoadEvent


class ErrorSendChunk(Exception):
    pass


class AsyncChunkSender:
    def __init__(self, config: dict):
        self.config = config
        
    async def _sendChunkData(self, session: aiohttp.ClientSession, data: dict) -> None:
        try:
            async with session.post(
                self.config.get("mapUrl"),
                json=data,
                timeout=aiohttp.ClientTimeout(total=5)
                ) as response:

                if response.status != 200:
                    raise ErrorSendChunk(f"HTTP error {response.status} for chunk data")
                
        except Exception as e:
            raise ErrorSendChunk(f"Error sending chunk: {e}")
            
    async def run(self, queue: mp.Queue) -> None:
        async with aiohttp.ClientSession() as session:
            while True:
                if not queue.empty():
                    chunkData = queue.get()
                    asyncio.create_task(self._sendChunkData(session, chunkData))
                else:
                    await asyncio.sleep(0.1)


def startChunkSender(queue: mp.Queue, config: dict) -> None:
    sender = AsyncChunkSender(config)
    asyncio.run(sender.run(queue))


class Map(Plugin):
    api_version = "0.10"
    
    def on_load(self) -> None:
        print("        ___                       ___         ___           ___           ___    ")
        print("       /\  \                     /\  \       /\  \         /\  \         /\  \   ")
        print("      |::\  \       ___         /::\  \     |::\  \       /::\  \       /::\  \  ")
        print("      |:|:\  \     /\__\       /:/\:\__\    |:|:\  \     /:/\:\  \     /:/\:\__\ ")
        print("    __|:|\:\  \   /:/__/      /:/ /:/  /  __|:|\:\  \   /:/ /::\  \   /:/ /:/  / ")
        print("   /::::|_\:\__\ /::\  \     /:/_/:/  /  /::::|_\:\__\ /:/_/:/\:\__\ /:/_/:/  /  ")
        print("   \:\~~\  \/__/ \/\:\  \__  \:\/:/  /   \:\~~\  \/__/ \:\/:/  \/__/ \:\/:/  /   ")
        print("    \:\  \          \:\/\__\  \::/__/     \:\  \        \::/__/       \::/__/    ")
        print("     \:\  \          \::/  /   \:\  \      \:\  \        \:\  \        \:\  \    ")
        print("      \:\__\         /:/  /     \:\__\      \:\__\        \:\__\        \:\__\   ")
        print("       \/__/         \/__/       \/__/       \/__/         \/__/         \/__/   ")
        print("                                                                                 ")

    def on_enable(self) -> None:
        self.save_default_config()
        self.register_events(self)

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