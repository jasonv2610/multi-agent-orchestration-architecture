# Implementation Guide

This guide walks through how to apply the architecture patterns in this repository to build your own multi-agent orchestration system on n8n. It covers the recommended reading order, the decisions you need to make before building, the sequence in which to build each component, and a pre-launch checklist.

This is not a repeat of [SETUP.md](SETUP.md). SETUP.md covers running the scheduling assistant example. This guide covers adapting the full architecture to your own domain.

---

## Who This Guide Is For

- You have read the README and understand the hub-and-spoke orchestration model
- You want to build a production system using these patterns, not just run the example
- You are comfortable with n8n workflow building at an intermediate level
- You have identified a real operational domain to automate

---

## Step 1 — Read the Architecture Docs in Order

Before building anything, read these documents in this sequence. Each one builds on the previous.

| Order | Document | What You Will Understand |
|-------|----------|--------------------------|
| 1 | `README.md` | Overall system model, design principles, what is and is not included |
| 2 | `architecture/overview.md` | Orchestrator responsibilities, agent model, caching layer, key decisions |
| 3 | `architecture/diagrams/agent-topology.md` | Visual flow — primary path, error path, scheduling sub-pipeline |
| 4 | `governance/contracts-overview.md` | How agent contracts work and why they exist |
| 5 | `governance/policy-summary.md` | Routing, caching, verification, and versioning policies |
| 6 | `registry-pattern/ssot-pattern.md` | Why configuration is centralized and how the registry works |
| 7 | `examples/redacted-agent-contract.yaml` | Concrete contract structure before you write your own |
| 8 | `examples/redacted-orchestrator-workflow.json` | Orchestrator node anatomy with role annotations |
| 9 | `examples/redacted-workflow.json` | Domain agent workflow structure |
| 10 | `architecture/error-handler.md` | Recovery model — understand before you build any agent |
| 11 | `architecture/integrations.md` | What external services connect and how credentials are managed |
| 12 | `architecture/observability.md` | What to instrument — plan this before you build, not after |

The scheduling assistant (in `examples/scheduling-assistant/`) is a full working reference. Return to it once you have completed the above — it will be significantly more useful after you understand the architecture it implements.

---

## Step 2 — Make Your Architecture Decisions

Answer these questions before writing any workflow. Decisions made here determine the structure of every component you build.

### 2.1 Domain Scoping

**What bounded contexts does your system cover?**

Each bounded context becomes one domain agent. Agents should not share responsibilities. If two functions always require each other's data, they may belong in the same agent. If they are independently operable, they should be separate agents.

Start with the minimum viable set. It is easier to split an agent later than to untangle a merged one.

| Decision | Question to Answer |
|---|---|
| Agent count | How many distinct domains does your system cover? Start with 2–4. |
| Agent boundaries | Can each agent execute completely from its own data store without querying another agent? |
| Orchestrator input channels | Which channels will the orchestrator receive input from? (text, voice, image, API) |
| Response channels | Where do responses go? (chat interface, email, API callback, voice) |

### 2.2 Routing Design

**How will the orchestrator know which agent to call?**

| Decision | Question to Answer |
|---|---|
| Shortcode patterns | Which high-frequency commands can be identified deterministically without LLM classification? |
| Confidence threshold | Below what confidence score should the orchestrator request clarification instead of routing? (0.7 is a reasonable starting point) |
| Fallback behavior | What does the system return to the user when no agent matches and clarification is not possible? |

**Shortcode patterns save the most cost and latency.** Identify your top 5–10 most common commands and define deterministic patterns for them before building the LLM routing path.

### 2.3 Data Store Design

**Where does each agent read and write?**

