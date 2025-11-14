import asyncio
import aiohttp

import multiprocessing as mp


class PlayersSender:
    def __init__(self, config: dict):
        self.timeout = 5
        self.config = config
        
    async def _sendPlayerData(self, session: aiohttp.ClientSession, data: dict) -> None:
        try:
            playersUrl = self.config.get("playersUrl")
            async with session.post(playersUrl, json=data, timeout=self.timeout) as response:
                if response.status != 200:
                    errorText = await response.text()
                    print(f"[Mipmap] HTTP error {response.status} for players data: {errorText}")
                
        except aiohttp.ClientError as e:
            print(f"[Mipmap] Network error sending players data: {e}")
        
        except asyncio.TimeoutError as e:
            print(f"[Mipmap] Timeout sending players data: {e}")
            
    async def run(self, queue: mp.Queue) -> None:
        async with aiohttp.ClientSession() as session:
            while True:
                if not queue.empty():
                    playerData = queue.get()
                    asyncio.create_task(self._sendPlayerData(session, playerData))
                else:
                    await asyncio.sleep(0.1)
