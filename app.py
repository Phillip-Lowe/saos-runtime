#!/usr/bin/env python3
"""SAOS Runtime v1 — Main Entry Point

Replaces OpenClaw entry with SAOS-controlled execution.
SAOS handles all inputs; OpenClaw isolated behind legacy bridge.
"""

import sys
import json
from saos.controller import initialize, handle_request
from saos.legacy_bridge import run_legacy
from saos.memory import get_metrics, log_event


def main():
    """Main entry point for SAOS Runtime."""
    print("=" * 60)
    print("  SAOS Runtime v1 — System Operations Layer")
    print("  Base: OpenClaw (isolated behind legacy bridge)")
    print("=" * 60)
    print()
    
    # Initialize SAOS controller with legacy bridge
    controller = initialize(legacy_executor=run_legacy)
    
    log_event({"event": "system_startup", "version": "1.0.0"})
    
    # Parse command line or use defaults
    if len(sys.argv) > 1:
        # JSON input from command line
        try:
            input_data = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            # Treat as task type
            input_data = {"type": sys.argv[1], "payload": {}}
    else:
        # Default test input
        input_data = {
            "type": "general",
            "payload": {"message": "SAOS Runtime v1 initialized"}
        }
    
    print(f"📥 Input: {json.dumps(input_data, indent=2)}")
    print()
    
    # Execute through SAOS
    result = controller.handle_request(input_data)
    
    print(f"📤 Result: {json.dumps(result, indent=2)}")
    print()
    
    # Show system status
    status = controller.get_status()
    print(f"📊 Metrics: {json.dumps(status['metrics'], indent=2)}")
    print()
    
    # Show recent logs
    print("📝 Recent Events:")
    for log in status["recent_logs"]:
        ts = log.get("timestamp", "?")[11:19] if "timestamp" in log else "?"
        event = log.get("event", "unknown")
        print(f"   [{ts}] {event}")
    
    print()
    print("✅ SAOS Runtime v1 operational")
    
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
