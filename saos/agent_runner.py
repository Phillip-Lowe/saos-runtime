"""SAOS Agent Runner — Direct LLM execution without OpenClaw bootstrap.

Calls Ollama API directly with minimal context.
No workspace injection, no tool schemas, no 131K token bloat.

Usage:
    from saos.agent_runner import run_agent
    result = run_agent("sol", "Write a Python script to sort a list")
"""
import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from datetime import datetime

# Ollama API endpoint
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Agent model mapping — loaded from agents.json
_AGENTS_CACHE: Optional[Dict[str, Any]] = None


def _load_agents() -> Dict[str, Any]:
    """Load agent definitions from agents.json."""
    global _AGENTS_CACHE
    if _AGENTS_CACHE is not None:
        return _AGENTS_CACHE
    
    agents_path = os.path.join(os.path.dirname(__file__), "agents.json")
    try:
        with open(agents_path, 'r') as f:
            _AGENTS_CACHE = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _AGENTS_CACHE = {}
    return _AGENTS_CACHE


def _get_model_for_agent(agent_id: str) -> str:
    """Get the Ollama model name for an agent."""
    agents = _load_agents()
    agent = agents.get(agent_id.upper(), {})
    model = agent.get("model", "ollama/kimi-k2.6:cloud")
    # Strip "ollama/" prefix for direct API call
    if model.startswith("ollama/"):
        return model[7:]
    return model


def _get_agent_identity(agent_id: str) -> str:
    """Get minimal identity prompt for an agent."""
    agents = _load_agents()
    agent = agents.get(agent_id.upper(), {})
    role = agent.get("role", "executor")
    desc = agent.get("description", "")
    avatar = agent.get("avatar", "🤖")
    
    return f"You are {agent_id.upper()} ({avatar}), a {role}. {desc}"


def _load_agent_context(agent_id: str) -> str:
    """Load agent-specific context file if it exists (max 2000 chars)."""
    context_dir = os.path.join(os.path.dirname(__file__), "context")
    context_file = os.path.join(context_dir, f"{agent_id.lower()}.md")
    
    if os.path.exists(context_file):
        try:
            with open(context_file, 'r') as f:
                content = f.read()
            return content[:2000]  # Hard cap at 2000 chars
        except IOError:
            pass
    return ""


def _call_ollama(model: str, system_prompt: str, user_message: str, 
                 temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
    """Call Ollama API directly."""
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    url = f"{OLLAMA_URL}/api/chat"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        return {
            "error": f"Ollama connection failed: {str(e)}",
            "model": model
        }
    except Exception as e:
        return {
            "error": f"Ollama call failed: {str(e)}",
            "model": model
        }


def run_agent(agent_id: str, message: str, 
              context: Optional[str] = None,
              temperature: float = 0.7,
              max_tokens: int = 2000) -> Dict[str, Any]:
    """Run an agent with minimal context — no OpenClaw bootstrap.
    
    Args:
        agent_id: Agent name (e.g., "sol", "loki", "dooby")
        message: Task message/prompt
        context: Optional additional context string (max 2000 chars)
        temperature: Sampling temperature
        max_tokens: Max response tokens
    
    Returns:
        Dict with status, response, model, timing
    """
    start = datetime.utcnow()
    
    # Get model for this agent
    model = _get_model_for_agent(agent_id)
    
    # Build minimal system prompt (under 3000 chars total)
    system_parts = [_get_agent_identity(agent_id)]
    
    # Load agent context file if exists
    agent_ctx = _load_agent_context(agent_id)
    if agent_ctx:
        system_parts.append(agent_ctx)
    
    # Add caller-provided context
    if context:
        system_parts.append(context[:2000])
    
    # Add output format instruction
    system_parts.append("Respond concisely. If the task requires code, output clean code. If it requires analysis, be direct.")
    
    system_prompt = "\n\n".join(system_parts)
    
    # Call Ollama directly
    result = _call_ollama(model, system_prompt, message, temperature, max_tokens)
    
    elapsed = (datetime.utcnow() - start).total_seconds()
    
    if "error" in result:
        return {
            "status": "failed",
            "agent": agent_id,
            "model": model,
            "error": result["error"],
            "elapsed_seconds": elapsed,
            "timestamp": start.isoformat()
        }
    
    # Extract response text
    response_text = result.get("message", {}).get("content", "")
    
    return {
        "status": "ok",
        "agent": agent_id,
        "model": model,
        "response": response_text,
        "elapsed_seconds": elapsed,
        "timestamp": start.isoformat(),
        "tokens": {
            "input": result.get("prompt_eval_count", 0),
            "output": result.get("eval_count", 0),
            "total": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
        }
    }


def run_agent_structured(agent_id: str, message: str,
                          output_schema: Optional[Dict] = None,
                          context: Optional[str] = None,
                          temperature: float = 0.3) -> Dict[str, Any]:
    """Run an agent and parse structured JSON output.
    
    Forces low temperature for deterministic output.
    """
    schema_instruction = ""
    if output_schema:
        schema_instruction = f"\n\nRespond as valid JSON matching this schema:\n{json.dumps(output_schema, indent=2)}"
    
    result = run_agent(agent_id, message + schema_instruction, context, temperature, 1000)
    
    if result["status"] != "ok":
        return result
    
    # Try to parse JSON from response
    try:
        # Strip markdown code fences if present
        text = result["response"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        if text.startswith("json"):
            text = text[4:]
        
        result["parsed"] = json.loads(text.strip())
        result["structured"] = True
    except (json.JSONDecodeError, IndexError):
        result["structured"] = False
        result["parsed"] = None
    
    return result


def list_available_models() -> list:
    """List models available in Ollama."""
    try:
        url = f"{OLLAMA_URL}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


def check_ollama_status() -> Dict[str, Any]:
    """Check if Ollama is running and available."""
    try:
        url = f"{OLLAMA_URL}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return {
                "status": "online",
                "url": OLLAMA_URL,
                "models": len(data.get("models", [])),
                "model_names": [m.get("name", "") for m in data.get("models", [])][:10]
            }
    except Exception as e:
        return {
            "status": "offline",
            "url": OLLAMA_URL,
            "error": str(e)
        }