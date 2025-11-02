import requests
import multiprocessing as mp

from endstone.plugin import Plugin
from endstone.event import event_handler, ChunkLoadEvent


def sendChunkData(queue: mp.Queue, config: dict) -> None:
    while True:
        chunkData = queue.get()
        try:
            requests.post(config.get("mapUrl"), json=chunkData, timeout=5)
        except Exception as e:
            print(f"Error sending chunk: \n{e}")


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

        self._chunkDataSenderProcess = mp.Process(target=sendChunkData, args=(self._chunksQueue, self.config))
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