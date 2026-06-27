"""SAOS Controller — Main entry point for all SAOS operations."""
from typing import Dict, Any, Callable, Optional
from saos.router import route_task
from saos.pipeline import execute_pipeline
from saos.memory import get_metrics, get_recent_logs


class SAOSController:
    """Primary controller for SAOS runtime operations.
    
    Supports two execution modes:
    - 'runner': Direct LLM call via agent_runner.py (lean, no bootstrap)
    - 'bridge': OpenClaw subprocess via legacy_bridge.py (full context)
    """
    
    def __init__(self, executor: Optional[Callable] = None, mode: str = "runner"):
        self.mode = mode
        if executor:
            self.executor = executor
        elif mode == "runner":
            from saos.agent_runner import run_agent
            self.executor = self._runner_adapter
        elif mode == "bridge":
            from saos.legacy_bridge import run_core
            self.executor = run_core
        else:
            self.executor = self._default_executor
        
        self.pre_hooks = []
        self.post_hooks = []
    
    def _runner_adapter(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt SAOS task to agent_runner call."""
        from saos.agent_runner import run_agent
        agent = task.get("agent", "SOL")
        payload = task.get("payload", {})
        message = ""
        if isinstance(payload, dict):
            message = payload.get("message", payload.get("input", payload.get("query", str(payload))))
        else:
            message = str(payload)
        
        result = run_agent(agent, message)
        
        return {
            "status": "executed",
            "mode": "agent_runner",
            "result": result,
            "task_id": task.get("task_id")
        }
    
    def _default_executor(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Default executor."""
        return {
            "status": "executed",
            "mode": "default",
            "task": task
        }
    
    def register_pre_hook(self, hook: Callable) -> None:
        """Register a pre-execution hook."""
        self.pre_hooks.append(hook)
    
    def register_post_hook(self, hook: Callable) -> None:
        """Register a post-execution hook."""
        self.post_hooks.append(hook)
    
    def handle_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming request — routes, executes, returns result."""
        task = route_task(input_data)
        return execute_pipeline(
            task, 
            self.executor,
            pre_hooks=self.pre_hooks,
            post_hooks=self.post_hooks
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        from saos.agent_runner import check_ollama_status
        return {
            "status": "operational",
            "mode": self.mode,
            "ollama": check_ollama_status() if self.mode == "runner" else None,
            "metrics": get_metrics(),
            "recent_logs": get_recent_logs(10)
        }
    
    def get_metrics_report(self) -> Dict[str, Any]:
        """Get detailed metrics report."""
        return get_metrics()


# Global controller instance
_controller = None


def initialize(executor: Optional[Callable] = None, mode: str = "runner") -> SAOSController:
    """Initialize the SAOS controller.
    
    Args:
        executor: Custom executor function (overrides mode)
        mode: 'runner' for direct LLM, 'bridge' for OpenClaw subprocess
    """
    global _controller
    _controller = SAOSController(executor, mode)
    return _controller


def get_controller() -> SAOSController:
    """Get the current controller instance."""
    if _controller is None:
        return initialize()
    return _controller


def handle_request(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function — handle request with current controller."""
    return get_controller().handle_request(input_data)