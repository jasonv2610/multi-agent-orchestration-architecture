# Scheduling Sub-Pipeline

The scheduling sub-pipeline is a dedicated linear workflow that handles all calendar and time-based coordination requests. It operates independently from the main orchestration loop, applying a stage-gated processing model where each stage must complete and validate before the next executes.

---

## Why a Separate Pipeline

Scheduling requests have structural properties that make them a poor fit for the standard intent-dispatch model:

- They require multi-step normalization before any business logic can run (raw date expressions must be parsed before conflict checking is possible)
- They carry temporal side effects — a failed write mid-pipeline should not silently leave a partial state
- They involve external calendar coordination, which introduces variable latency not suitable for the synchronous agent-dispatch path

Isolating scheduling into its own pipeline keeps the main orchestrator stateless and fast, and allows each scheduling stage to be retried, replaced, or scaled independently.

---

## Pipeline Stages

```
  Calendar Request
        │
        ▼
  ┌─────────────┐
  │  01_intake  │  Receive, validate structure, attach metadata
  └──────┬──────┘
         │
         ▼
  ┌────────────────────────┐
  │  02_extract_normalize  │  Parse entities, normalize to standard schema
  └──────────┬─────────────┘
             │
             ▼
  ┌──────────────┐
  │  03_validate │  Apply business rules to normalized entities
  └──────┬───────┘
         │
         ▼
  ┌──────────────────┐
  │  04_conflict_scan│  Check for scheduling conflicts in data store
  └──────┬───────────┘
         │
         ▼
  ┌──────────────────┐
  │  05_route_export │  Write event, return confirmation + event ID
  └──────┬───────────┘
         │
         ▼
  ┌─────────────┐
  │  06_notify  │  Dispatch notifications to participants
  └─────────────┘
```

Each stage is a discrete, independently deployable unit. Stages communicate exclusively through the shared event payload schema — no stage holds a reference to another.

---

## Stage Reference

### 01 — Intake

**Purpose:** Accept the raw scheduling request, confirm minimum required fields are present, attach pipeline metadata before any processing begins.

**Inputs:** Raw request (text or structured) from orchestrator dispatch

**Outputs:** Structured intake payload with pipeline metadata attached

**Adds to payload:**
- `request_id` — unique identifier for this pipeline run
- `received_at` — ISO 8601 timestamp
- `source_channel` — originating input channel (text, voice, MCP)
- `raw_input` — preserved for audit

**Failure behavior:** Hard stop — malformed or incomplete intake does not enter the pipeline. Returns structured error to orchestrator.

---

### 02 — Extract and Normalize

**Purpose:** Parse all date/time expressions, extract structured entities, and normalize to the canonical payload schema. This is the only stage that performs linguistic and temporal interpretation.

**Inputs:** Intake payload from 01

**Outputs:** Normalized entity payload

**Extracts and normalizes:**
- Date and time expressions → ISO 8601 with timezone
- Relative expressions ("next Thursday", "end of month") → absolute values
- Duration (explicit or implied)
- Participant identifiers
- Location or resource references
- Recurrence pattern (if any)

**Design note:** All temporal ambiguity is resolved here. Downstream stages treat all datetime values as already normalized — they do not re-interpret natural language.

**Failure behavior:** If extraction produces insufficient entities to proceed (e.g., date is unresolvable), the pipeline halts and returns a clarification request to the user via the orchestrator.

---

### 03 — Validate

**Purpose:** Apply business rules to the normalized entities before any data store interaction occurs.

**Inputs:** Normalized entity payload from 02

**Validation checks:**
- Date is not in the past (for new events)
- Duration is within configured bounds
- Participant identifiers resolve to known records
- Resource identifiers resolve to known resources
- Recurrence pattern (if present) is structurally valid

**Outputs:** Validated payload — unchanged entity data, validation status appended

**Failure behavior:** Validation failures are returned as structured errors with the specific rule violated. The pipeline does not proceed to conflict scanning on a validation failure.

---

### 04 — Conflict Scan

**Purpose:** Query the calendar data store to detect scheduling conflicts before any write is attempted.

**Inputs:** Validated payload from 03

**Checks:**
- Existing events occupying the same time window for any participant
- Resource or room double-booking
- Participant availability blocks (if declared)
- Recurrence expansion conflicts (checks all occurrences, not just the first)

