"""Agent monitoring system for schematic extraction tasks.

This module provides a comprehensive monitoring system for tracking multiple
extraction agents, their progress, and ensuring they complete their assigned tasks.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable
from uuid import uuid4


class AgentStatus(str, Enum):
    """Status of an extraction agent."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Priority level for agent tasks."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentTask:
    """Represents a task assigned to an extraction agent."""
    task_id: str
    agent_id: str
    description: str
    task_type: str  # e.g., "page_extraction", "validation", "indexing"
    priority: TaskPriority = TaskPriority.NORMAL
    status: AgentStatus = AgentStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: float = 0.0  # 0.0 to 1.0
    pages_assigned: List[int] = field(default_factory=list)
    pages_completed: List[int] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> AgentTask:
        """Create from dictionary."""
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = AgentStatus(data['status'])
        return cls(**data)


@dataclass
class Agent:
    """Represents an extraction agent."""
    agent_id: str
    name: str
    agent_type: str  # e.g., "gemini_extractor", "validator", "indexer"
    status: AgentStatus = AgentStatus.PENDING
    current_task_id: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    created_at: float = field(default_factory=time.time)
    last_heartbeat: Optional[float] = None
    last_activity: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> Agent:
        """Create from dictionary."""
        data['status'] = AgentStatus(data['status'])
        return cls(**data)


