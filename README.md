# Story-to-Video Generation System

A system for generating consistent character videos from stories using ComfyUI and MV-Adapter.

## Architecture

The system consists of two main components:

1. **ComfyUI Inference Service**: A Dockerized service for image generation
2. **Agentic Backend**: Python-based agents for story processing and video generation

### Components

- `ReferenceImageAgent`: Handles reference image processing
- `SceneAgent`: Splits stories into scenes
- `ConsistentImageGenerationAgent`: Generates consistent images
- `VideoComposerAgent`: Creates final videos
- `ComfyClient`: Manages ComfyUI API interactions

## Setup

### Prerequisites

- Docker and Docker Compose
- NVIDIA GPU with CUDA support
- Python 3.8+

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd storeebackend
```

2. Create required directories:
```bash
mkdir -p comfyui_service/{workflows,models,outputs,temp}
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the ComfyUI service:
```bash
cd comfyui_service
docker-compose up -d
```

## Usage

1. Initialize the agents:
```python
from MM_StoryAgent.agents import (
    ReferenceImageAgent,
    SceneAgent,
    ConsistentImageGenerationAgent,
    VideoComposerAgent
)

# Initialize agents
ref_agent = ReferenceImageAgent()
scene_agent = SceneAgent()
gen_agent = ConsistentImageGenerationAgent()
video_agent = VideoComposerAgent()
```

2. Process a story:
```python
# Generate or use reference image
ref_image = await ref_agent.process_reference(
    story_id="your_story_id",
    character_prompt="your character description"
)

# Split story into scenes
scenes = scene_agent.split_story(your_story_text)
scene_agent.save_scenes("your_story_id", scenes)

# Generate images
generated_images = await gen_agent.generate_scenes(
    story_id="your_story_id",
    reference_image=ref_image,
    scenes=scenes
)

# Create video
final_video = video_agent.compose_video(
    story_id="your_story_id",
    image_paths=generated_images
)
```

## Directory Structure

```
storeebackend/
├── comfyui_service/
│   ├── docker-compose.yml
│   ├── workflows/
│   │   └── mv_adapter_workflow.json
│   ├── models/
│   ├── outputs/
│   └── temp/
└── MM_StoryAgent/
    ├── agents/
    │   ├── reference_image_agent.py
    │   ├── scene_agent.py
    │   ├── consistent_image_agent.py
    │   └── video_composer_agent.py
    └── comfy_client.py
```

## License

MIT License