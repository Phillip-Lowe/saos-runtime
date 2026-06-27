"""SAOS Memory — Task store and event logging."""
from typing import Dict, Any, List, Optional
from datetime import datetime

memory_store = {
    "tasks": {},
    "logs": [],
    "agents": {},
    "metrics": {
        "total_tasks": 0,
        "completed_tasks": 0,
        "failed_tasks": 0
    }
}


def save_task(task: Dict[str, Any]) -> None:
    """Persist a task to memory."""
    memory_store["tasks"][task["task_id"]] = task
    memory_store["metrics"]["total_tasks"] += 1


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a task by ID."""
    return memory_store["tasks"].get(task_id)


def update_task(task_id: str, status: str, result: Any = None, error: str = None) -> bool:
    """Update task status and optionally result/error."""
    task = memory_store["tasks"].get(task_id)
    if not task:
        return False
    
    task["status"] = status
    task["updated_at"] = datetime.utcnow().isoformat()
    
    if result is not None:
        task["result"] = result
    if error is not None:
        task["error"] = error
    
    if status == "completed":
        memory_store["metrics"]["completed_tasks"] += 1
    elif status == "failed":
        memory_store["metrics"]["failed_tasks"] += 1
    
    return True


def log_event(event: Dict[str, Any]) -> None:
    """Log an event with timestamp."""
    event["timestamp"] = datetime.utcnow().isoformat()
    memory_store["logs"].append(event)
    # Keep last 1000 logs
    if len(memory_store["logs"]) > 1000:
        memory_store["logs"] = memory_store["logs"][-1000:]


def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent logs."""
    return memory_store["logs"][-limit:]


def get_agent_tasks(agent: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get tasks for a specific agent, optionally filtered by status."""
    tasks = [
        t for t in memory_store["tasks"].values()
        if t["agent"] == agent
    ]
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    return tasks


def get_metrics() -> Dict[str, Any]:
    """Get system metrics."""
    return memory_store["metrics"].copy()
