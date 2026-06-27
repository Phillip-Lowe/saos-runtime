"""SAOS Pipeline — Task execution flow with legacy bridge."""
from typing import Dict, Any, Callable, Optional
from saos.memory import save_task, update_task, log_event
from saos.schema import validate_task


def execute_pipeline(task: Dict[str, Any], legacy_executor: Callable,
                     pre_hooks: Optional[list] = None,
                     post_hooks: Optional[list] = None) -> Dict[str, Any]:
    """Execute a task through the SAOS pipeline."""
    
    # Validate task
    if not validate_task(task):
        error_result = {
            "status": "failed",
            "error": "Invalid task structure",
            "task_id": task.get("task_id", "unknown")
        }
        log_event({
            "event": "task_validation_failed",
            "task_id": task.get("task_id", "unknown")
        })
        return error_result
    
    task_id = task["task_id"]
    
    # Pre-execution hooks
    if pre_hooks:
        for hook in pre_hooks:
            try:
                hook(task)
            except Exception as e:
                log_event({
                    "event": "pre_hook_failed",
                    "task_id": task_id,
                    "error": str(e)
                })
    
    # Save task to memory
    save_task(task)
    
    log_event({
        "event": "task_started",
        "task_id": task_id,
        "agent": task["agent"],
        "type": task["type"]
    })
    
    try:
        # Execute through legacy bridge
        result = legacy_executor(task)
        
        # Update task status
        update_task(task_id, "completed", result=result)
        
        log_event({
            "event": "task_completed",
            "task_id": task_id,
            "agent": task["agent"],
            "type": task["type"]
        })
        
        pipeline_result = {
            "status": "completed",
            "task_id": task_id,
            "result": result
        }
        
    except Exception as e:
        error_msg = str(e)
        update_task(task_id, "failed", error=error_msg)
        
        log_event({
            "event": "task_failed",
            "task_id": task_id,
            "agent": task["agent"],
            "type": task["type"],
            "error": error_msg
        })
        
        pipeline_result = {
            "status": "failed",
            "task_id": task_id,
            "error": error_msg
        }
    
    # Post-execution hooks
    if post_hooks:
        for hook in post_hooks:
            try:
                hook(task, pipeline_result)
            except Exception as e:
                log_event({
                    "event": "post_hook_failed",
                    "task_id": task_id,
                    "error": str(e)
                })
    
    return pipeline_result


def batch_execute(tasks: list, legacy_executor: Callable) -> list:
    """Execute multiple tasks in sequence."""
    results = []
    for task in tasks:
        result = execute_pipeline(task, legacy_executor)
        results.append(result)
    return results