**Conflict resolution options (policy-configured):**
- Hard block — pipeline halts, conflict details returned to user
- Soft warning — conflict flagged in payload but pipeline continues
- Auto-reschedule — next available slot is proposed (if enabled by routing policy)

**Outputs:** Conflict-free validated payload, or conflict report

**Design note:** This stage is read-only. No writes occur before 05. This preserves a clean rollback state if validation or conflict checks fail.

---

### 05 — Route and Export

**Purpose:** Write the confirmed event to the appropriate calendar data store and return a structured confirmation.

**Inputs:** Conflict-free validated payload from 04

**Operations:**
- Resolves destination calendar via registry lookup (no hardcoded data store references)
- Writes event with full normalized payload as structured record
- Generates event ID
- Appends write confirmation to payload

**Outputs:** Export confirmation payload including event ID, write timestamp, and data store reference

**Failure behavior:** On write failure, the pipeline triggers the system error handler. The event is not partially written — if the write does not confirm, no downstream notification is sent.

---

### 06 — Notify

**Purpose:** Dispatch notifications to all participants and return final pipeline status to the orchestrator.

**Inputs:** Export confirmation payload from 05

**Operations:**
- Resolves participant notification channels via registry
- Dispatches confirmation to each participant
- Formats response for return to the originating user

**Outputs:** Final pipeline response (success + event ID + notification status)

**Design note:** Notification failures do not roll back the event write. The event is considered created once 05 completes. 06 failures are logged and can be retried independently without re-running the full pipeline.

---

## Shared Event Payload Schema

All stages read from and write to a single payload object. Each stage appends its outputs without modifying fields set by earlier stages, preserving a full audit trail within the payload.

```json
{
  "request_id": "string — pipeline run identifier",
  "received_at": "ISO 8601 timestamp",
  "source_channel": "text | voice | mcp",
  "raw_input": "string — preserved from intake",

  "entities": {
    "title": "string",
    "start": "ISO 8601 with timezone",
    "end": "ISO 8601 with timezone",
    "duration_minutes": "integer",
    "participants": ["array of resolved identifiers"],
    "location": "string or null",
    "recurrence": "recurrence pattern object or null"
  },

  "validation_status": "passed | failed",
  "validation_errors": ["array — populated if failed, empty if passed"],

  "conflict_status": "clear | conflict | warning",
  "conflicts": ["array — populated if conflicts found, empty if clear"],

  "export": {
    "event_id": "string — assigned by data store on write",
    "written_at": "ISO 8601 timestamp",
    "data_store_ref": "logical registry key — not the raw ID"
  },

  "notifications": {
    "dispatched_to": ["array of participant identifiers"],
    "status": "sent | partial | failed"
  },

  "pipeline_status": "complete | failed | clarification_required",
  "failed_at_stage": "stage name or null"
}
```

---

## Design Decisions

**Linear over parallel** — Each stage depends on the output of the previous. Normalization must complete before validation; validation must pass before conflict scanning; conflict scanning must clear before writing. Parallelism is not applicable to a dependency chain.

**Read-only until stage 05** — Stages 01 through 04 perform no data store writes. This keeps the pipeline reversible until the conflict check passes. There is no partial-write state to clean up on failure.

**Payload immutability per stage** — Each stage appends to the payload rather than overwriting earlier fields. This preserves the full processing history for debugging and audit without requiring a separate log.

**Independent deployability** — Stages share no runtime references to each other. The payload schema is the only coupling point. Any stage can be replaced, scaled, or retried without modifying adjacent stages.

**Notification decoupled from write** — Stage 06 is intentionally separated from stage 05. The event exists in the data store once 05 completes. Notification delivery is a best-effort, independently retriable operation that does not affect the calendar record.

---

## Working Example

An importable n8n implementation of this pipeline is available in `examples/scheduling-assistant/`. The 6 workflow files map directly to the stages described above — each file is a self-contained, independently deployable n8n workflow that applies the same patterns documented here (registry-resolved config, spec-defined payload schema, stage-gated execution).

See `examples/scheduling-assistant/README.md` for setup instructions and `examples/scheduling-assistant/specs/event_payload.schema.json` for the full payload schema.
