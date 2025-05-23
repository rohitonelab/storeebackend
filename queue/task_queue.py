import redis
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

class StoryQueue:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.paid_queue = "story_queue:paid"
        self.free_queue = "story_queue:free"
        
    async def enqueue_story(self, user_id: str, prompt: str, priority: str = "free") -> str:
        """Add a new story request to the queue."""
        request_id = str(uuid.uuid4())
        story_request = {
            "user_id": user_id,
            "prompt": prompt,
            "priority": priority,
            "request_id": request_id,
            "timestamp": datetime.utcnow().timestamp()
        }
        
        queue_key = self.paid_queue if priority == "paid" else self.free_queue
        self.redis.lpush(queue_key, json.dumps(story_request))
        return request_id
    
    async def get_next_story(self) -> Optional[Dict[str, Any]]:
        """Get the next story request, prioritizing paid users."""
        # Try paid queue first
        story = self.redis.rpop(self.paid_queue)
        if not story:
            # If no paid stories, try free queue
            story = self.redis.rpop(self.free_queue)
        
        return json.loads(story) if story else None
    
    async def get_queue_lengths(self) -> Dict[str, int]:
        """Get the current length of both queues."""
        return {
            "paid": self.redis.llen(self.paid_queue),
            "free": self.redis.llen(self.free_queue)
        } 