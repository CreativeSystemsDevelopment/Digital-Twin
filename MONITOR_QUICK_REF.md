# Agent Monitor - Quick Reference Card

## Quick Start

```bash
# Start the server
uvicorn src.digital_twin.app:app --reload --host 0.0.0.0 --port 8000

# View dashboard
open http://localhost:8000/monitor/dashboard

# Run demo
python examples/monitor_demo.py
```

## Essential Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/monitor/summary` | GET | Overall system status |
| `/monitor/agents` | GET | List all agents |
| `/monitor/tasks` | GET | List all tasks |
| `/monitor/agents/register` | POST | Register new agent |
| `/monitor/tasks/assign` | POST | Assign task to agent |
| `/monitor/tasks/{id}/progress` | PUT | Update progress |
| `/monitor/dashboard` | GET | Visual dashboard |

## Quick Code Examples

### Register an Agent
```python
from src.digital_twin.agent_monitor import get_monitor

monitor = get_monitor()
agent_id = monitor.register_agent("MyAgent", "extractor")
```

### Assign a Task
```python
task_id = monitor.assign_task(
    agent_id,
    "Extract pages 1-50",
    "page_extraction",
    pages=list(range(1, 51))
)
```

### Update Progress
```python
monitor.update_task_progress(task_id, 0.5)  # 50% complete
monitor.heartbeat(agent_id, task_id)        # Still alive
```

### Complete a Task
```python
from src.digital_twin.agent_monitor import AgentStatus

monitor.update_task_progress(task_id, 1.0)
monitor.update_task_status(task_id, AgentStatus.COMPLETED)
```

## Status Values

- `pending` - Not started
- `initializing` - Setting up
- `running` - In progress
- `paused` - Temporarily stopped
- `completed` - Successfully finished
- `failed` - Error occurred
- `cancelled` - Manually stopped

## Priority Levels

- `low` - Background tasks
- `normal` - Standard tasks (default)
- `high` - Important tasks
- `critical` - Urgent tasks

## Using cURL

```bash
# Register agent
curl -X POST "http://localhost:8000/monitor/agents/register?name=Agent1&agent_type=extractor"

# Get summary
curl http://localhost:8000/monitor/summary

# Update progress
curl -X PUT http://localhost:8000/monitor/tasks/{task_id}/progress \
  -H "Content-Type: application/json" \
  -d '{"progress": 0.75}'
```

## Automatic Gemini Integration

The monitoring system automatically tracks Gemini extraction agents:

```python
from src.digital_twin.gemini_service import GeminiExtractor

# This automatically registers with the monitor
extractor = GeminiExtractor()

# Run extraction - progress is tracked automatically
result = extractor.run_sample_extraction(
    schematic_path=...,
    legend_path=...,
    reading_instructions_path=...,
    system_instructions_path=...
)
```

## Monitoring Best Practices

1. **Send heartbeats** every 30-60 seconds for long tasks
2. **Update progress** after each meaningful unit of work
3. **Use proper status flow**: pending → running → completed/failed
4. **Handle errors**: Always mark failed tasks with error messages
5. **Check for stalled agents**: Use `/monitor/stalled` endpoint

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent appears stalled | Check `/monitor/stalled` endpoint |
| Task stuck in running | Ensure code calls `update_task_status` on completion |
| State file corruption | Delete `data/monitor_state.json` to reset |
| Import errors | Run `pip install -e .` to install dependencies |

## More Information

- **Full docs**: See `AGENT_MONITOR_DOCS.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`
- **Demo**: Run `python examples/monitor_demo.py`
- **Dashboard**: http://localhost:8000/monitor/dashboard
