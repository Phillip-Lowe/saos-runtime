# SAOS Runtime v1

**System Operations Layer — AI Operating System**

Built from OpenClaw base, rearchitected for SAOS control.

## Architecture

```
SAOS Runtime
├── saos/          ← SAOS control system (NEW)
│   ├── controller.py   ← Main entry point
│   ├── router.py       ← Task routing matrix
│   ├── pipeline.py     ← Execution flow
│   ├── schema.py       ← Task creation/validation
│   ├── memory.py       ← In-memory store + metrics
│   ├── agents.json     ← Fleet definitions
│   └── legacy_bridge.py ← Bridge to OpenClaw
├── core/          ← OpenClaw base (PRESERVED)
└── integrations/  ← Tools/channels (RESERVED)
```

## Quick Start

```bash
python app.py
```

## SAOS Fleet

| Agent | Role | Model |
|-------|------|-------|
| SOL | Executor | ollama/kimi-k2.6:cloud |
| ORACLE | Planner | external |
| ASSEMBLY | Architect | ollama/deepseek-v4-pro:cloud |
| DOOBY | Coder | ollama/qwen2.5-coder:7b |
| LOKI | Operator | ollama/qwen3.5:9b |
| CODY | Reviewer | ollama/kimi-k2.6:cloud |
| GENI | Creative | ollama/deepseek-v4-pro:cloud |
| VALI | Validator | ollama/kimi-k2.6:cloud |
| PESSI | Risk | ollama/deepseek-v4-pro:cloud |
| CHATTY | Messenger | ollama/kimi-k2.6:cloud |
| ATLAS | Researcher | ollama/kimi-k2.6:cloud |
| JURIS | Compliance | ollama/kimi-k2.6:cloud |

## Status

✅ Phase 1: Clone + Own  
✅ Phase 2: Isolate Core  
✅ Phase 3: Build SAOS Core  
✅ Phase 4: Legacy Bridge  
✅ Phase 5: Entry Point  
✅ Phase 6: Validation  

## License

OpenClaw base under existing licenses. SAOS layer proprietary.
