# Multi-Agent Orchestration Architecture

A contract-first, registry-driven multi-agent orchestration architecture deployed on n8n Cloud. The system routes structured and unstructured inputs across specialized domain agents using deterministic routing and confidence-governed intent classification.

## Architecture Overview

A central orchestrator receives input from multiple channels, text, voice, and image, classifies intent using a routing layer, and delegates execution to an appropriate domain agent.

Agents operate independently against dedicated data stores and are bound by explicit input and output contracts. Execution failures are intercepted by a recovery layer that applies remediation patterns without direct human intervention.

| Attribute | Value |
|------------|-------|
| Runtime | n8n Cloud |
| User Interface | Telegram |
| Developer Interface | Claude Code via MCP |
| Version | 2.2.0 |


## System Layers

```
┌──────────────────────────────────────────────────┐
│  Workflows                                       │
│  Orchestration · Domain Agents · Error Handler   │
│  Scheduling Pipeline · Helper Utilities          │
├──────────────────────────────────────────────────┤
│  Governance                                      │
│  Agent Contracts · Routing Policy                │
│  Caching Policy · Verification Policy            │
│  Version Validation · Pre-commit Gates           │
├──────────────────────────────────────────────────┤
│  Registry (SSOT)                                 │
│  Data Store References · Credential Identifiers  │
│  Routing Rules · Cache Class Definitions         │
├──────────────────────────────────────────────────┤
│  Knowledge  ·········· (private)                 │
│  Prompt Templates · n8n Standards · RAG Patterns │
├──────────────────────────────────────────────────┤
│  Operations  ········· (private)                 │
│  Self-healing · Debugging Patterns · Audit Tools │
└──────────────────────────────────────────────────┘
```

## Repository Structure

The system is organized into five logical layers. This public showcase includes the first three; the final two are private.

**Workflows**
The automation layer. Contains the master orchestrator, six domain agents, a scheduling sub-pipeline, error handler, and helper utilities. Workflows are version-controlled and validated against declared contracts before deployment. No workflow is ever deleted from production -deprecated logic is deactivated or superseded.

**Governance**
The contract and policy layer. Declares input/output schemas for each agent, routing policy, caching policy, verification thresholds, and versioning rules. A pre-commit validation gate enforces contract compliance before any workflow change reaches the repository.

**Registry**
The configuration SSOT layer. Centralizes all data store references, credential identifiers, routing rules, and cache class definitions. Workflows resolve identifiers at runtime from the registry; no environment-specific values are hard-coded into the workflow logic.

**Integrations** *(conceptual -credentials and endpoints are private)*
The external service layer. Organized into four categories: AI and reasoning services, data storage backends, communication interfaces, and developer tooling. All integration credentials are managed outside the repository.

**Documentation** *(private)*
Internal knowledge base, prompt templates, n8n execution standards, debugging patterns, and operational runbooks. Not included in this public showcase.

## Execution Example

**Input:** Voice message -"86 the salmon" (mark menu item as unavailable)

1. Messaging interface receives the voice attachment and passes it to the orchestrator
2. Orchestrator routes audio through a speech-to-text transcription node
3. Transcript matches a deterministic shortcode pattern; LLM classification is bypassed
4. Operations Agent is invoked with the extracted item identifier
5. Agent updates the inventory data store with availability status and timestamp
6. Confirmation is synthesized to audio and returned as a voice reply

## Core Capabilities

- Text, voice, and image input processing
- Deterministic shortcode routing for high-frequency commands
- LLM-based intent classification for unstructured natural language
- Tiered response caching across five TTL classes
- Autonomous error detection and self-healing via AI-assisted workflow repair
- Registry-driven configuration with no hardcoded identifiers in workflow logic
- Spec-defined agent contracts enforced by pre-commit validation

## Scope and Exclusions

This repository is a curated public showcase of architecture, workflow structure, and design patterns from a larger private system. The following are not included:

- Proprietary prompt engineering and LLM routing logic
- Production credentials and environment-specific configuration
- Internal operational data and user context
- Self-healing infrastructure and repair tooling
- Workflow implementations containing non-public business logic

Published materials reflect architectural and structural decisions only. Functional reproduction requires environment configuration not available in this repository.

## Design Principles

- **Configuration over hardcoding** -Environment-specific values reside in a centralized registry, never inside workflow logic.
- **Contracts over assumptions** -Every agent declares explicit input/output schemas enforced at commit time.
- **Validation before delegation** -Low-confidence intent triggers clarification rather than speculative routing.
- **Abstraction over coupling** -Agents share no direct dependencies; coordination flows through the orchestrator.

## License

Refer to [LICENSE.md](LICENSE.md) for licensing terms.
