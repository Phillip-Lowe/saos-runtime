"""SAOS Legacy Bridge — Connects SAOS to OpenClaw execution layer."""
import json
import os
from typing import Dict, Any

# Path to legacy OpenClaw code
LEGACY_PATH = os.path.join(os.path.dirname(__file__), "..", "legacy")


def load_legacy_config() -> Dict[str, Any]:
    """Load legacy OpenClaw configuration if available."""
    config_paths = [
        os.path.join(LEGACY_PATH, "config", "openclaw.json"),
        os.path.join(LEGACY_PATH, "src", "config", "openclaw.json"),
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


def run_legacy(task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a task through the legacy OpenClaw bridge.
    
    This is the integration point — currently returns a stub.
    When OpenClaw API is available, this calls into legacy/src execution.
    """
    agent = task.get("agent", "SOL")
    task_type = task.get("type", "general")
    payload = task.get("payload", {})
    
    # Try to load legacy config for context
    legacy_config = load_legacy_config()
    
    # Build execution context
    execution_context = {
        "agent": agent,
        "task_type": task_type,
        "payload": payload,
        "legacy_config_loaded": bool(legacy_config),
        "legacy_path": LEGACY_PATH
    }
    
    # TODO: Integrate with actual OpenClaw execution
    # Options:
    # 1. Import legacy/src modules directly
    # 2. Call OpenClaw CLI subprocess
    # 3. Use OpenClaw API/gateway
    # 4. Spawn isolated subprocess
    
    return {
        "status": "executed",
        "mode": "legacy_bridge_stub",
        "context": execution_context,
        "message": f"Task routed to {agent} for {task_type} — legacy bridge active but not yet integrated",
        "task_id": task.get("task_id")
    }


def get_legacy_status() -> Dict[str, Any]:
    """Check if legacy OpenClaw is available."""
    return {
        "legacy_path_exists": os.path.exists(LEGACY_PATH),
        "legacy_path": LEGACY_PATH,
        "config_loaded": bool(load_legacy_config())
    }


def initialize_legacy_integration() -> bool:
    """Initialize connection to legacy OpenClaw."""
    if not os.path.exists(LEGACY_PATH):
        return False
    
    # Verify legacy structure
    required_dirs = ["src", "packages"]
    for d in required_dirs:
        if not os.path.exists(os.path.join(LEGACY_PATH, d)):
            return False
    
    return True