| Decision | Question to Answer |
|---|---|
| Store per agent | Does each agent have its own isolated data store, or do agents share stores with access controls? |
| Store type | Google Sheets (operational, low volume), PostgreSQL/Supabase (structured queries, scale), Redis (cache only) |
| Write frequency | Which agents write on every execution? Which are read-only? Write-heavy agents need stricter error handling. |
| Cache eligibility | Which agent responses can be cached? What TTL class is appropriate for each domain? |

### 2.4 Credential Inventory

**List every external credential the system will need before building.**

Do not build workflows and discover credential requirements mid-build. Create a table:

| Logical Name | Service | Used By | OAuth or Key |
|---|---|---|---|
| (example) `google_workspace` | Google Calendar / Sheets | Productivity Agent, Operations Agent | OAuth2 |
| (example) `openai` | LLM router | Orchestrator | API Key |

These logical names go in your registry. The actual credentials go in n8n's credential vault.

---

## Step 3 — Build in This Order

Build in this sequence. Each layer depends on the previous. Building out of order produces incomplete components you will have to revise.

```
1. Registry
      ↓
2. Agent Contracts
      ↓
3. Orchestrator (routing layer only — no agents yet)
      ↓
4. Domain Agents (one at a time)
      ↓
5. Error Handler
      ↓
6. Observability
      ↓
7. Governance Gates
```

---

### 3.1 Registry First

Build your registry before any workflow. The registry is the configuration SSOT — workflows resolve identifiers from it at runtime. Building workflows before the registry results in hardcoded IDs that are difficult to migrate later.

**What goes in the registry:**
- All data store logical names and their resolved IDs (spreadsheet IDs, database names, folder IDs)
- All workflow logical names and IDs (filled in after import — see step 3.3)
- All credential logical names (not the credentials themselves — logical names only)
- All cache TTL class definitions
- All routing rules and shortcode patterns

Use `registry-pattern/example-registry-sanitized.json` as your structural template. Replace all `<REDACTED>` placeholders with your actual logical names. Leave IDs as placeholders until you have imported workflows and have real n8n IDs.

**Commit your registry to version control.** It is configuration, not secrets — treat it like code.

---

### 3.2 Agent Contracts Second

Write a contract for every domain agent before building any agent workflow. Contracts define the interface between the orchestrator and the agent. Without them, the dispatch payload builder in the orchestrator has nothing to validate against.

Use `examples/redacted-agent-contract.yaml` as your template for each agent.

**What every contract must declare:**

```yaml
agent: "[Your Agent Name]"
version: "1.0.0"
domain: "[bounded context]"

input:
  required:
    - name: intent
      type: string
    - name: parameters
      type: object
      properties:
        # domain-specific fields your agent needs

output:
  guaranteed:
    - name: response_text
      type: string
    - name: confidence
      type: number
    - name: execution_status
      type: string
      enum: [success, partial, failed]

constraints:
  max_execution_ms: 10000
  default_ttl_class: medium
  retry_on_partial_failure: true
  max_retries: 2
```

**Contract versioning rule:** Increment the version whenever you add a required input field, remove a guaranteed output field, or change the error shape. Minor changes (new optional fields, expanded enums) do not require a bump.

---

### 3.3 Orchestrator Third

Build the orchestrator workflow using `examples/redacted-orchestrator-workflow.json` as your structural reference.

Build in this node order, testing each path before adding the next:

1. **Multi-channel trigger** — Configure for your input channels
2. **Input normalizer** — Handle each input type (text passthrough, voice → STT)
3. **Shortcode matcher** — Load patterns from routing registry; return matched/not-matched
4. **Routing branch** — If matched: skip to registry lookup. If not: go to LLM classifier
5. **LLM intent classifier** — Configure model, prompt template, and output schema
6. **Confidence gate** — Check confidence against threshold from routing policy
7. **Clarification responder** — Return user-facing clarification when confidence is low
8. **Registry lookup** — Resolve target agent from routing registry
9. **Dispatch payload builder** — Assemble payload, validate against agent contract
10. **Agent dispatcher** — Execute agent workflow; route failures to error router
11. **Response handler** — Format for delivery channel
12. **Error router** — Capture failure context, trigger error handler async

