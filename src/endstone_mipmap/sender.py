import asyncio
import aiohttp
import multiprocessing as mp


class ChunkSender:
    def __init__(self, config: dict):
        self.config = config
        
    async def _sendChunkData(self, session: aiohttp.ClientSession, data: dict) -> None:
        try:
            async with session.post(
                self.config.get("mapUrl"),
                json=data,
                timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 5))
            ) as response:

                if response.status != 200:
                    print(f"[Mipmap] HTTP error {response.status} for chunk data")
                
        except aiohttp.ClientError as e:
            print(f"[Mipmap] Network error sending chunk: {e}")
        
        except asyncio.TimeoutError as e:
            print(f"[Mipmap] Timeout sending chunk: {e}")
            
    async def run(self, queue: mp.Queue) -> None:
        async with aiohttp.ClientSession() as session:
            while True:
                if not queue.empty():
                    chunkData = queue.get()
                    asyncio.create_task(self._sendChunkData(session, chunkData))
                else:
                    await asyncio.sleep(0.1)