# Agent Monitoring System Documentation

## Overview

The Agent Monitoring System provides comprehensive tracking and management of extraction agents working on the schematic digitizer repository. It ensures all agents stay on task until completion and provides real-time visibility into the extraction workflow.

## Features

- **Agent Registration**: Track multiple extraction agents
- **Task Management**: Assign and monitor tasks for each agent
- **Progress Tracking**: Real-time progress updates with page-level granularity
- **Status Monitoring**: Track agent and task statuses (pending, running, completed, failed)
- **Heartbeat System**: Detect stalled or unresponsive agents
- **Persistence**: Automatic state saving to survive restarts
- **RESTful API**: Complete API for programmatic access
- **Dashboard UI**: Visual monitoring interface at `/monitor/dashboard`

## Architecture

### Core Components

1. **AgentMonitor**: Central monitoring system that tracks all agents and tasks
2. **Agent**: Represents an extraction agent with metadata and status
3. **AgentTask**: Represents a task assigned to an agent
4. **AgentStatus**: Enumeration of possible statuses (pending, running, completed, failed, etc.)
5. **TaskPriority**: Task priority levels (low, normal, high, critical)

### Data Flow

```
┌─────────────────┐
│  Gemini         │
│  Extractor      │──► Register Agent
└────────┬────────┘
         │
         ├──► Create Task
         │
         ├──► Update Status
         │
         ├──► Update Progress
         │
         ├──► Send Heartbeat
         │
         └──► Complete/Fail
```

## API Endpoints

### Agent Management

#### `GET /monitor/agents`
List all registered agents.

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "...",
      "name": "GeminiExtractor-001",
      "agent_type": "gemini_extractor",
      "status": "running",
      "tasks_completed": 5,
      "tasks_failed": 0
    }
  ],
  "total": 1
}
```

#### `POST /monitor/agents/register`
Register a new agent.

**Parameters:**
- `name` (string): Human-readable agent name
- `agent_type` (string): Type of agent (e.g., "gemini_extractor")
- `metadata` (dict, optional): Additional metadata

**Response:**
```json
{
  "agent_id": "uuid-here",
  "message": "Agent 'name' registered successfully"
}
```

#### `GET /monitor/agents/{agent_id}`
Get detailed information about a specific agent.

#### `PUT /monitor/agents/{agent_id}/status`
Update an agent's status.

**Parameters:**
- `status` (string): New status (pending, running, completed, failed, etc.)
- `activity` (string, optional): Current activity description

#### `POST /monitor/agents/{agent_id}/heartbeat`
Record an agent heartbeat.

**Parameters:**
- `current_task_id` (string, optional): ID of task currently being worked on

### Task Management

#### `GET /monitor/tasks`
List all tasks with optional filtering.

**Parameters:**
- `agent_id` (string, optional): Filter by agent
- `status` (string, optional): Filter by status

#### `GET /monitor/tasks/{task_id}`
Get detailed information about a specific task.

#### `POST /monitor/tasks/assign`
Assign a new task to an agent.

**Parameters:**
- `agent_id` (string): Agent to assign task to
- `description` (string): Task description
- `task_type` (string): Type of task
- `priority` (string): Priority level (low, normal, high, critical)
- `pages` (list[int], optional): List of page numbers to process
- `metadata` (dict, optional): Additional metadata

**Response:**
```json
{
  "task_id": "uuid-here",
  "message": "Task assigned to agent {agent_id}"
}
```

#### `PUT /monitor/tasks/{task_id}/status`
Update a task's status.

**Parameters:**
- `status` (string): New status
- `error` (string, optional): Error message if failed

#### `PUT /monitor/tasks/{task_id}/progress`
Update a task's progress.

**Parameters:**
- `progress` (float): Progress value between 0.0 and 1.0
- `pages_completed` (list[int], optional): List of completed page numbers

### Monitoring

#### `GET /monitor/summary`
Get overall summary of all agents and tasks.

**Response:**
```json
{
  "total_agents": 2,
  "agents_by_status": {
    "running": 1,
    "completed": 1
  },
  "total_tasks": 5,
  "tasks_by_status": {
    "running": 2,
    "completed": 3
  },
  "overall_progress": 0.75,
  "agents": [...],
  "recent_activity": [...]
}
```

#### `GET /monitor/incomplete`
Get all tasks that are not yet completed.

#### `GET /monitor/stalled`
Check for agents that haven't sent a heartbeat recently.

**Parameters:**
- `timeout_seconds` (float): Timeout threshold (default: 300)

#### `GET /monitor/dashboard`
Display visual monitoring dashboard.

## Usage Examples

### Python Integration

```python
from src.digital_twin.agent_monitor import get_monitor, AgentStatus, TaskPriority