**At this stage, agent workflows do not exist yet.** Test the orchestrator routing paths using mock responses before building agents. This confirms routing logic is correct before domain logic adds complexity.

---

### 3.4 Domain Agents Fourth

Build one agent at a time. Do not build all agents simultaneously. The first agent reveals structural decisions that apply to all subsequent agents.

Use `examples/redacted-workflow.json` as your structural template. Every agent workflow should follow this node order:

```
Trigger (executeWorkflowTrigger)
    ↓
Registry Lookup (resolve data store logical name)
    ↓
Cache Check (check Redis cache for matching key)
    ↓      ↓
  hit    miss
    ↓      ↓
Return   AI Reasoning (if applicable to domain)
cached       ↓
         Data Read (from domain data store)
              ↓
         Business Logic (domain-specific processing)
              ↓
         Data Write (if applicable)
              ↓
         Cache Write (store result with TTL class key)
              ↓
         Response Formatter (shape to output contract)
```

**Each agent must:**
- Reference data stores by logical name via the registry — never hardcode IDs
- Return the exact output fields declared in its contract
- Return a structured error shape (not a raw exception) on failure
- Respect its declared `max_retries` value

**Test each agent in isolation** by calling it directly before connecting it to the orchestrator. Confirm it returns the correct output contract shape on success and the correct error shape on failure.

---

### 3.5 Error Handler Fifth

Build the error handler after at least one agent is working. You need real failure patterns to test against.

Structure the error handler as two paths (see `architecture/error-handler.md` for full detail):

**Path A — Known fix pattern:**
1. Classify error type against error type registry
2. If known pattern found: retrieve fix, apply, validate against contract, re-execute
3. If validation passes: re-execute. If fails: escalate.

**Path B — AI-assisted repair:**
1. If no pattern found: capture structured failure context
2. Submit context to repair model (sanitized — no raw values, schema only)
3. Validate proposed fix against contract
4. If valid: apply and re-execute. Log for catalog promotion.
5. If invalid after max retries: human escalation record

**Error type catalog:** Start with the 5–10 most common n8n failure types for your integrations (timeouts, auth failures, rate limits, schema violations). Add patterns as new failures occur. The goal is to grow Path A coverage so Path B is rarely reached.

---

### 3.6 Observability Sixth

Add instrumentation to each component using `architecture/observability.md` as your signal reference. Instrument in this priority order:

1. **Routing layer** — shortcode hit rate, LLM call rate, classification confidence, routing latency
2. **Agent layer** — execution status per agent, execution latency per agent, cache hit rate per agent
3. **Error handler** — error rate by type, Path A vs B split, repair success rate, escalation rate
4. **System health** — end-to-end latency, queue depth, active workflow count

Build your 4 dashboards (System Health, Routing, Agent Performance, Error Recovery) before going live. You cannot diagnose production problems you are not measuring.

---

### 3.7 Governance Gates Last

Once the system is working end-to-end, add the pre-commit validation gates:

- **Version increment gate** — Block commits that modify workflow JSON without a version bump
- **Registry key gate** — Block commits that introduce workflow references to undefined registry keys
- **Contract compliance gate** — Block commits that introduce contract violations

These gates prevent the most common source of production drift: incremental changes that break interfaces silently. See `governance/contracts-overview.md` for the enforcement model.

---

## Step 4 — Adapting the Scheduling Assistant

The scheduling assistant in `examples/scheduling-assistant/` is the only fully functional workflow set in this repository. Use it as a concrete reference when building your own pipeline components.

**What is directly reusable:**

