import asyncio
import structlog
from typing import Set

log = structlog.get_logger()

class Broadcaster:
    def __init__(self):
        self.queues: Set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.queues.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue):
        self.queues.remove(queue)

    async def broadcast(self, message: dict):
        if not self.queues:
            return
            
        for queue in self.queues:
            await queue.put(message)
        
        # log.debug("Broadcasted message", subscribers=len(self.queues))

broadcaster = Broadcaster()
