# Multi-Agent Orchestration Architecture

A contract-first, registry-driven multi-agent orchestration system built on n8n Cloud. This is a public portfolio repository derived from a live production system. All credentials, proprietary routing logic, and internal operational data are excluded.

---

## What This Repository Contains

| Layer | Path | Purpose |
|-------|------|---------|
| Architecture docs | `architecture/` | System design for each component |
| Governance | `governance/` | Agent contracts, policies, and pre-commit validation |
| Registry pattern | `registry-pattern/` | SSOT configuration pattern and sanitized example |
| Examples | `examples/` | Structural reference files and an importable n8n pipeline |
| Tests | `tests/` | Structural test examples for contract compliance |
| Setup | `SETUP.md` | Credential setup, environment variables, and workflow import guide |
| Implementation guide | `IMPLEMENTATION_GUIDE.md` | How to adapt these patterns to a new system |

---

## Core Rules (Read Before Touching Anything)

**Never add secrets.** No API keys, tokens, OAuth credentials, connection strings, or environment-specific values belong in any file in this repository. Credentials are stored in n8n's credential vault and referenced by logical name only.

**Never hardcode IDs.** Workflow IDs, spreadsheet IDs, folder IDs, and database names are resolved at runtime through the registry. Any value that changes between environments belongs in the registry, not in a workflow node.

**Never skip a version bump.** Every change to a workflow JSON file requires a `versionId` increment. The pre-commit validator blocks commits that modify workflow logic without one.

**Never add em dashes.** All documentation in this repository is written without em dashes. Use a colon, a comma, or split into two sentences instead.

---

## Writing Style

All documentation follows plain professional English. Before writing or editing any text:

- Use a colon where you would use an em dash to introduce a clarification
- Use a comma or period where you would use an em dash as a parenthetical
- Use "make sure" instead of "ensure"
- Use "use" instead of "utilize" or "leverage"
- Use "run" instead of "execute" (except in precise technical node execution contexts)
- Use "build" or "set up" instead of "implement"
- Write in active voice. Passive constructions like "is enforced by" should be rewritten.
- Keep sentences short. If a sentence needs an em dash to hold together, split it.

---

## Repository Conventions

### Workflow JSON files

- All files live in `examples/scheduling-assistant/workflows/`
- Credential references use logical names matched exactly to n8n credential names (see `SETUP.md`)
- Inter-workflow triggers use `$env.WORKFLOW_ID_*` references, never raw IDs
- Every workflow carries a `versionId` field in semver format (e.g., `"v1.1.0"`)
- Disabled nodes are intentional placeholders. Do not enable them without reading the setup docs.

### Registry

- The registry is the single source of truth for all configuration
- Logical names are the keys. Raw IDs and secrets are never stored here.
- See `registry-pattern/ssot-pattern.md` for the pattern and `registry-pattern/example-registry-sanitized.json` for the structure

### Agent contracts

- Contracts are declared before building any agent workflow
- The contract declares: required inputs, guaranteed outputs, error shape, execution constraints, and versioning rules
- See `examples/redacted-agent-contract.yaml` for the structure

### Pre-commit validation

- `governance/pre-commit-contract-validator.js` is a structural example of the validation script
- In a real implementation it installs to `.git/hooks/pre-commit` via `npm install` (husky)
- It checks two things: version bump present, and output nodes conform to declared contract

---

## Key Design Decisions

These decisions are fixed. Do not propose changes that contradict them.

**No agent-to-agent calls.** All inter-domain coordination flows through the orchestrator. Agents are stateless and communicate only through structured payloads.

**Shortcode bypass before LLM.** Deterministic patterns are matched first. The LLM classifier is only reached when no shortcode matches. This controls cost and latency.

**Validation before calendar access.** In the scheduling pipeline, stages 01-03 perform no external reads or writes. External operations begin only after business logic validation passes.

**Notification decoupled from write.** A notification failure does not roll back a completed write. Stages 05 and 06 are independent by design.

**Payload immutability per stage.** Each pipeline stage appends to the shared payload. It does not overwrite fields set by earlier stages.

---

## What Is Not in This Repository

This is a public showcase. The following are intentionally excluded:

- Proprietary prompt engineering and LLM routing logic
- Production credentials and environment configuration
- Internal operational data and user context
- Self-healing infrastructure and repair tooling
- Workflow implementations containing non-public business logic

Do not add any of the above.

---

## Changelog

All changes are tracked in `CHANGELOG.md`. Update it whenever you add, modify, or remove files.
