# ORACLE — Lean Agent Architecture for Business

**Date:** 2026-06-27
**Source:** ORACLE system design handoff
**Status:** DESIGN COMPLETE — awaiting implementation

---

## 1. CORE PRINCIPLE

> **Agents should not own complexity — the system should.**

Agents = decision nodes
System = execution + memory + rules

---

## 2. ARCHITECTURE OVERVIEW

```
Company System
│
├── Agent Layer (lean decision units)
│   ├── Role Agents
│   ├── Validator Agents
│   └── Risk Agents
│
├── Orchestration Layer (SOL-equivalent)
│
├── Execution Layer (tools, APIs, workflows)
│
├── Memory Layer (structured state)
│
└── Interface Layer (dashboard/API)
```

---

## 3. AGENT DESIGN (LEAN MODEL)

### 3.1 Agent Definition Schema

```
AGENT = {
  name,
  role,
  inputs,
  outputs,
  constraints,
  decision_rules,
  escalation_rules
}
```

**No agent should exceed:**
- 1 primary role
- 5 decision rules
- 3 outputs

### 3.2 Example: SUPPORT_AGENT

```
Role: Handle customer issues

Inputs:
- ticket
- customer data
- system state

Outputs:
- response
- escalation_flag
- tag

Constraints:
- must not expose internal data
- must follow policy templates

Decision Rules:
1. classify urgency
2. check known issues
3. match resolution template
4. detect escalation condition

Escalation:
- refund request → RISK
- legal risk → JURIS
- repeated failure → ORCHESTRATOR
```

---

## 4. AGENT TYPES (STANDARD SET)

### 4.1 Core Role Agents

| Agent | Purpose | SAOS Equivalent |
|-------|---------|-----------------|
| SUPPORT | Customer issues | CHATTY |
| SALES | Lead handling | CHATTY + ATLAS |
| OPS | Task routing | LOKI |
| FINANCE | Billing, invoices | CODY |
| PRODUCT | Feature logic | ASSEMBLY |

### 4.2 System Agents

| Agent | Purpose | SAOS Equivalent |
|-------|---------|-----------------|
| ORCHESTRATOR | Flow control | SOL |
| VALIDATOR | Correctness | VALI |
| RISK | Failure detection | PESSI |
| LEGAL | Compliance | JURIS |
| MEMORY | State integrity | ATLAS |

### 4.3 Rule

> No company should start with more than **6–8 agents total**

---

## 5. ORCHESTRATION LAYER

### 5.1 Responsibilities

- Route inputs → correct agent
- Enforce execution order
- Prevent loops
- Handle retries
- Track state

### 5.2 Execution Flow

```
Input → Classifier → Agent → Validator → Risk Check → Output
```

### 5.3 Retry Policy (GLOBAL)

- Max attempts: 5
- Attempt 1–3: retry with context correction
- Attempt 4: switch strategy
- Attempt 5: escalate

### 5.4 Escalation Path

```
Agent → Validator → Risk → Human / SOL escalation
```

---

## 6. MEMORY SYSTEM (NON-BLOAT CRITICAL)

### 6.1 Rule

> No free-form memory. Only structured state.

### 6.2 Memory Schema

```
STATE = {
  entity_id,
  type,           // order, ticket, task
  status,
  attributes,
  history[],
  last_updated
}
```

### 6.3 Memory Layers

| Layer | Purpose | SAOS Implementation |
|-------|---------|---------------------|
| Active State | Live operations | memory.py tasks dict |
| Log | Immutable history | memory.py logs array |
| Knowledge | Reusable patterns | agents.json + routing matrix |

### 6.4 Constraints

Agents cannot:
- Write arbitrary data
- Modify past logs
- Store raw conversations as memory

---

## 7. EXECUTION LAYER

### 7.1 Execution Contract

Agents **do not execute tools directly**. They output **instructions**.

```
EXECUTION_REQUEST = {
  action,
  target,
  payload,
  validation_required
}
```

### 7.2 Example

```json
{
  "action": "send_email",
  "target": "customer",
  "payload": {
    "template": "refund_approved",
    "variables": {...}
  },
  "validation_required": true
}
```

### 7.3 Benefits

- Prevents hallucinated tool use
- Centralizes security
- Enables logging + rollback

---

## 8. VALIDATION LAYER (VALI)

### 8.1 Responsibilities

- Check output correctness
- Enforce schema compliance
- Prevent invalid actions

### 8.2 Validation Checks

- Schema valid
- Entity exists
- Data consistent
- Action allowed

