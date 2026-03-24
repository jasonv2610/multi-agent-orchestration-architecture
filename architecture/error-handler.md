# Error Handler

The error handler is a dedicated recovery agent that intercepts workflow execution failures and applies structured remediation without blocking the primary execution path. It operates asynchronously: a failure in one workflow does not delay responses to concurrent requests.

---

## Design Principles

**Async and non-blocking.** The error handler runs on a separate execution path. When a workflow failure is routed to it, the originating request receives an immediate failure response to the user while recovery runs independently. This prevents a single degraded integration from cascading into visible latency for unrelated requests.

**Recover before escalating.** The handler exhausts all automated recovery options before surfacing a failure for human review. Human escalation is treated as a signal that the fix catalog needs expansion, not a routine outcome.

**Validate before re-executing.** No fix is applied directly. Every proposed fix, whether from the pattern catalog or AI-assisted repair, is validated against the declared agent contract before re-execution. This prevents a malformed repair from producing a second failure.

**Fix catalog over generalism.** Known error types are resolved by deterministic fix patterns, not by re-running LLM classification each time. The AI-assisted repair path exists only for errors with no catalog match. This keeps recovery fast and cost-efficient for common failure modes.

---

## Error Type Catalog

The error type registry is the authoritative catalog of classified failure patterns. Each entry maps an error type to a remediation strategy.

### Error Type Schema

```yaml
error_type: "string: unique identifier"
error_class: "transient | permanent | recoverable"
affected_component: "orchestrator | agent | data_store | integration | contract"
description: "string: human-readable description of the condition"
known_fix_pattern: "pattern_id or null"
retry_eligible: true | false
max_retries: integer
escalation_policy: "log_and_notify | immediate_escalation | silent_log"
```

### Error Classes

| Class | Behavior | Examples |
|-------|----------|---------|
| **Transient** | Retry eligible. Condition is expected to self-resolve. | Integration timeout, momentary data store unavailability, rate limit hit |
| **Permanent** | Not retry eligible. Condition will not change on retry. | Malformed input payload, invalid registry key reference, contract schema violation |
| **Recoverable** | Requires a fix before retry. Condition can be resolved with a targeted correction. | Stale registry reference, deprecated workflow node type, auth credential rotation needed |

### Example Catalog Entries (Structural, Values Redacted)

```yaml
- error_type: "data_store.timeout"
  error_class: transient
  affected_component: data_store
  description: "Data store operation did not complete within the configured execution window"
  known_fix_pattern: "retry_with_backoff"
  retry_eligible: true
  max_retries: 2
  escalation_policy: log_and_notify

- error_type: "contract.output_schema_violation"
  error_class: permanent
  affected_component: contract
  description: "Agent returned a response that does not conform to its declared output schema"
  known_fix_pattern: null
  retry_eligible: false
  max_retries: 0
  escalation_policy: immediate_escalation

- error_type: "registry.undefined_key"
  error_class: recoverable
  affected_component: orchestrator
  description: "Workflow references a registry key that does not exist in the current registry"
  known_fix_pattern: "registry_key_repair"
  retry_eligible: true
  max_retries: 1
  escalation_policy: immediate_escalation

- error_type: "integration.auth_failure"
  error_class: recoverable
  affected_component: integration
  description: "External service returned an authentication error"
  known_fix_pattern: "credential_refresh"
  retry_eligible: true
  max_retries: 1
  escalation_policy: log_and_notify
```

---

## Recovery Paths

### Path A: Known Fix Pattern

Applies when the classified error type has a `known_fix_pattern` entry in the catalog.

```
Failure captured
      │
      ▼
Error type classified against registry
      │
      ▼
Known fix pattern found?
      │
     yes
      │
      ▼
Retrieve fix pattern from catalog
      │
      ▼
Apply fix (deterministic, no LLM call)
      │
      ▼
Validate fix against agent contract
      │
  passes?
      │
     yes ──▶ Re-execute workflow ──▶ Log result
      │
      no ──▶ Escalate (fix produced invalid state)
```

**Fix pattern types (structural examples):**

