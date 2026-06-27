"""SAOS Controller — Main entry point for all SAOS operations."""
from typing import Dict, Any, Callable, Optional
from saos.router import route_task
from saos.pipeline import execute_pipeline
from saos.memory import get_metrics, get_recent_logs


class SAOSController:
    """Primary controller for SAOS runtime operations."""
    
    def __init__(self, legacy_executor: Optional[Callable] = None):
        self.legacy_executor = legacy_executor or self._default_executor
        self.pre_hooks = []
        self.post_hooks = []
    
    def _default_executor(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Default executor when no legacy bridge is provided."""
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
            self.legacy_executor,
            pre_hooks=self.pre_hooks,
            post_hooks=self.post_hooks
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "status": "operational",
            "metrics": get_metrics(),
            "recent_logs": get_recent_logs(10)
        }
    
    def get_metrics_report(self) -> Dict[str, Any]:
        """Get detailed metrics report."""
        return get_metrics()


# Global controller instance
_controller = None


def initialize(legacy_executor: Optional[Callable] = None) -> SAOSController:
    """Initialize the SAOS controller."""
    global _controller
    _controller = SAOSController(legacy_executor)
    return _controller


def get_controller() -> SAOSController:
    """Get the current controller instance."""
    if _controller is None:
        return initialize()
    return _controller


def handle_request(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function — handle request with current controller."""
    return get_controller().handle_request(input_data)
