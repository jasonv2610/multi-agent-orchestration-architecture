# Examples

This directory contains four reference resources that illustrate the architecture patterns described in `architecture/`.

---

## Contents

| Resource | Type | What It Shows |
|----------|------|---------------|
| `redacted-orchestrator-workflow.json` | Structural example | Full orchestrator node sequence: multi-channel trigger, shortcode bypass, LLM classifier, confidence gate, registry lookup, dispatch, error routing |
| `redacted-workflow.json` | Structural example | Single domain agent workflow: registry lookup, cache check, AI reasoning, data read/write, response formatting |
| `redacted-agent-contract.yaml` | Schema example | Agent input/output contract structure: required fields, output guarantees, error shape, execution constraints, versioning rules |
| `redacted-error-handler.json` | Structural example | Full error handler node sequence: failure capture, error classification, Path A catalog lookup, Path B AI-assisted repair, contract validation before re-execution, escalation, observability emission |
| `scheduling-assistant/` | Importable implementation | Complete 6-stage n8n pipeline: intake, extraction, validation, conflict scan, calendar write, notification |

---

## How to Use These Examples

### Structural examples (redacted JSON/YAML)

`redacted-orchestrator-workflow.json`, `redacted-workflow.json`, and `redacted-agent-contract.yaml` are **read-only reference documents**. They show node types, roles, and data flow with all production values replaced by `<REDACTED>` placeholders.

Use these to understand:
- How the orchestrator connects shortcode matching, LLM classification, and agent dispatch
- What a domain agent workflow looks like internally (registry lookup → cache check → business logic → response)
- The full contract structure your agents should declare

### Scheduling assistant (importable)

`scheduling-assistant/` contains production-ready n8n workflow files with all credentials referenced by logical name and all workflow IDs resolved from environment variables. Import and run these directly.

See `scheduling-assistant/README.md` for setup instructions and `SETUP.md` (root) for credential configuration.

---

## Pattern Coverage

| Pattern | Demonstrated In |
|---------|-----------------|
| Registry-resolved data store references | `redacted-workflow.json`, `redacted-orchestrator-workflow.json`, `registry-pattern/example-registry-sanitized.json` |
| Shortcode bypass (no LLM for known commands) | `redacted-orchestrator-workflow.json` |
| Confidence gating | `redacted-orchestrator-workflow.json` |
| Agent input/output contracts | `redacted-agent-contract.yaml` |
| Error handler,Path A/B recovery | `redacted-error-handler.json` |
| Contract validation before re-execution | `redacted-error-handler.json` |
| AI-assisted repair with catalog promotion | `redacted-error-handler.json` |
| Stage-gated linear pipeline | `scheduling-assistant/` |
| Payload schema enforcement | `scheduling-assistant/specs/event_payload.schema.json` |
| Environment-variable workflow IDs | `scheduling-assistant/workflows/*.json` |
| Configurable notification channel | `scheduling-assistant/workflows/06_notify.json` |
