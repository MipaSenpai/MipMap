import asyncio
import aiohttp

import multiprocessing as mp


class ChunksSender:
    def __init__(self, config: dict, resultQueue: mp.Queue):
        self.timeout = 5
        self.config = config
        self.resultQueue = resultQueue
        
    async def _sendChunkData(self, session: aiohttp.ClientSession, data: dict) -> None:
        chunkX = data.get("chunkX")
        chunkZ = data.get("chunkZ")
        
        payload = {"chunk": data.get("chunk")}
        
        try:
            async with session.post(self.config.get("mapUrl"), json=payload, timeout=self.timeout) as response:
                if response.status == 200:
                    self.resultQueue.put(("success", chunkX, chunkZ))

                else:
                    errorText = await response.text()
                    self.resultQueue.put(("error", chunkX, chunkZ))

                    print(f"[Mipmap] HTTP error {response.status} for chunk ({chunkX}, {chunkZ}): {errorText}")
                
        except aiohttp.ClientError as e:
            print(f"[Mipmap] Network error sending chunk ({chunkX}, {chunkZ}): {e}")
            self.resultQueue.put(("error", chunkX, chunkZ))
        
        except asyncio.TimeoutError as e:
            print(f"[Mipmap] Timeout sending chunk ({chunkX}, {chunkZ}): {e}")
            self.resultQueue.put(("error", chunkX, chunkZ))
            
    async def run(self, queue: mp.Queue) -> None:
        async with aiohttp.ClientSession() as session:
            while True:
                if not queue.empty():
                    chunkData = queue.get()
                    asyncio.create_task(self._sendChunkData(session, chunkData))
                else:
                    await asyncio.sleep(0.1)
