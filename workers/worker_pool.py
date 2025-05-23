import asyncio
import logging
from typing import List, Dict
from workers.agentic_worker import AgenticWorker

logger = logging.getLogger(__name__)

class WorkerPool:
    def __init__(self, num_workers: int = 5, redis_url: str = "redis://localhost:6379"):
        self.num_workers = num_workers
        self.redis_url = redis_url
        self.workers: Dict[str, AgenticWorker] = {}
        self.tasks: List[asyncio.Task] = []
        
    async def start(self):
        """Start all workers in the pool."""
        logger.info(f"Starting worker pool with {self.num_workers} workers")
        
        for i in range(self.num_workers):
            worker_id = f"worker-{i+1}"
            worker = AgenticWorker(worker_id, self.redis_url)
            self.workers[worker_id] = worker
            
            # Start worker in background
            task = asyncio.create_task(worker.run())
            self.tasks.append(task)
            
        logger.info("All workers started successfully")
        
    async def stop(self):
        """Stop all workers in the pool."""
        logger.info("Stopping worker pool")
        
        # Stop all workers
        for worker in self.workers.values():
            await worker.stop()
            
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        # Wait for all tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("Worker pool stopped successfully")
        
    def get_active_workers(self) -> int:
        """Get the number of currently active workers."""
        return len(self.workers)
        
    async def scale_workers(self, new_count: int):
        """Scale the number of workers up or down."""
        current_count = len(self.workers)
        
        if new_count > current_count:
            # Add new workers
            for i in range(current_count, new_count):
                worker_id = f"worker-{i+1}"
                worker = AgenticWorker(worker_id, self.redis_url)
                self.workers[worker_id] = worker
                task = asyncio.create_task(worker.run())
                self.tasks.append(task)
                
        elif new_count < current_count:
            # Remove excess workers
            workers_to_remove = list(self.workers.keys())[new_count:]
            for worker_id in workers_to_remove:
                worker = self.workers.pop(worker_id)
                await worker.stop()
                
        logger.info(f"Scaled worker pool from {current_count} to {new_count} workers") 