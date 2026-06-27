"""SAOS Router — Route tasks to appropriate agents based on type."""
from typing import Dict, Any, List, Optional
from saos.schema import create_task

# Agent routing matrix — maps task types to agents
ROUTING_MATRIX = {
    "risk": "PESSI",
    "validation": "VALI",
    "monitoring": "PESSI",
    "code": "DOOBY",
    "architecture": "ASSEMBLY",
    "creative": "GENI",
    "test": "VALI",
    "review": "CODY",
    "messaging": "CHATTY",
    "research": "ATLAS",
    "legal": "JURIS",
    "background": "LOKI",
    "strategy": "SOL",
    "general": "SOL"
}

# Priority override rules
PRIORITY_RULES = {
    "security_incident": "critical",
    "credential_exposure": "critical",
    "production_down": "critical",
    "revenue": "high",
    "client_facing": "high"
}


def determine_agent(task_type: str, payload: Dict[str, Any]) -> str:
    """Determine which agent should handle a task."""
    # Direct routing by task type
    if task_type in ROUTING_MATRIX:
        return ROUTING_MATRIX[task_type]
    
    # Payload inspection for context-based routing
    payload_str = str(payload).lower()
    
    if any(k in payload_str for k in ["security", "secret", "credential", "exposed"]):
        return "PESSI"
    
    if any(k in payload_str for k in ["code", "script", "build", "deploy"]):
        return "DOOBY"
    
    if any(k in payload_str for k in ["design", "image", "frontend", "creative"]):
        return "GENI"
    
    if any(k in payload_str for k in ["test", "qa", "verify", "validate"]):
        return "VALI"
    
    if any(k in payload_str for k in ["message", "email", "notify", "chat"]):
        return "CHATTY"
    
    if any(k in payload_str for k in ["research", "analyze", "discover"]):
        return "ATLAS"
    
    # Default fallback
    return "SOL"


def determine_priority(task_type: str, payload: Dict[str, Any]) -> str:
    """Determine task priority based on type and payload."""
    payload_str = str(payload).lower()
    
    for keyword, priority in PRIORITY_RULES.items():
        if keyword in task_type.lower() or keyword in payload_str:
            return priority
    
    return "normal"


def route_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Route incoming task data to appropriate agent."""
    task_type = input_data.get("type", "general")
    payload = input_data.get("payload", input_data)
    
    agent = determine_agent(task_type, payload)
    priority = determine_priority(task_type, payload)
    
    return create_task(agent, task_type, payload, priority)


def get_routing_matrix() -> Dict[str, str]:
    """Get current routing configuration."""
    return ROUTING_MATRIX.copy()


def update_routing(task_type: str, agent: str) -> None:
    """Update routing rule for a task type."""
    ROUTING_MATRIX[task_type] = agent