### 8.3 Fail Behavior

```
Fail → Send back to agent with error
Retry → max 5
Escalate
```

---

## 9. RISK LAYER (PESSI)

### 9.1 Purpose

Detect:
- Financial loss
- Legal exposure
- System inconsistency
- Security issues

### 9.2 Risk Flags

| Type | Example | Action |
|------|---------|--------|
| HIGH | unauthorized refund | Block + escalate |
| MEDIUM | missing data | Warn + log |
| LOW | formatting issue | Allow |

---

## 10. DEPLOYMENT MODEL

### 10.1 Each Company Gets

```
Client Instance
├── Agent Set (6–8 agents)
├── Orchestrator
├── Database
├── Dashboard
├── API Layer
```

### 10.2 Isolation Rules

- No shared client data
- Separate memory stores
- Shared agent templates only

---

## 11. OPEN SOURCE STRATEGY

### 11.1 OPEN SOURCE

- Agent schema
- Orchestration framework
- Execution contract
- Validation logic

### 11.2 CLOSED (CORE ADVANTAGE)

- Prompt logic
- Agent tuning
- Business workflows
- Optimization layers
- SaaS dashboard

### 11.3 Result

> **The standard + the premium implementation**

---

## 12. ANTI-BLOAT RULES (NON-NEGOTIABLE)

| # | Rule | Why |
|---|------|-----|
| 1 | Agents cannot call other agents directly | Prevents chaos |
| 2 | No agent owns memory | Avoids state corruption |
| 3 | No multi-role agents | Enforces clarity |
| 4 | All outputs must be structured | No free text decisions |
| 5 | Execution must be centralized | Prevents tool drift |

---

## 13. BUILD PLAN

### Step 1: Define Core Agents (DONE — SAOS fleet exists)

### Step 2: Implement Schemas

- [ ] Agent schema (agents.json v2)
- [ ] Execution contract (execution.py)
- [ ] Memory schema (memory.py v2)

### Step 3: Build Orchestrator

- [ ] Routing logic (router.py v2)
- [ ] Retry handling (pipeline.py v2)
- [ ] Escalation (escalation.py)

### Step 4: Add Execution Layer

- [ ] Email dispatcher
- [ ] Database update handler
- [ ] Webhook caller

### Step 5: Dashboard (SAOS)

- [ ] Activity feed
- [ ] Task status
- [ ] Agent logs

### Retry Policy
5 attempts per task

### Escalation
→ SOL → Human → Log + halt

### Completion Criteria
- [ ] Agent handles real workflow
- [ ] Full traceability
- [ ] No silent failures
- [ ] Deterministic outputs

---

## 14. SAOS v1 vs ORACLE Architecture Gap Analysis

| Component | SAOS v1 Status | ORACLE Requirement | Gap |
|-----------|---------------|-------------------|-----|
| Agent schema | agents.json (basic) | Full schema with rules | ⚠️ Needs v2 |
| Orchestration | controller.py (simple) | Full flow control | ⚠️ Needs v2 |
| Execution layer | legacy_bridge.py (stub→subprocess) | Structured execution contract | ⚠️ Needs executor.py |
| Memory | memory.py (dict + logs) | Structured state with layers | ⚠️ Needs v2 |
| Validation | None | VALI layer with checks | ❌ Missing |
| Risk | router priority rules only | PESSI layer with flags | ❌ Missing |
| Escalation | None | Defined escalation path | ❌ Missing |
| Dashboard | None | Activity feed + status | ❌ Missing |

---

## 15. NEXT STEPS

### Option A: Schema-First (Recommended)
1. Build agent schema v2 with constraints/rules
2. Build execution contract
3. Build memory v2 with structured state
4. Integrate with existing bridge

### Option B: Workflow-First
1. Pick one business workflow (support ticket)
2. Build minimal agent set for that flow
3. Add orchestration around it
4. Expand from there

### Option C: Infrastructure-First
1. Build the execution layer (executor.py)
2. Add validation + risk hooks
3. Build dashboard
4. Plug in agents last

---

## 16. ORACLE FINAL POSITION

> You're not building "AI agents."
>
> You're building: **A deterministic operational system powered by constrained decision units**

**Validation: PASS**
- Execution Path: PASS
- System Boundaries: PASS
- Non-bloat compliance: PASS
- SOL alignment: PASS
- Business deployability: PASS

---

*Saved to: `/Users/philliplowe/saos-runtime/docs/oracle-lean-agent-architecture.md`*
