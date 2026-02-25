# Architecture Overview

## Pattern: Orchestrator + Domain Agents + Error Handler

The system follows a hub-and-spoke orchestration pattern. A single central orchestrator handles all input reception, intent classification, and routing. Domain agents are stateless execution units that receive a classified intent payload, perform domain-specific work, and return a structured response.

This pattern isolates domain logic behind clear input/output contracts, allowing each agent to evolve independently without coupling to other agents or the orchestrator's internal routing logic.

---

## Orchestrator Responsibilities

- Receive inputs from all channels (text, voice, image)
- Normalize input type before classification
- Classify intent using LLM routing with confidence scoring
- Match deterministic shortcode patterns before invoking LLM (cost reduction)
- Dispatch to target agent with structured payload
- Receive agent response and format for delivery
- Route failures to Error Handler

## Domain Agent Responsibilities

Each domain agent handles one bounded context:

| Domain | Bounded Context |
|---|---|
| Productivity | Task management, calendar, email |
| Finance | Expense tracking, receipt processing |
| Operations | Inventory management, operational logging |
| Growth | Learning tracking, career logging |
| Intelligence | Research queries, knowledge base retrieval |
| Document | Document generation and processing |

Agents do not communicate with each other. All inter-domain coordination flows through the orchestrator.

---

## Error Handler

A dedicated error recovery agent monitors workflow execution failures. On failure detection, the error handler:

1. Captures the failure context
2. Looks up known fix patterns for the error type
3. Invokes an AI-assisted repair process
4. Validates the fix before re-execution

The error handler operates asynchronously and does not block the primary execution path.

---

## Voice Pipeline

The voice processing path follows a linear transcription → routing → synthesis pattern:

```
Voice Input → Speech-to-Text → Orchestrator (text) → Agent → TTS → Voice Output
```

The same routing and agent layer handles voice and text uniformly after transcription. Voice is purely an I/O concern, not an architectural one.

---

## Caching Layer

Responses are cached across the orchestration layer by TTL class. Five TTL classes map to data volatility:

| Class | Duration | Applied To |
|---|---|---|
| No-cache | 0 | Real-time data |
| Short | Minutes | High-frequency status |
| Medium | Hours | General queries |
| Long | Days | Research and analysis |
| Reference | Week | Stable definitions |

Cache keys are scoped by agent, user context, and a hash of the query parameters.

---

## Key Design Decisions

- **No direct agent-to-agent calls** — prevents hidden coupling and makes routing auditable
- **Shortcode bypass** — deterministic routing for known high-frequency commands avoids unnecessary LLM calls
- **Registry-resolved configuration** — no data store IDs, API endpoints, or routing rules are hardcoded in workflow logic (see `registry-pattern/`)
- **Spec-defined contracts** — each agent's input/output shape is declared in a schema; violations are caught at validation time, not runtime
