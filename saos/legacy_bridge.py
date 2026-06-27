"""SAOS Core Bridge — Connects SAOS to OpenClaw execution layer."""
import json
import os
from typing import Dict, Any

# Path to core OpenClaw code
CORE_PATH = os.path.join(os.path.dirname(__file__), "..", "core")


def load_core_config() -> Dict[str, Any]:
    """Load core OpenClaw configuration if available."""
    config_paths = [
        os.path.join(CORE_PATH, "config", "openclaw.json"),
        os.path.join(CORE_PATH, "src", "config", "openclaw.json"),
        os.path.expanduser("~/.openclaw/openclaw.json")
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                continue
    
    return {}


def run_core(task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a task through the core OpenClaw bridge.
    
    This is the integration point — currently returns a stub.
    When OpenClaw API is available, this calls into core/src execution.
    """
    agent = task.get("agent", "SOL")
    task_type = task.get("type", "general")
    payload = task.get("payload", {})
    
    # Try to load core config for context
    core_config = load_core_config()
    
    # Build execution context
    execution_context = {
        "agent": agent,
        "task_type": task_type,
        "payload": payload,
        "core_config_loaded": bool(core_config),
        "core_path": CORE_PATH
    }
    
    # TODO: Integrate with actual OpenClaw execution
    # Options:
    # 1. Import core/src modules directly
    # 2. Call OpenClaw CLI subprocess
    # 3. Use OpenClaw API/gateway
    # 4. Spawn isolated subprocess
    
    return {
        "status": "executed",
        "mode": "core_bridge_stub",
        "context": execution_context,
        "message": f"Task routed to {agent} for {task_type} — core bridge active but not yet integrated",
        "task_id": task.get("task_id")
    }


def get_core_status() -> Dict[str, Any]:
    """Check if core OpenClaw is available."""
    return {
        "core_path_exists": os.path.exists(CORE_PATH),
        "core_path": CORE_PATH,
        "config_loaded": bool(load_core_config())
    }


def initialize_core_integration() -> bool:
    """Initialize connection to core OpenClaw."""
    if not os.path.exists(CORE_PATH):
        return False
    
    # Verify core structure
    required_dirs = ["src", "packages"]
    for d in required_dirs:
        if not os.path.exists(os.path.join(CORE_PATH, d)):
            return False
    
    return True