| Component | How to Adapt |
|---|---|
| Pipeline stage structure (01–06 numbered files) | Use the same numbered naming convention for any multi-stage pipeline you build |
| Set node output pattern (`Set Output Data` node between Code and ExecuteWorkflow) | Copy this pattern exactly — it is how each stage packages its output for the next |
| `$env.WORKFLOW_ID_*` references | Use env vars for all inter-workflow IDs — never hardcode |
| Merge node pattern (stage 04) | Any time a node that may return 0 items feeds into logic that must always execute, add a Merge node before it |
| Notification stage decoupled from write stage | If you build any pipeline with both a write stage and a notification stage, keep them separate — notification failure should not roll back a completed write |

**What you replace:**

| Scheduling component | Your equivalent |
|---|---|
| Intake webhook | Your trigger (webhook, Telegram, cron, API call) |
| NLP extraction (stage 02) | Your data extraction or transformation logic |
| Business validation (stage 03) | Your domain-specific validation rules |
| Google Calendar conflict scan (stage 04) | Your domain-specific pre-write check |
| Google Calendar / Outlook event creation (stage 05) | Your domain data store write |
| SMTP email notification (stage 06) | Your notification channel (Telegram, email, API callback) |

---

## Step 5 — Pre-Launch Checklist

Run through this checklist before going live.

### Registry
- [ ] All data store IDs are populated (not placeholder values)
- [ ] All workflow IDs are populated (assigned by n8n after import)
- [ ] All credential logical names map to credentials that exist in n8n's vault
- [ ] Registry is committed to version control
- [ ] No workflow contains a hardcoded data store ID or credential ID

### Contracts
- [ ] Every domain agent has a declared contract in version control
- [ ] All contracts are at version 1.0.0 or higher (not placeholder)
- [ ] Every required input field in every contract is populated by the dispatch payload builder

### Workflows
- [ ] All 6 scheduling assistant workflows are imported and activated in the correct order
- [ ] All domain agent workflows are activated
- [ ] Orchestrator is activated last
- [ ] Error handler is activated
- [ ] All `WORKFLOW_ID_*` environment variables are set in n8n

### Routing
- [ ] Shortcode patterns are loaded in the routing registry
- [ ] Confidence threshold is set in the routing policy
- [ ] Clarification responder is tested with a low-confidence input
- [ ] At least one end-to-end test per agent domain passes

### Error Handling
- [ ] Error handler activates on a test failure (confirm by triggering a deliberate failure)
- [ ] At least Path A is functional for at least one known error type (e.g., timeout)
- [ ] Escalation notification channel is configured

### Observability
- [ ] All 4 dashboards are configured
- [ ] Alert thresholds are set for at least: agent failure rate, human escalation rate, end-to-end latency p99
- [ ] A test execution is visible in all dashboards

### Security
- [ ] No API keys, tokens, or connection strings appear in any workflow JSON file
- [ ] No secrets appear in the registry file
- [ ] All credentials are stored exclusively in n8n's credential vault
- [ ] Webhook URLs are not hardcoded in documentation published publicly

---

## Common Mistakes

**Building agents before contracts.** This produces agents with undeclared or inconsistent output shapes. The orchestrator's dispatch payload builder cannot validate against a contract that does not exist.

**Hardcoding workflow IDs.** When a workflow is re-imported or an n8n instance is migrated, IDs change. Use `$env.WORKFLOW_ID_*` references throughout. Update the registry; leave workflows untouched.

**Skipping the Merge node on variable-result queries.** Any n8n node that queries an external source and may return 0 items will stop execution on the 0-item path. If downstream logic must always run regardless of result count, place a Merge node between the query node and the downstream logic. See stage 04 in the scheduling assistant for the implementation pattern.

**Building observability after launch.** You cannot establish a baseline for alerting thresholds from live production data. Build dashboards during development, observe behavior in staging, then set thresholds before go-live.

**One agent for all domains.** The orchestrator pattern only provides value if agents have clear, separate responsibilities. A single large agent that handles multiple domains defeats the purpose of the routing layer and makes the system harder to debug, scale, and replace.
