# Session Save — 2026-06-27 ~12:22 CDT
**User directive:** "Save everything before compaction"

---

## What Was Accomplished

### 1. SAOS Runtime v1 — Core Bridge INTEGRATED ✅
- **File:** `saos/legacy_bridge.py` — Fixed to use correct OpenCLaw CLI invocation
- **Command:** `node openclaw.mjs agent --agent <id> --message "..." --json`
- **Status:** WORKING — SOL responds through bridge, ~11-14s inference time
- **Location:** `/Volumes/External/saos-runtime/` (external HDD)

### 2. Tool Restrictions for SOL
- **Config:** `~/.openclaw/openclaw.json`
- **SOL tools:** `minimal` profile + `memory_search`, `memory_get`, `read`, `exec`
- **Result:** SOL gets ~5 tools instead of 30+

### 3. Bootstrap Limits Lowered
- **Config:** `~/.openclaw/openclaw.json`
  - `bootstrapMaxChars`: 5000 (was 20000)
  - `bootstrapTotalMaxChars`: 10000 (was 150000)
- **Source:** `core/src/agents/embedded-agent-helpers/bootstrap.ts`
  - `DEFAULT_BOOTSTRAP_MAX_CHARS = 5_000` (was 20_000)
  - `DEFAULT_BOOTSTRAP_TOTAL_MAX_CHARS = 10_000` (was 60_000)
- **NOT YET APPLIED** — compiled dist hasn't been rebuilt

### 4. Loki + Dooby Bootstrap Config (NEEDS REBUILD)
- **Problem:** Local models fail due to 131K token context injection
- **Solution:** Need to add `tools` config + lower bootstrap limits to agent configs
- **Blocker:** OpenClaw dist needs rebuild to pick up source changes

### 5. Build Attempt
- **Tried:** `node core/scripts/build-all.mjs`
- **Status:** Stuck/Hung — no CPU activity, no output
- **Alternative:** Try specific profile builds

### 6. GitHub Repo Updated
- **URL:** https://github.com/Phillip-Lowe/saos-runtime
- **Commits:** Working bridge, lowered limits, tool restrictions

---

## ORACLE Lean Agent Architecture Document
- **Saved:** `docs/oracle-lean-agent-architecture.md`
- **Status:** Design complete, implementation gap analysis done
- **Key insight:** SAOS needs custom agent runner OR rebuilt OpenClaw

---

## Pending Items

1. ⏳ **Rebuild OpenClaw** to apply bootstrap limit changes
2. ⏳ **Add Loki + Dooby tool configs** to `openclaw.json`
3. ⏳ **Test Loki/Dooby** with reduced context
4. ⏳ **Build custom agent runner** (last resort)

---

## Key Files Modified

| File | Change |
|------|--------|
| `saos/legacy_bridge.py` | Fixed CLI invocation |
| `~/.openclaw/openclaw.json` | SOL tools + bootstrap limits |
| `core/src/agents/embedded-agent-helpers/bootstrap.ts` | Default limits lowered |
| `docs/oracle-lean-agent-architecture.md` | ORACLE design saved |

---

## Disk Status

| Location | Size | Status |
|----------|------|--------|
| `/Volumes/External/saos-runtime` | ~250MB | Working repo |
| `~/.openclaw/` | 6.4GB | Live config (don't touch) |
| `/tmp/` | Cleaned | Staging removed |

---

## Next Session Priority

**REBUILD OPENCLAW** or **build custom agent runner** for Loki/Dooby to work with local models.
