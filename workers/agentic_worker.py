import asyncio
import logging
from typing import Dict, Any, List
from queue.task_queue import StoryQueue
from batching.batch_controller import BatchController

logger = logging.getLogger(__name__)

class AgenticWorker:
    def __init__(self, worker_id: str, redis_url: str = "redis://localhost:6379"):
        self.worker_id = worker_id
        self.queue = StoryQueue(redis_url)
        self.batch_controller = BatchController()
        self.is_running = False
        
    async def process_story(self, story_request: Dict[str, Any]) -> None:
        """Process a single story request."""
        try:
            logger.info(f"Worker {self.worker_id} processing story {story_request['request_id']}")
            
            # TODO: Replace with actual MMStoryAgent call
            # For now, we'll create a mock story plan
            story_plan = {
                "scenes": [
                    {
                        "scene_id": i,
                        "description": f"Scene {i} for story {story_request['request_id']}",
                        "characters": ["character1", "character2"],
                        "task_type": "image_generation"
                    }
                    for i in range(1, 13)  # 12 scenes per story
                ]
            }
            
            # Send each scene to the batch controller
            for scene in story_plan["scenes"]:
                await self.batch_controller.add_task(
                    request_id=story_request["request_id"],
                    scene_id=scene["scene_id"],
                    task_type=scene["task_type"],
                    character_ids=scene["characters"],
                    scene_description=scene["description"]
                )
                
            logger.info(f"Worker {self.worker_id} completed story {story_request['request_id']}")
            
        except Exception as e:
            logger.error(f"Error processing story {story_request['request_id']}: {str(e)}")
            # TODO: Implement retry logic or error handling
            
    async def run(self):
        """Main worker loop."""
        self.is_running = True
        logger.info(f"Starting agentic worker {self.worker_id}")
        
        while self.is_running:
            try:
                # Get next story from queue
                story_request = await self.queue.get_next_story()
                
                if story_request:
                    await self.process_story(story_request)
                else:
                    # No stories in queue, wait before checking again
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker {self.worker_id} encountered error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def stop(self):
        """Stop the worker."""
        self.is_running = False
        logger.info(f"Stopping agentic worker {self.worker_id}") 