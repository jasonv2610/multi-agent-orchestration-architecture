# Tests

This directory contains structural examples of the integration tests that enforce contract compliance before deployment.

---

## Testing Philosophy

Tests in this system have one primary job: **assert that every workflow's outputs conform to its declared agent contract**. This anchors the pre-commit gate — a workflow that passes contract tests can be committed; one that fails is blocked.

Three test categories cover the full contract surface:

| Category | What It Asserts | When It Runs |
|----------|----------------|--------------|
| **Contract compliance** | Workflow output fields match declared contract schema | Pre-commit, CI |
| **Payload schema** | Stage-to-stage payloads satisfy the shared event schema | Pre-commit, CI |
| **Policy compliance** | Routing, caching, and versioning rules are not violated | CI |

---

## Contract Compliance Tests

Contract compliance tests load a workflow file and validate that its response-formatter node's declared output fields match the agent's contract schema.

See `examples/contract-compliance.test.example.js` for the structural test pattern.

**What a passing test confirms:**
- All guaranteed output fields (`response_text`, `confidence`, `execution_status`) are declared
- No guaranteed fields have been renamed or removed
- The error shape matches the contract's declared error schema
- The contract version is consistent with the workflow's versionId

**What triggers a failure:**
- A response-formatter node missing a guaranteed output field
- An output field type mismatch vs the contract schema
- A workflow versionId that does not match the contract version it was validated against

---

## Payload Schema Tests

Payload schema tests validate that each pipeline stage's output conforms to the shared event payload schema (`specs/event_payload.schema.json`). These tests catch field renames, missing required fields, and type drift between stages.

**Test scope:** Each of the 6 scheduling assistant stages is tested with a fixture payload representing its expected output. The fixture is validated against the JSON Schema.

---

## Policy Compliance Tests

Policy compliance tests assert that workflow configuration files respect the declared system policies:

- **Routing policy** — No workflow contains a hardcoded agent endpoint; all routing uses registry lookup
- **Caching policy** — Cache TTL class references match the declared classes in the registry
- **Versioning policy** — No workflow's versionId is lower than or equal to its previous committed version

---

## Running Tests

```bash
# REDACTED: test runner command
# Example structure only — adapt to your test framework

npm test                    # run all tests
npm test -- --contract      # contract compliance only
npm test -- --payload       # payload schema only
npm test -- --policy        # policy compliance only
```

---

## Test File Naming Convention

```
tests/
├── README.md                               # This file
└── examples/
    └── contract-compliance.test.example.js  # Structural test example (redacted)
```

Production test files follow the same naming pattern with agent domain names in place of "example".
