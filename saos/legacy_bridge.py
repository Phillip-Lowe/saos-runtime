"""SAOS Core Bridge — Connects SAOS to OpenClaw execution layer."""
import json
import os
import subprocess
from typing import Dict, Any
from datetime import datetime

# Path to repo root (where openclaw.mjs lives)
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")

# Path to core OpenClaw source code
CORE_PATH = os.path.join(REPO_ROOT, "core")

# Path to OpenClaw CLI
OPENCLAW_CLI = os.path.join(REPO_ROOT, "openclaw.mjs")


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


def _build_openclaw_prompt(task: Dict[str, Any]) -> str:
    """Build a prompt string for OpenClaw from task payload."""
    agent = task.get("agent", "SOL")
    task_type = task.get("type", "general")
    payload = task.get("payload", {})
    
    # Build context-aware prompt
    prompt_parts = [f"You are SAOS agent {agent}."]
    prompt_parts.append(f"Task type: {task_type}")
    
    if isinstance(payload, dict):
        if "message" in payload:
            prompt_parts.append(f"Message: {payload['message']}")
        if "input" in payload:
            prompt_parts.append(f"Input: {payload['input']}")
        if "query" in payload:
            prompt_parts.append(f"Query: {payload['query']}")
        
        # Add any remaining payload fields
        for key, value in payload.items():
            if key not in ["message", "input", "query"]:
                prompt_parts.append(f"{key}: {value}")
    else:
        prompt_parts.append(f"Payload: {str(payload)}")
    
    return "\n\n".join(prompt_parts)


def run_core(task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a task through the core OpenClaw bridge.
    
    Uses subprocess to invoke OpenClaw CLI with the task payload.
    Correct invocation: node openclaw.mjs agent --agent <id> --message "<prompt>" --json
    """
    agent = task.get("agent", "SOL")
    task_type = task.get("type", "general")
    payload = task.get("payload", {})
    task_id = task.get("task_id", "unknown")
    
    # Build execution context
    execution_context = {
        "agent": agent,
        "task_type": task_type,
        "payload": payload,
        "task_id": task_id,
        "core_path": CORE_PATH,
        "core_cli_exists": os.path.exists(OPENCLAW_CLI),
        "repo_root": REPO_ROOT
    }
    
    # Check if OpenClaw CLI exists
    if not os.path.exists(OPENCLAW_CLI):
        return {
            "status": "executed",
            "mode": "core_bridge_stub",
            "context": execution_context,
            "message": f"Task routed to {agent} for {task_type} — OpenClaw CLI not found at {OPENCLAW_CLI}",
            "task_id": task_id,
            "note": "Core bridge active but OpenClaw needs npm install/build"
        }
    
    # Build prompt for OpenClaw
    prompt = _build_openclaw_prompt(task)
    
    # Correct CLI invocation:
    # node openclaw.mjs agent --agent <id> --message "<prompt>" --json
    try:
        cmd = [
            "node", OPENCLAW_CLI,
            "agent",
            "--agent", agent.lower(),
            "--message", prompt,
            "--json"
        ]
        
        # Execute OpenClaw with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=REPO_ROOT
        )
        
        execution_context["returncode"] = result.returncode
        execution_context["stdout_length"] = len(result.stdout)
        execution_context["stderr_length"] = len(result.stderr)
        
        if result.returncode == 0:
            # Try to parse JSON output
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = result.stdout[:5000]
            
            return {
                "status": "executed",
                "mode": "core_bridge_subprocess",
                "context": execution_context,
                "result": output,
                "task_id": task_id,
                "executed_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "executed",
                "mode": "core_bridge_subprocess_error",
                "context": execution_context,
                "error": result.stderr[:2000],
                "task_id": task_id,
                "note": "OpenClaw returned non-zero exit code"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "executed",
            "mode": "core_bridge_timeout",
            "context": execution_context,
            "error": "OpenClaw execution timed out after 300s",
            "task_id": task_id
        }
    except Exception as e:
        return {
            "status": "executed",
            "mode": "core_bridge_exception",
            "context": execution_context,
            "error": str(e),
            "task_id": task_id
        }


def run_core_stub(task: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback stub execution when OpenClaw is not available."""
    agent = task.get("agent", "SOL")
    task_type = task.get("type", "general")
    
    return {
        "status": "executed",
        "mode": "core_bridge_stub",
        "context": {
            "agent": agent,
            "task_type": task_type,
            "core_path": CORE_PATH,
            "note": "OpenClaw subprocess not available — returning stub"
        },
        "message": f"Task routed to {agent} for {task_type} — stub mode",
        "task_id": task.get("task_id")
    }


def get_core_status() -> Dict[str, Any]:
    """Check if core OpenClaw is available."""
    return {
        "core_path_exists": os.path.exists(CORE_PATH),
        "core_path": CORE_PATH,
        "cli_exists": os.path.exists(OPENCLAW_CLI),
        "cli_path": OPENCLAW_CLI,
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
