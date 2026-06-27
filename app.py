#!/usr/bin/env python3
"""SAOS Runtime v1 — Main Entry Point

Uses agent_runner.py for direct LLM execution.
No OpenClaw bootstrap. No context injection. No tool schema bloat.
"""

import sys
import json
from saos.controller import initialize
from saos.memory import get_metrics, log_event
from saos.agent_runner import check_ollama_status


def main():
    """Main entry point for SAOS Runtime."""
    print("=" * 60)
    print("  SAOS Runtime v1 — Direct LLM Agent Runner")
    print("  No OpenClaw bootstrap — lean context injection")
    print("=" * 60)
    print()
    
    # Check Ollama status
    status = check_ollama_status()
    if status["status"] != "online":
        print(f"❌ Ollama not available: {status.get('error', 'unknown')}")
        print(f"   URL: {status['url']}")
        print("   Start Ollama: ollama serve")
        return 1
    
    print(f"✅ Ollama: {status['url']} ({status['models']} models)")
    print()
    
    # Initialize SAOS controller in runner mode (direct LLM)
    controller = initialize(mode="runner")
    
    log_event({"event": "system_startup", "version": "1.0.0", "mode": "runner"})
    
    # Parse command line or use defaults
    if len(sys.argv) > 1:
        try:
            input_data = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            input_data = {"type": sys.argv[1], "payload": {}}
    else:
        input_data = {
            "type": "general",
            "payload": {"message": "SAOS Runtime v1 initialized — report status"}
        }
    
    print(f"📥 Input: {json.dumps(input_data, indent=2)}")
    print()
    
    # Execute through SAOS
    result = controller.handle_request(input_data)
    
    print(f"📤 Result: {json.dumps(result, indent=2, default=str)}")
    print()
    
    # Show system status
    sys_status = controller.get_status()
    print(f"📊 Metrics: {json.dumps(sys_status['metrics'], indent=2)}")
    print()
    
    # Show recent logs
    print("📝 Recent Events:")
    for log in sys_status["recent_logs"]:
        ts = log.get("timestamp", "?")[11:19] if "timestamp" in log else "?"
        event = log.get("event", "unknown")
        print(f"   [{ts}] {event}")
    
    print()
    print("✅ SAOS Runtime v1 operational — direct LLM mode")
    
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())