class AgentMonitor:
    """
    Central monitoring system for all extraction agents.
    
    Tracks agent status, task assignments, progress, and ensures
    all agents complete their assigned work.
    """
    
    def __init__(self, persistence_path: Optional[Path] = None):
        """
        Initialize the agent monitor.
        
        Args:
            persistence_path: Path to save/load monitor state
        """
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.lock = threading.Lock()
        self.persistence_path = persistence_path or Path("data/monitor_state.json")
        self.callbacks: List[Callable] = []
        
        # Load existing state if available
        self._load_state()
    
    def register_agent(self, name: str, agent_type: str, metadata: Optional[Dict] = None) -> str:
        """
        Register a new agent with the monitor.
        
        Args:
            name: Human-readable agent name
            agent_type: Type of agent (e.g., "gemini_extractor")
            metadata: Additional agent metadata
        
        Returns:
            agent_id: Unique identifier for the agent
        """
        with self.lock:
            agent_id = str(uuid4())
            agent = Agent(
                agent_id=agent_id,
                name=name,
                agent_type=agent_type,
                metadata=metadata or {}
            )
            self.agents[agent_id] = agent
            self._persist_state()
            self._notify_callbacks("agent_registered", agent=agent)
            return agent_id
    
    def assign_task(self, 
                    agent_id: str,
                    description: str,
                    task_type: str,
                    priority: TaskPriority = TaskPriority.NORMAL,
                    pages: Optional[List[int]] = None,
                    metadata: Optional[Dict] = None) -> str:
        """
        Assign a new task to an agent.
        
        Args:
            agent_id: Agent to assign task to
            description: Task description
            task_type: Type of task
            priority: Task priority
            pages: List of page numbers to process (if applicable)
            metadata: Additional task metadata
        
        Returns:
            task_id: Unique identifier for the task
        """
        with self.lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not registered")
            
            task_id = str(uuid4())
            task = AgentTask(
                task_id=task_id,
                agent_id=agent_id,
                description=description,
                task_type=task_type,
                priority=priority,
                pages_assigned=pages or [],
                metadata=metadata or {}
            )
            self.tasks[task_id] = task
            self._persist_state()
            self._notify_callbacks("task_assigned", task=task)
            return task_id
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, activity: Optional[str] = None):
        """Update an agent's status."""
        with self.lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")
            
            agent = self.agents[agent_id]
            agent.status = status
            agent.last_heartbeat = time.time()
            if activity:
                agent.last_activity = activity
            
            self._persist_state()
            self._notify_callbacks("agent_status_updated", agent=agent)
    
    def update_task_status(self, task_id: str, status: AgentStatus, error: Optional[str] = None):
        """Update a task's status."""
        with self.lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            old_status = task.status
            task.status = status
            
            if status == AgentStatus.RUNNING and not task.started_at:
                task.started_at = time.time()
            elif status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
                task.completed_at = time.time()
                
                # Update agent stats
                agent = self.agents.get(task.agent_id)
                if agent:
                    if status == AgentStatus.COMPLETED:
                        agent.tasks_completed += 1
                    elif status == AgentStatus.FAILED:
                        agent.tasks_failed += 1
            
            if error:
                task.error_message = error
            
            self._persist_state()
            self._notify_callbacks("task_status_updated", task=task, old_status=old_status)
    
    def update_task_progress(self, task_id: str, progress: float, pages_completed: Optional[List[int]] = None):
        """
        Update task progress.
        
        Args:
            task_id: Task identifier
            progress: Progress value between 0.0 and 1.0
            pages_completed: List of completed page numbers
        """
        with self.lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            task.progress = max(0.0, min(1.0, progress))
            
            if pages_completed is not None:
                task.pages_completed = pages_completed
            
            # Auto-update status based on progress
            if task.progress >= 1.0 and task.status == AgentStatus.RUNNING:
                task.status = AgentStatus.COMPLETED
                task.completed_at = time.time()
            
            self._persist_state()
            self._notify_callbacks("task_progress_updated", task=task)
    
    def heartbeat(self, agent_id: str, current_task_id: Optional[str] = None):
        """
        Record an agent heartbeat to show it's still alive.
        
        Args:
            agent_id: Agent identifier
            current_task_id: Current task being worked on
        """
        with self.lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")
            
            agent = self.agents[agent_id]
            agent.last_heartbeat = time.time()
            if current_task_id:
                agent.current_task_id = current_task_id
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent information."""
        with self.lock:
            return self.agents.get(agent_id)
    
    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task information."""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all registered agents."""
        with self.lock:
            return list(self.agents.values())
    
    def get_all_tasks(self, agent_id: Optional[str] = None, status: Optional[AgentStatus] = None) -> List[AgentTask]:
        """
        Get tasks, optionally filtered by agent or status.
        
        Args:
            agent_id: Filter by agent ID
            status: Filter by status
        
        Returns:
            List of matching tasks
        """
        with self.lock:
            tasks = list(self.tasks.values())
            
            if agent_id:
                tasks = [t for t in tasks if t.agent_id == agent_id]
            
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            return tasks
    
    def get_agent_summary(self, agent_id: str) -> dict:
        """Get a summary of an agent's status and tasks."""
        with self.lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return {}
            
            agent_tasks = [t for t in self.tasks.values() if t.agent_id == agent_id]
            
            return {
                "agent": agent.to_dict(),
                "total_tasks": len(agent_tasks),
                "tasks_by_status": {
                    status.value: len([t for t in agent_tasks if t.status == status])
                    for status in AgentStatus
                },
                "current_task": next((t.to_dict() for t in agent_tasks if t.task_id == agent.current_task_id), None),
                "recent_tasks": [t.to_dict() for t in sorted(agent_tasks, key=lambda x: x.created_at, reverse=True)[:5]]
            }
    
    def get_overall_summary(self) -> dict:
        """Get an overall summary of all agents and tasks."""
        with self.lock:
            return {
                "total_agents": len(self.agents),
                "agents_by_status": {
                    status.value: len([a for a in self.agents.values() if a.status == status])
                    for status in AgentStatus
                },
                "total_tasks": len(self.tasks),
                "tasks_by_status": {
                    status.value: len([t for t in self.tasks.values() if t.status == status])
                    for status in AgentStatus
                },
                "overall_progress": self._calculate_overall_progress(),
                "agents": [a.to_dict() for a in self.agents.values()],
                "recent_activity": self._get_recent_activity()
            }
    
    def get_incomplete_tasks(self) -> List[AgentTask]:
        """Get all tasks that are not completed."""
        with self.lock:
            incomplete_statuses = [
                AgentStatus.PENDING,
                AgentStatus.INITIALIZING,
                AgentStatus.RUNNING,
                AgentStatus.PAUSED
            ]
            return [t for t in self.tasks.values() if t.status in incomplete_statuses]
    
    def check_stalled_agents(self, timeout_seconds: float = 300) -> List[str]:
        """
        Check for agents that haven't sent a heartbeat recently.
        
        Args:
            timeout_seconds: Time in seconds before considering an agent stalled
        
        Returns:
            List of stalled agent IDs
        """
        with self.lock:
            current_time = time.time()
            stalled = []
            
            for agent_id, agent in self.agents.items():
                if agent.status == AgentStatus.RUNNING and agent.last_heartbeat:
                    if current_time - agent.last_heartbeat > timeout_seconds:
                        stalled.append(agent_id)
            
            return stalled
    
    def register_callback(self, callback: Callable):
        """Register a callback for monitor events."""
        self.callbacks.append(callback)
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress across all tasks."""
        if not self.tasks:
            return 0.0
        
        total_progress = sum(t.progress for t in self.tasks.values())
        return total_progress / len(self.tasks)
    
    def _get_recent_activity(self, limit: int = 10) -> List[dict]:
        """Get recent activity across all tasks."""
        activities = []
        
        for task in self.tasks.values():
            agent = self.agents.get(task.agent_id)
            agent_name = agent.name if agent else "Unknown"
            
            if task.started_at:
                activities.append({
                    "timestamp": task.started_at,
                    "event": "task_started",
                    "agent": agent_name,
                    "description": task.description
                })
            
            if task.completed_at:
                activities.append({
                    "timestamp": task.completed_at,
                    "event": "task_completed" if task.status == AgentStatus.COMPLETED else "task_failed",
                    "agent": agent_name,
                    "description": task.description
                })
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    def _notify_callbacks(self, event: str, **kwargs):
        """Notify all registered callbacks of an event."""
        for callback in self.callbacks:
            try:
                callback(event, **kwargs)
            except Exception:
                pass  # Don't let callback errors break the monitor
    
    def _persist_state(self):
        """Save current state to disk."""
        if not self.persistence_path:
            return
        
        try:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            
            state = {
                "agents": {aid: agent.to_dict() for aid, agent in self.agents.items()},
                "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
                "saved_at": time.time()
            }
            
            self.persistence_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception:
            pass  # Silent fail on persistence errors
    
    def _load_state(self):
        """Load state from disk if available."""
        if not self.persistence_path or not self.persistence_path.exists():
            return
        
        try:
            state = json.loads(self.persistence_path.read_text(encoding="utf-8"))
            
            self.agents = {
                aid: Agent.from_dict(data)
                for aid, data in state.get("agents", {}).items()
            }
            
            self.tasks = {
                tid: AgentTask.from_dict(data)
                for tid, data in state.get("tasks", {}).items()
            }
        except Exception:
            pass  # Silent fail on load errors


# Global monitor instance
_monitor_instance: Optional[AgentMonitor] = None


def get_monitor(persistence_path: Optional[Path] = None) -> AgentMonitor:
    """Get or create the global monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = AgentMonitor(persistence_path)
    return _monitor_instance
