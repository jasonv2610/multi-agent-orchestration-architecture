# Multi-Agent Orchestration Architecture

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
![Status](https://img.shields.io/badge/Status-Production_Architecture-6d8b74?style=flat-square&labelColor=1a1a2e)
![Validation](https://img.shields.io/badge/Validation-Private_Pipeline-6d8b74?style=flat-square&labelColor=1a1a2e)
![Type](https://img.shields.io/badge/Type-Production_Architecture-6d8b74?style=flat-square&labelColor=1a1a2e)

> This repository represents a production architecture layer. Execution pipelines and validation operate in a private environment.

86-item inventory lookups in under 30 seconds  
VIP contract turnaround reduced from 2 days to same-session  
Zero manual receipt entry  

This is a production system, not a tutorial.

A contract-first, registry-driven multi-agent orchestration architecture on n8n Cloud. Seven specialized agents. One orchestrator. Zero manual intervention.

Built for engineers who want production-grade patterns: registry-based configuration, formal agent contracts, and autonomous error recovery.

## What It Does

| Agent         | Outcome                                                                              |
|---------------|--------------------------------------------------------------------------------------|
| Operations    | 86-item response from manual lookup to under 30 seconds; all stock events logged     |
| Intelligence  | Research answers in under 10 seconds via Perplexity and RAG over Supabase            |
| Documents     | VIP contract turnaround from 2 days to same-session via Google Docs API              |
| Finance       | Manual receipt entry eliminated; OCR auto-categorization logs expenses in one step   |
| Self-Healing  | Resolves known errors without human input; escalates unknowns to Telegram            |

## Business Impact

| Metric | Baseline | Result | Delta |
|--------|----------|--------|-------|
| Contract turnaround time | 2 days | Same-session | -99%+ |
| Receipt entry | Manual, per transaction | OCR auto-categorized | 100% automated |
| Inventory lookup latency | Manual lookup | Under 30 seconds | -95%+ |
| Operational error recovery | Human intervention required | Autonomous resolution | Zero-touch for known failures |

## Execution Example

**Input:** Voice message: "86 the salmon" (mark menu item as unavailable)

1. Messaging interface receives the voice attachment and passes it to the orchestrator
2. Orchestrator routes audio through a speech-to-text transcription node
3. Transcript matches a deterministic shortcode pattern, so LLM classification is bypassed
4. Operations Agent is invoked with the extracted item identifier
5. Agent updates the inventory data store with availability status and timestamp
6. Confirmation is synthesized to audio and returned as a voice reply

## Architecture Overview

A central orchestrator receives input from multiple channels, text, voice, and image, classifies intent using a routing layer, and delegates to an appropriate domain agent.

Agents operate independently against dedicated data stores and are bound by explicit input and output contracts. Execution failures are intercepted by a recovery layer that applies remediation patterns without direct human intervention.

| Attribute            | Value                |
|----------------------|----------------------|
| Runtime              | n8n Cloud            |
| User Interface       | Telegram             |
| Developer Interface  | Claude Code via MCP  |
| Version              | 1.0.0                |


## System Layers

```
+--------------------------------------------------+
|  Layer 1: Workflows                              |
|  Orchestration, Domain Agents, Error Handler     |
|  Scheduling Pipeline, Helper Utilities           |
+--------------------------------------------------+
|  Layer 2: Governance                             |
|  Agent Contracts, Routing Policy                 |
|  Caching Policy, Verification Policy             |
|  Version Validation, Pre-commit Gates            |
+--------------------------------------------------+
|  Layer 3: Registry (SSOT)                        |
|  Data Store References, Credential Identifiers   |
|  Routing Rules, Cache Class Definitions          |
+--------------------------------------------------+
|  Layer 4: Knowledge  (private)                   |
|  Prompt Templates, n8n Standards, RAG Patterns   |
+--------------------------------------------------+
|  Layer 5: Operations  (private)                  |
|  Self-healing, Debugging Patterns, Audit Tools   |
+--------------------------------------------------+
```

## Repository Structure

The system is organized into five logical layers. This repository includes architecture documentation, governance tooling, and workflow examples. Internal operational documentation is private. Internal operational documentation is private.

**Architecture**
Design documentation for each system component. Covers the orchestration pattern, domain agent model, scheduling sub-pipeline, error recovery model, integration layer, and observability design.

- `architecture/overview.md`: Orchestrator, domain agents, caching layer, key design decisions
- `architecture/scheduling-pipeline.md`: 6-stage scheduling sub-pipeline, event payload schema, stage reference
- `architecture/error-handler.md`: Error type catalog, known fix patterns, AI-assisted repair, escalation model
- `architecture/integrations.md`: AI/reasoning, data storage, communication, and developer tooling integrations
- `architecture/observability.md`: Signal taxonomy, alert thresholds, dashboard structure
- `architecture/diagrams/agent-topology.md`: Primary flow, error path, and scheduling pipeline topology

**Governance**
The contract and policy layer. Declares input/output schemas for each agent, routing policy, caching policy, verification thresholds, and versioning rules. A pre-commit validation gate checks contract compliance before any workflow change reaches the repository.

**Examples**

Two categories: one fully importable pipeline, and structural reference files showing architecture patterns.

**Importable (drop into any n8n instance):**

`examples/scheduling-assistant/workflows/` -- 6 production workflow JSON files, valid and ready to import:

| File                          | Stage                                             | Nodes |
|-------------------------------|---------------------------------------------------|-------|
| `01_intake.json`              | Receive and validate incoming request             | 8     |
| `02_extract_normalize.json`   | Parse datetime, normalize attendees and location  | 5     |
| `03_validate.json`            | Apply business rules, flag missing fields         | 7     |
| `04_conflict_scan.json`       | Read-only calendar check, surface alternatives   | 9     |
| `05_route_export.json`        | Write to Google Calendar or Outlook               | 8     |
| `06_notify.json`              | Send confirmation via configured channel          | 5     |

See `examples/scheduling-assistant/README.md` for import steps and environment variable setup.

**Structural reference (redacted -- architecture patterns only, not importable):**

- `examples/redacted-orchestrator-workflow.json`: Master orchestrator routing structure with annotated node roles
- `examples/redacted-error-handler.json`: Error handler node sequence -- Path A catalog recovery, Path B AI-assisted repair, escalation
- `examples/redacted-agent-contract.yaml`: Domain agent input/output contract structure
- `examples/redacted-workflow.json`: Domain agent workflow node structure

**Notebooks**
Interactive Python demos of core architectural patterns. Runnable without credentials or live system access.

- `notebooks/routing-system-demo.ipynb`: End-to-end routing pipeline demo - Tier 1 shortcode matching, Tier 2 LLM classification simulation, confidence gate visualization, and 30-day routing distribution charts.

**Documentation** *(private)*
Internal knowledge base, prompt templates, n8n execution standards, debugging patterns, and operational runbooks. Not included in this release.

## Core Capabilities

- Text, voice, and image input processing
- Deterministic shortcode routing for high-frequency commands
- LLM-based intent classification for unstructured natural language
- Tiered response caching across five TTL classes
- Autonomous error detection and self-healing via AI-assisted workflow repair
- Registry-driven configuration with no hardcoded identifiers in workflow logic
- Spec-defined agent contracts enforced by pre-commit validation

## Scope and Exclusions

This repository is a curated release of architecture, workflow structure, and design patterns from a larger private system. The following are not included:

- Proprietary prompt engineering and LLM routing logic
- Production credentials and environment-specific configuration
- Internal operational data and user context
- Self-healing infrastructure and repair tooling
- Workflow implementations containing non-public business logic

Published materials reflect architectural and structural decisions only. Functional reproduction requires environment configuration not available in this repository.
## Architecture and Governance

| Dimension | Implementation |
|-----------|----------------|
| Orchestrator Engine | Central hub-and-spoke orchestrator; single entry point for all input channels |
| Agent Topology | Six stateless domain agents; zero direct agent-to-agent communication |
| Data Classification | T2 credentials in n8n vault; T3 operational data never exposed in workflow logic |
| Determinism | Shortcode routing is fully deterministic; LLM path confidence-gated before dispatch |
| Idempotency | Registry-resolved workflow IDs; stage payloads append-only, never overwrite |
| Telemetry | Structured events emitted at each routing, agent, cache, and error decision point |
| Self-Healing | Autonomous Path A catalog recovery and Path B AI-assisted repair before escalation |
| Contract Enforcement | Input/output schemas declared per agent; validated at commit time and runtime |

## Design Principles

- **Configuration over hardcoding:** Environment-specific values reside in a centralized registry, never inside workflow logic.
- **Contracts over assumptions:** Every agent declares explicit input/output schemas enforced at commit time.
- **Validation before delegation:** Low-confidence intent triggers clarification rather than speculative routing.
- **Abstraction over coupling:** Agents share no direct dependencies. Coordination flows through the orchestrator.

## Getting Started

- [SETUP.md](SETUP.md): Tool requirements, credential configuration, workflow import order, environment variables, and verification steps.
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md): How to apply these architecture patterns to build your own system: reading order, architecture decisions, component build sequence, scheduling assistant adaptation guide, and pre-launch checklist.

## License

Refer to [LICENSE.md](LICENSE.md) for licensing terms.
