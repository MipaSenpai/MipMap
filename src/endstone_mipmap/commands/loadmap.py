import math

from typing import List, Tuple

from endstone.command import Command, CommandSender, CommandExecutor
from endstone.plugin import Plugin


class MapLoader():
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.isLoading = False

        self.messages: dict = self.plugin.config.get("messages", {})
        self.areasQueue: List[Tuple[int, int, int, int, str]] = []

        self.batchId = 0
        self.totalBatches = 0
        self.completedBatches = 0
        
    def startLoading(self, minX: int, minZ: int, maxX: int, maxZ: int, batchSize: int, maxAreas: int) -> None:
        if self.isLoading:
            self.plugin.logger.warning(self.messages.get("mapLoadingAlreadyRunning"))
            return
        
        self.isLoading = True
        self.areasQueue = []
        self.maxAreas = maxAreas
        self.completedBatches = 0
        
        areaCount = 0
        for x in range(minX, maxX, batchSize):
            for z in range(minZ, maxZ, batchSize):
                endX = min(x + batchSize, maxX)
                endZ = min(z + batchSize, maxZ)

                areaId = f"loadmap-{areaCount}"

                self.areasQueue.append((x, z, endX, endZ, areaId))
                areaCount += 1
        
        self.totalBatches = math.ceil(areaCount / maxAreas)
        
        self.plugin.logger.info(self.messages.get("mapLoadingStartedLog").format(areaCount=areaCount))
        self._nextBatch()

    def _nextBatch(self) -> None:
        if not self.areasQueue:
            self._finishLoading()
            return
        
        batch = []
        for _ in range(min(self.maxAreas, len(self.areasQueue))):
            batch.append(self.areasQueue.pop(0))
        
        self.completedBatches += 1
        batchNum = self.completedBatches
        
        percentage = (batchNum / self.totalBatches * 100) if self.totalBatches > 0 else 0
        
        self.plugin.logger.info(
            self.messages.get("processingBatch").format(
                batchSize=len(batch), 
                remaining=len(self.areasQueue),
                currentBatch=batchNum,
                totalBatches=self.totalBatches,
                percentage=percentage
            )
        )
        
        for x, z, endX, endZ, areaId in batch:
            command = f"tickingarea add {x} 0 {z} {endX} 0 {endZ} {areaId}"
            self.plugin.server.dispatch_command(self.plugin.server.command_sender, command)
        
        self.batchId += 1
        
        self.plugin.batchTracker.startBatch(
            batchId=self.batchId,
            areas=batch,
            onComplete=lambda: self._removeBatch(batch)
        )

    def _removeBatch(self, batch: List[Tuple[int, int, int, int, str]]) -> None:
        for _, _, _, _, areaId in batch:
            command = f"tickingarea remove {areaId}"
            self.plugin.server.dispatch_command(self.plugin.server.command_sender, command)
        
        self.plugin.logger.info(self.messages.get("batchProcessed").format(batchSize=len(batch)))
        
        self.plugin.server.scheduler.run_task(self.plugin, self._nextBatch, 1)

    def _finishLoading(self) -> None:
        self.isLoading = False
        self.plugin.batchTracker.cancelBatch()
        self.plugin.logger.info(self.messages.get("mapLoadingFinished"))


class LoadmapCommand(CommandExecutor):
    def __init__(self, plugin: Plugin):
        super().__init__()
        self.plugin = plugin
        self.mapLoader = MapLoader(plugin)

        self.messages: dict = self.plugin.config.get("messages", {})
        self.config: dict = self.plugin.config

        self.batchSize = self.config.get("mapLoading", {}).get("batchSize", 100)
        self.maxAreas = self.config.get("mapLoading", {}).get("maxAreas", 10)
    
    def clearAreas(self):
        self.plugin.server.dispatch_command(self.plugin.server.command_sender, "tickingarea remove_all")

    def on_command(self, sender: CommandSender, command: Command, args: List[str]) -> bool:                    
        if len(args) == 0:
            self.clearAreas()
            
            defaultArea: dict = self.config.get("mapLoading", {}).get("defaultArea", {})
            
            minX = defaultArea.get("minX")
            minZ = defaultArea.get("minZ")
            maxX = defaultArea.get("maxX")
            maxZ = defaultArea.get("maxZ")
            
            self.mapLoader.startLoading(minX, minZ, maxX, maxZ, self.batchSize, self.maxAreas)
            sender.send_message(self.messages.get("loadingStarted").format(minX=minX, minZ=minZ, maxX=maxX, maxZ=maxZ))
                
        elif args[0].lower() == "status":
            if self.mapLoader.isLoading:
                remaining = len(self.mapLoader.areasQueue)
                sender.send_message(self.messages.get("loadingInProgress").format(remaining=remaining))
            else:
                sender.send_message(self.messages.get("loadingNotRunning"))
                
        elif len(args) == 4:
            self.clearAreas()

            minX, minZ, maxX, maxZ = map(int, args[:4])
            if minX >= maxX or minZ >= maxZ:
                sender.send_message(self.messages.get("invalidCoordinates"))
                return True

            self.mapLoader.startLoading(minX, minZ, maxX, maxZ, self.batchSize, self.maxAreas)
            sender.send_message(self.messages.get("loadingStarted").format(minX=minX, minZ=minZ, maxX=maxX, maxZ=maxZ))
                
        elif args[0].lower() == "help":
            sender.send_message(self.messages.get("helpUsage"))
            sender.send_message(self.messages.get("helpDefault"))
            sender.send_message(self.messages.get("helpCustom"))
            sender.send_message(self.messages.get("helpStatus"))
            sender.send_message(self.messages.get("helpInfo"))
            
        return True