import asyncio
import json
import logging
import time
import uuid
from typing import List, Dict, Any
import redis.asyncio as redis
from datetime import datetime

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchingService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.batches: Dict[str, List[Dict[str, Any]]] = {}
        self.batch_timestamps: Dict[str, float] = {}
        
    async def start(self):
        """Start all batching loops concurrently."""
        tasks = []
        for task_type in settings.TASK_TYPES:
            for priority in settings.PRIORITY_LEVELS:
                queue_name = settings.QUEUE_NAMES[task_type][priority]
                tasks.append(self.batch_loop(queue_name))
        
        await asyncio.gather(*tasks)
    
    async def batch_loop(self, queue_name: str):
        """Main batching loop for a specific queue."""
        logger.info(f"Starting batch loop for {queue_name}")
        
        while True:
            try:
                batch = []
                start_time = time.time()
                
                # Try to form a batch
                while len(batch) < settings.BATCH_SIZE:
                    # Check if we've exceeded the timeout
                    if time.time() - start_time > settings.BATCH_TIMEOUT:
                        break
                    
                    # Try to get a task from the queue
                    task_data = await self.redis_client.rpop(queue_name)
                    if task_data:
                        task = json.loads(task_data)
                        batch.append(task)
                    else:
                        # No tasks available, wait a bit
                        await asyncio.sleep(0.1)
                
                # Process the batch if we have any tasks
                if batch:
                    await self.process_batch(queue_name, batch)
                
            except Exception as e:
                logger.error(f"Error in batch loop for {queue_name}: {str(e)}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def process_batch(self, queue_name: str, batch: List[Dict[str, Any]]):
        """Process a batch of tasks by sending it to the GPU service."""
        try:
            batch_id = str(uuid.uuid4())
            logger.info(f"Processing batch {batch_id} with {len(batch)} tasks from {queue_name}")
            
            # TODO: Implement actual GPU service call
            # For now, just log the batch
            for task in batch:
                logger.info(f"Processing task {task['task_id']} in batch {batch_id}")
            
            # Simulate processing time
            await asyncio.sleep(1)
            
            # TODO: Implement callback to notify task completion
            logger.info(f"Completed batch {batch_id}")
            
        except Exception as e:
            logger.error(f"Error processing batch from {queue_name}: {str(e)}")
            # TODO: Implement retry logic or dead letter queue
    
    async def add_task(self, task_type: str, priority: str, task_data: Dict[str, Any]):
        """Add a new task to the appropriate queue."""
        queue_name = settings.QUEUE_NAMES[task_type][priority]
        task_data["timestamp"] = datetime.utcnow().timestamp()
        
        try:
            await self.redis_client.lpush(queue_name, json.dumps(task_data))
            logger.info(f"Added task {task_data['task_id']} to {queue_name}")
        except Exception as e:
            logger.error(f"Error adding task to {queue_name}: {str(e)}")
            raise

async def start_batching_service():
    """Entry point to start the batching service."""
    service = BatchingService()
    await service.start()

if __name__ == "__main__":
    asyncio.run(start_batching_service()) 