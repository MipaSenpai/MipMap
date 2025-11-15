import queue

import multiprocessing as mp
from multiprocessing import Queue, Process

from .tileGenerator import TileRenderer


def tileWorker(taskQueue):
    tile = TileRenderer()
    while True:
        try:
            chunk_data: dict = taskQueue.get(timeout=5)
            if chunk_data is None:
                break
                
            tile.generateTile(chunk_data)
            
        except queue.Empty:
            continue


class TileQueueManager:
    def __init__(self, maxWorkers=None):
        self.workers = []
        self.tileQueue = Queue()
        self.maxWorkers = maxWorkers or min(4, mp.cpu_count())
        
    def startWorkers(self):
        for _ in range(self.maxWorkers):
            worker = Process(target=tileWorker, args=(self.tileQueue,))
            worker.start()

            self.workers.append(worker)
    
    def stopWorkers(self):
        for _ in self.workers:
            self.tileQueue.put(None)

        for worker in self.workers:
            worker.join(timeout=10)
            if worker.is_alive():
                worker.terminate()
        
        self.workers.clear()
    
    def addTask(self, chunk_data):
        self.tileQueue.put(chunk_data)
        return self.tileQueue.qsize()