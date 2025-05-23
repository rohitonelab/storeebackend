from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import asyncio
from datetime import datetime

from ingestion.task_splitter import process_story
from batching.batching_service import BatchingService
from gpu_workers.worker_interface import GPUWorkerInterface
from queue.task_queue import StoryQueue
from workers.worker_pool import WorkerPool

app = FastAPI(title="StoreeBackend", description="Scalable Video Generation Queue System")

# Initialize services
story_queue = StoryQueue()
worker_pool = WorkerPool(num_workers=5)  # Start with 5 workers

class StorySubmission(BaseModel):
    user_id: str
    priority: str
    story_id: Optional[str] = None
    content: str
    callback_url: str

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    gpu_service_healthy: bool
    active_workers: int
    queue_lengths: Dict[str, int]

@app.post("/submit_story")
async def submit_story(story: StorySubmission):
    """Submit a new story for processing."""
    try:
        # Add story to queue
        request_id = await story_queue.enqueue_story(
            user_id=story.user_id,
            prompt=story.content,
            priority=story.priority
        )
        return {"request_id": request_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check the health of the service and its dependencies."""
    gpu_worker = GPUWorkerInterface()
    try:
        gpu_healthy = await gpu_worker.check_health()
        queue_lengths = await story_queue.get_queue_lengths()
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().timestamp(),
            gpu_service_healthy=gpu_healthy,
            active_workers=worker_pool.get_active_workers(),
            queue_lengths=queue_lengths
        )
    finally:
        await gpu_worker.close()

@app.post("/scale_workers/{new_count}")
async def scale_workers(new_count: int):
    """Scale the number of workers up or down."""
    if new_count < 1 or new_count > 20:  # Limit max workers to 20
        raise HTTPException(status_code=400, detail="Worker count must be between 1 and 20")
    await worker_pool.scale_workers(new_count)
    return {"status": "success", "new_worker_count": new_count}

@app.on_event("startup")
async def startup_event():
    """Start the batching service and worker pool on application startup."""
    batching_service = BatchingService()
    asyncio.create_task(batching_service.start())
    await worker_pool.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the worker pool on application shutdown."""
    await worker_pool.stop()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 