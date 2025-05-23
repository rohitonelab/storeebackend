import logging
import httpx
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUWorkerInterface:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.GPU_SERVICE_URL,
            headers={"Authorization": f"Bearer {settings.GPU_API_KEY}"} if settings.GPU_API_KEY else {}
        )
    
    async def process_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a batch of tasks to the GPU service for processing.
        
        Args:
            batch: List of task dictionaries to process
            
        Returns:
            Dict containing the batch processing results
        """
        try:
            # Prepare the batch payload
            payload = {
                "batch_id": batch[0]["task_id"],  # Use first task ID as batch ID
                "tasks": batch,
                "timestamp": datetime.utcnow().timestamp()
            }
            
            # Send the batch to the GPU service
            response = await self.client.post("/process_batch", json=payload)
            response.raise_for_status()
            
            # Process the results
            results = response.json()
            
            # Send callbacks for each completed task
            await self._send_callbacks(batch, results)
            
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error processing batch: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            raise
    
    async def _send_callbacks(self, batch: List[Dict[str, Any]], results: Dict[str, Any]):
        """Send callback notifications for completed tasks."""
        for task, result in zip(batch, results.get("task_results", [])):
            try:
                callback_url = task["callback_url"]
                callback_data = {
                    "task_id": task["task_id"],
                    "status": "completed",
                    "result": result,
                    "timestamp": datetime.utcnow().timestamp()
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(callback_url, json=callback_data)
                    response.raise_for_status()
                    
            except Exception as e:
                logger.error(f"Error sending callback for task {task['task_id']}: {str(e)}")
                # TODO: Implement retry logic for failed callbacks
    
    async def check_health(self) -> bool:
        """Check if the GPU service is healthy and available."""
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"GPU service health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

async def process_batch(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Entry point for processing a batch of tasks."""
    worker = GPUWorkerInterface()
    try:
        return await worker.process_batch(batch)
    finally:
        await worker.close() 