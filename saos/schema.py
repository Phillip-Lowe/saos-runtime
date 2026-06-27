"""SAOS Task Schema — Task creation and validation."""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional


def create_task(agent: str, task_type: str, payload: Dict[str, Any], 
                priority: str = "normal", parent_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized SAOS task."""
    task = {
        "task_id": str(uuid.uuid4()),
        "agent": agent,
        "type": task_type,
        "status": "pending",
        "payload": payload,
        "priority": priority,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "parent_id": parent_id,
        "result": None,
        "error": None
    }
    return task


def validate_task(task: Dict[str, Any]) -> bool:
    """Validate a task has required fields."""
    required = ["task_id", "agent", "type", "status", "payload"]
    return all(field in task for field in required)


def task_summary(task: Dict[str, Any]) -> str:
    """Human-readable task summary."""
    return f"[{task.get('agent', 'UNKNOWN')}] {task.get('type', 'unknown')} — {task.get('status', 'unknown')}"
