# Changelog

All notable changes to this repository are documented here.

---

## v2.3.0 (2026-03-02)

### Removed
- `CLAUDE.md`: Internal AI operating instructions. Not appropriate for a public portfolio repo. Repo conventions and design decisions remain in `README.md` and `IMPLEMENTATION_GUIDE.md`.

---

## v2.2.0 (2026-01-19)

### Added
- `package.json`: Dev dependency manifest with `ajv`, `ajv-formats`, `semver`, `jest`, and `husky`. Includes npm scripts for `test`, `test:contract`, `test:schema`, `test:policy`, `validate`, and `prepare`.
- `.nvmrc`: Node.js version pin (20)
- `SETUP.md`: Step-by-step credential and environment configuration guide covering Google Calendar OAuth2, Microsoft Outlook OAuth2, notification channel setup, and PostgreSQL logging
- `IMPLEMENTATION_GUIDE.md`: Structural guide for adapting the architecture to new projects. Includes reading order, build sequence, pre-launch checklist, and common mistakes.
- `examples/README.md`: Index of all example resources with a pattern coverage matrix
- `examples/redacted-error-handler.json`: Sanitized structural example of the error handler workflow. Covers failure capture, error classification, Path A catalog lookup, Path B AI-assisted repair, contract validation before re-execution, catalog promotion, escalation, and observability emission.
- `governance/pre-commit-contract-validator.js`: Structural example of the pre-commit validation script. Shows version bump checking and contract compliance validation at commit time.
- `tests/README.md`: Testing approach covering contract compliance, payload schema, and policy compliance test categories
- `tests/examples/contract-compliance.test.example.js`: Structural contract compliance test example showing guaranteed output field assertions, error shape validation, and version consistency checks
- `CHANGELOG.md`: This file
- `architecture/overview.md`: "Working Example" section cross-linking to `examples/scheduling-assistant/`
- `architecture/scheduling-pipeline.md`: "Working Example" section cross-linking to the importable n8n implementation
- `registry-pattern/example-registry-sanitized.json`: Added `routing_registry`, `workflow_registry`, and `error_type_registry` partitions to complete the registry SSOT illustration

### Changed
- `examples/scheduling-assistant/manifest.json`: Version bumped from `v1` to `v1.1.0` to match workflow file versions after the Merge node fix
- `examples/scheduling-assistant/workflows/06_notify.json`: Email Send node disabled by default and converted to a configurable placeholder. A note was added directing implementers to replace it with their delivery channel (Telegram, webhook, Slack, etc.).
- `governance/contracts-overview.md`: Added contract example cross-references to the enforcement section
- `.gitignore`: Expanded from a single entry to a comprehensive pattern set covering env files, OS artifacts, editor directories, and build outputs

### Fixed
- `examples/scheduling-assistant/README.md`: Removed internal project reference from the footer
- `examples/scheduling-assistant/workflows/04_conflict_scan.json`: Added Merge node (appendItems, typeVersion 3) to prevent zero-result calendar reads from halting execution
- `registry-pattern/ssot-pattern.md`: Added missing blank lines around the paragraph between the code block and the next section heading

---

## v2.1.0 (2026-01-15)

### Added
- `examples/scheduling-assistant/`: Complete 6-stage scheduling sub-pipeline with importable n8n workflow files
- `examples/scheduling-assistant/specs/event_payload.schema.json`: Shared JSON Schema for all pipeline stages
- `architecture/scheduling-pipeline.md`: Full design documentation for the scheduling sub-pipeline

### Changed
- `architecture/overview.md`: Added Caching Layer and Key Design Decisions sections

---

## v2.0.0 (2026-01-10)

### Added
- `registry-pattern/`: Registry-as-SSOT pattern documentation and sanitized example
- `governance/`: Agent contracts overview and routing/caching policy summary
- `architecture/integrations.md`: External integration map
- `architecture/observability.md`: Observability and logging strategy
- `architecture/error-handler.md`: Error handler design
- `architecture/diagrams/agent-topology.md`: Agent topology diagram

### Changed
- `architecture/overview.md`: Expanded to cover orchestrator responsibilities, domain agent table, voice pipeline, and caching layer

---

## v1.0.0 (2025-12-01)

### Added
- Initial repository structure
- `architecture/overview.md`: Core architecture overview
- `examples/redacted-orchestrator-workflow.json`: Sanitized orchestrator structural example
- `examples/redacted-workflow.json`: Sanitized domain agent structural example
- `examples/redacted-agent-contract.yaml`: Sanitized agent contract structural example
- `README.md`: Project overview and design principles
- `LICENSE.md`: CC BY-NC-ND 4.0