# Get monitor instance
monitor = get_monitor()

# Register an agent
agent_id = monitor.register_agent(
    name="My Extractor",
    agent_type="gemini_extractor",
    metadata={"version": "1.0"}
)

# Assign a task
task_id = monitor.assign_task(
    agent_id=agent_id,
    description="Extract pages 1-50",
    task_type="page_extraction",
    priority=TaskPriority.HIGH,
    pages=list(range(1, 51))
)

# Update status
monitor.update_agent_status(agent_id, AgentStatus.RUNNING, "Starting extraction")
monitor.update_task_status(task_id, AgentStatus.RUNNING)

# Report progress
monitor.update_task_progress(task_id, 0.5, pages_completed=list(range(1, 26)))

# Send heartbeat
monitor.heartbeat(agent_id, task_id)

# Complete task
monitor.update_task_progress(task_id, 1.0, pages_completed=list(range(1, 51)))
monitor.update_task_status(task_id, AgentStatus.COMPLETED)
```

### cURL Examples

```bash
# Register an agent
curl -X POST "http://localhost:8000/monitor/agents/register?name=Agent1&agent_type=extractor"

# List all agents
curl http://localhost:8000/monitor/agents

# Assign a task
curl -X POST http://localhost:8000/monitor/tasks/assign \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "...",
    "description": "Extract pages",
    "task_type": "extraction",
    "priority": "high"
  }'

# Update progress
curl -X PUT http://localhost:8000/monitor/tasks/{task_id}/progress \
  -H "Content-Type: application/json" \
  -d '{"progress": 0.75}'

# Get summary
curl http://localhost:8000/monitor/summary
```

## Gemini Integration

The monitoring system is automatically integrated with the Gemini extraction workflow:

1. **Auto-Registration**: Each `GeminiExtractor` instance automatically registers as an agent
2. **Task Creation**: Extraction workflows create tasks automatically
3. **Progress Reporting**: Progress is updated as pages are extracted
4. **Heartbeats**: Sent periodically during extraction
5. **Completion**: Tasks are marked complete/failed automatically

No manual intervention is needed - monitoring works out of the box!

## Dashboard

Access the visual dashboard at: `http://localhost:8000/monitor/dashboard`

Features:
- Real-time statistics
- Agent list with status indicators
- Task list with progress bars
- Auto-refresh every 5 seconds
- Clean, modern UI

## Persistence

The monitoring state is automatically saved to `data/monitor_state.json` and persists across server restarts. This ensures:

- Task history is preserved
- Progress is not lost on crashes
- Long-running extractions can be resumed

## Best Practices

1. **Regular Heartbeats**: Send heartbeats at least every 60 seconds for long-running tasks
2. **Progress Updates**: Update progress after each page or meaningful unit of work
3. **Error Handling**: Always mark tasks as failed with error messages when exceptions occur
4. **Status Transitions**: Follow proper status flow: pending → running → completed/failed
5. **Cleanup**: Consider archiving or deleting very old completed tasks periodically

## Troubleshooting

### Agent appears stalled
Check `/monitor/stalled` endpoint to identify agents that haven't sent heartbeats.

### Task stuck in running state
Ensure the extraction code properly calls `update_task_status` on completion or failure.

### State file corruption
Delete `data/monitor_state.json` to reset. Historical data will be lost.

### Memory concerns
The monitor stores all tasks in memory. For very large extractions (10,000+ tasks), consider periodic cleanup of completed tasks.

## Future Enhancements

Potential improvements:
- Task queue management
- Automatic task retry on failure
- Performance metrics and analytics
- Email/webhook notifications
- Task cancellation support
- Database backend for large-scale deployments
