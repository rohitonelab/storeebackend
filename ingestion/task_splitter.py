import json
import logging
import uuid
from typing import Dict, List, Any
from datetime import datetime

from config import settings
from batching.batching_service import BatchingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskSplitter:
    def __init__(self, batching_service: BatchingService):
        self.batching_service = batching_service
    
    async def process_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a story and split it into subtasks.
        
        Args:
            story_data: Dictionary containing:
                - user_id: str
                - priority: str ("premium" or "free")
                - story_id: str
                - content: str (the story text)
                - callback_url: str
        
        Returns:
            Dict containing the story_id and list of created task IDs
        """
        story_id = story_data.get("story_id", str(uuid.uuid4()))
        user_id = story_data["user_id"]
        priority = story_data["priority"]
        content = story_data["content"]
        callback_url = story_data["callback_url"]
        
        # Extract scenes from the story
        scenes = self._extract_scenes(content)
        
        # Create tasks for each scene
        task_ids = []
        for scene_idx, scene in enumerate(scenes):
            # Create character generation task
            char_task = await self._create_task(
                task_type="character",
                priority=priority,
                user_id=user_id,
                story_id=story_id,
                scene_idx=scene_idx,
                prompt=scene["character_prompt"],
                callback_url=callback_url
            )
            task_ids.append(char_task["task_id"])
            
            # Create scene generation task
            scene_task = await self._create_task(
                task_type="scene",
                priority=priority,
                user_id=user_id,
                story_id=story_id,
                scene_idx=scene_idx,
                prompt=scene["scene_prompt"],
                callback_url=callback_url
            )
            task_ids.append(scene_task["task_id"])
            
            # Create clip generation task
            clip_task = await self._create_task(
                task_type="clip",
                priority=priority,
                user_id=user_id,
                story_id=story_id,
                scene_idx=scene_idx,
                prompt=scene["animation_prompt"],
                callback_url=callback_url
            )
            task_ids.append(clip_task["task_id"])
        
        return {
            "story_id": story_id,
            "task_ids": task_ids
        }
    
    def _extract_scenes(self, content: str) -> List[Dict[str, str]]:
        """
        Extract scenes from story content.
        This is a placeholder implementation - in reality, you'd want to use
        more sophisticated NLP to extract meaningful scenes and prompts.
        """
        # Simple split by paragraphs for demonstration
        paragraphs = content.split("\n\n")
        scenes = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                scenes.append({
                    "character_prompt": f"Generate character for: {paragraph[:100]}...",
                    "scene_prompt": f"Generate scene for: {paragraph[:100]}...",
                    "animation_prompt": f"Animate scene: {paragraph[:100]}..."
                })
        
        return scenes
    
    async def _create_task(
        self,
        task_type: str,
        priority: str,
        user_id: str,
        story_id: str,
        scene_idx: int,
        prompt: str,
        callback_url: str
    ) -> Dict[str, Any]:
        """Create and queue a new task."""
        task_data = {
            "task_id": str(uuid.uuid4()),
            "user_id": user_id,
            "priority": priority,
            "task_type": task_type,
            "story_id": story_id,
            "scene_idx": scene_idx,
            "prompt": prompt,
            "callback_url": callback_url,
            "timestamp": datetime.utcnow().timestamp()
        }
        
        await self.batching_service.add_task(task_type, priority, task_data)
        return task_data

async def process_story(story_data: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for processing a new story."""
    batching_service = BatchingService()
    splitter = TaskSplitter(batching_service)
    return await splitter.process_story(story_data) 