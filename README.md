# StoreeBackend - Scalable Video Generation Queue System

A high-performance, priority-aware batching queue system for multimodal video generation, optimized for GPU utilization and request latency.

## 🎯 Features

- Priority-based task queuing (Premium/Free tiers)
- Concurrent batching for multiple task types
- Horizontal scaling support
- Fault tolerance and reliability mechanisms
- GPU utilization optimization

## 🏗️ Architecture

The system consists of several key components:

- **Task Splitter**: Parses input stories into subtasks
- **Batching Service**: Forms and manages task batches
- **GPU Worker Interface**: Handles GPU pod communication
- **Queue Management**: Redis-based priority queues
- **Metadata Storage**: PostgreSQL/MongoDB for task tracking

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Redis
- PostgreSQL/MongoDB (optional)
- Kubernetes cluster (for production)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running Locally

```bash
python main.py
```

## 📁 Project Structure

```
agent_backend/
├── ingestion/          # Input parsing, story splitting
├── batching/          # Batching system
├── gpu_workers/       # GPU pod interface
├── db/                # Database models and queue logic
└── utils/             # Shared utilities
```

## 🔧 Configuration

Key configuration parameters in `.env`:

- `REDIS_HOST`: Redis server address
- `REDIS_PORT`: Redis port
- `GPU_SERVICE_URL`: GPU worker service endpoint
- `BATCH_SIZE`: Maximum tasks per batch
- `BATCH_TIMEOUT`: Maximum wait time for batch formation

## 📊 Performance Metrics

- Average processing time per story: ~60s
- Batch formation timeout: 5s
- Priority ratio (Premium:Free): 3:1

## 🔐 Security

- API key authentication
- Secure callback URLs
- Encrypted task payloads

## 📝 License

MIT License