| Pattern ID | Behavior |
|------------|---------|
| `retry_with_backoff` | Wait a configured delay, then re-attempt the failed operation unchanged |
| `registry_key_repair` | Look up the undefined key in a fallback registry partition; if found, substitute and re-execute |
| `credential_refresh` | Trigger a credential refresh via the engine's credential manager, then re-execute |
| `cache_bypass` | Mark the specific cache key as invalid, force a fresh execution, repopulate cache |
| `payload_sanitize` | Apply a declared sanitization transform to the input payload before re-execution |

---

### Path B: AI-Assisted Repair

Applies when no known fix pattern matches the classified error type, or when the error type is unclassified.

```
Failure captured
      │
      ▼
Error type classified against registry
      │
      ▼
Known fix pattern found?
      │
      no
      │
      ▼
Capture failure context:
  - Error message and stack trace (sanitized)
  - Workflow node type and version
  - Input payload structure (values redacted)
  - Agent contract for the failing component
  - Last successful execution state
      │
      ▼
Submit context to repair model
      │
      ▼
Repair model returns proposed fix
      │
      ▼
Validate proposed fix against agent contract
      │
  passes?
      │
     yes ──▶ Apply fix ──▶ Re-execute ──▶ If successful: add to fix catalog
      │
      no ──▶ Retry repair (up to max_retries)
              │
              still failing after max_retries
              │
              ▼
          Human escalation
```

**Repair model context structure:**

The context sent to the repair model is scoped to what is strictly necessary. This keeps the repair call focused and reduces hallucination surface.

```json
{
  "error_type": "classified error type or 'unclassified'",
  "error_message": "sanitized error description",
  "failed_node_type": "workflow node type identifier",
  "failed_node_version": "semver string",
  "input_payload_schema": "structure only, no values",
  "contract_ref": "agent contract schema for the failing component",
  "last_successful_execution": "ISO 8601 timestamp"
}
```

**Catalog expansion:** When AI-assisted repair produces a successful fix, the fix pattern is promoted to the catalog with a human review flag. After a configurable number of successful applications without regression, it graduates to a confirmed catalog entry and becomes a Path A fix for subsequent occurrences.

---

## Retry Policy

Retry limits are declared per agent in the agent contract:

```yaml
constraints:
  retry_on_partial_failure: true
  max_retries: 2
```

The error handler respects the contract's `max_retries` value. It does not override agent-level limits with a system-level default. This lets agents with higher failure tolerance (e.g., async logging) configure more retries than agents where strict execution order matters (e.g., scheduling writes).

**Retry state tracking:** Each retry attempt decrements the remaining retry count in the execution context. The handler does not restart the counter on a new fix attempt. Retries are consumed across both Path A and Path B attempts within a single failure event.

---

## Escalation

When all recovery options are exhausted, the error handler produces a structured escalation record:

```json
{
  "escalation_id": "string",
  "timestamp": "ISO 8601",
  "error_type": "string",
  "error_class": "transient | permanent | recoverable",
  "affected_component": "string",
  "recovery_attempts": [
    {
      "path": "A | B",
      "fix_applied": "pattern ID or 'ai_generated'",
      "validation_result": "passed | failed",
      "re_execution_result": "success | failed"
    }
  ],
  "retries_consumed": "integer",
  "escalation_policy": "log_and_notify | immediate_escalation | silent_log",
  "recommended_action": "string, generated by repair model or catalog"
}
```

Escalations are written to the error log data store and, depending on escalation policy, trigger a notification. `immediate_escalation` errors produce an alert synchronously. `log_and_notify` errors are batched into a review queue.

---

## Relationship to Observability

The error handler emits structured events at each decision point for the observability layer:

- Error captured (type, class, component)
- Path selected (A or B)
- Fix applied (pattern ID or AI-generated)
- Validation result
- Re-execution result
- Retry count consumed
- Escalation triggered (if applicable)

These events feed the Error Recovery dashboard in `architecture/observability.md`. The known-pattern match rate and AI-assisted repair success rate metrics are derived entirely from error handler event emissions.
