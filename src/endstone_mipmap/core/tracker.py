import threading

from typing import Callable, Optional, Set, Tuple

from endstone.plugin import Plugin


class BatchTracker:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.lock = threading.Lock()
        
        self.batchId: Optional[int] = None
        self.expectedChunks: Set[Tuple[int, int]] = set()
        self.processedChunks: Set[Tuple[int, int]] = set()
        
        self.onBatchComplete: Optional[Callable] = None
        
        self.timeoutTask = None
        
    def startBatch(self, batchId: int, areas: list, onComplete: Callable) -> None:
        with self.lock:
            self.batchId = batchId
            self.expectedChunks.clear()
            self.processedChunks.clear()
            self.onBatchComplete = onComplete
            
            for minX, minZ, maxX, maxZ, _ in areas:
                chunkMinX = minX // 16
                chunkMinZ = minZ // 16
                chunkMaxX = (maxX - 1) // 16
                chunkMaxZ = (maxZ - 1) // 16
                
                for cx in range(chunkMinX, chunkMaxX + 1):
                    for cz in range(chunkMinZ, chunkMaxZ + 1):
                        self.expectedChunks.add((cx, cz))
            
            self.plugin.logger.info(f"Batch {batchId} started. Expected chunks: {len(self.expectedChunks)}")
            
            if self.timeoutTask:
                try:
                    self.plugin.server.scheduler.cancel_task(self.timeoutTask)   
                except:
                    pass

                self.timeoutTask = None
    
    def chunkProcessed(self, chunkX: int, chunkZ: int) -> None:
        with self.lock:
            if self.batchId is None:
                return
            
            chunkCoords = (chunkX, chunkZ)
            
            if chunkCoords in self.expectedChunks:
                self.processedChunks.add(chunkCoords)
                
                progress = len(self.processedChunks)
                total = len(self.expectedChunks)
                percentage = (progress / total * 100) if total > 0 else 0
                
                if progress % max(1, total // 20) == 0 or progress == total:
                    self.plugin.logger.info(
                        f"Batch {self.batchId} progress: "
                        f"{progress}/{total} ({percentage:.1f}%)"
                    )
                
                if progress >= total:
                    self._completeBatch()

            else:
                self.plugin.logger.debug(f"Received chunk ({chunkX}, {chunkZ}) not in current batch {self.batchId}")
    
    def _completeBatch(self) -> None:
        if self.batchId is None:
            return
        
        self.plugin.logger.info(
            f"Batch {self.batchId} completed! "
            f"Processed {len(self.processedChunks)}/{len(self.expectedChunks)} chunks"
        )
        
        if self.timeoutTask:
            try:
                self.plugin.server.scheduler.cancel_task(self.timeoutTask)
            except:
                pass

            self.timeoutTask = None
        
        callback = self.onBatchComplete
        self.batchId = None

        self.expectedChunks.clear()
        self.processedChunks.clear()

        self.onBatchComplete = None
        
        if callback:
            self.plugin.server.scheduler.run_task(self.plugin, callback, 1)
    
    
    def cancelBatch(self) -> None:
        with self.lock:
            if self.timeoutTask:
                try:
                    self.plugin.server.scheduler.cancel_task(self.timeoutTask)
                except:
                    pass
                
                self.timeoutTask = None
            
            self.batchId = None
            self.onBatchComplete = None

            self.expectedChunks.clear()
            self.processedChunks.clear()
