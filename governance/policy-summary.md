# Policy Summary

Four system-level policies govern runtime behavior. Each policy is declared as a spec file and enforced by the validation layer.

---

## Routing Policy

Defines how the orchestrator maps incoming intent to a target agent.

**Deterministic routing** — Shortcode patterns are matched before any LLM call. Matched patterns route directly to the target agent without AI classification overhead.

**LLM routing** — Unmatched inputs are classified by the LLM router. The router returns:
- `target_agent` — the resolved domain agent
- `confidence` — classification confidence score (0.0–1.0)
- `parameters` — extracted structured fields

**Confidence threshold** — Inputs classified below the configured threshold are not dispatched to an agent. The orchestrator instead returns a clarification request to the user.

**Fallback** — If no agent domain matches clearly, the orchestrator returns a clarification request rather than routing on an ambiguous classification.

---

## Caching Policy

Defines response cache behavior by data volatility class.

| TTL Class | Behavior | Applies To |
|---|---|---|
| No-cache | Never stored | Real-time status, live prices |
| Short | Expires in minutes | Inventory state, availability |
| Medium | Expires in hours | General query responses |
| Long | Expires in days | Research summaries, analysis |
| Reference | Expires in a week | Definitions, how-to content |

Cache keys are scoped to agent, user context, and a query hash. User-specific data is never shared across cache contexts.

---

## Verification Policy

Defines anti-hallucination controls for AI-generated responses.

**Confidence thresholds** — Each agent type has a configured minimum confidence for its LLM calls. Responses below threshold are flagged or suppressed.

**Clarification trigger** — When the system cannot produce a high-confidence response, it generates a clarification request rather than a low-confidence answer.

---

## Versioning Policy

Defines how workflow and contract versions are managed.

**Version format** — Semantic versioning (major.minor.patch) applied to each workflow independently.

**Validation gate** — A pre-commit script validates that all modified workflows carry a version increment. Commits that modify workflow logic without a version bump are blocked.

**No-deletion rule** — Workflows and agent nodes are never deleted from the production environment. Deprecated logic is deactivated or superseded, not removed. This prevents irreversible state loss.

**Minimal-delta updates** — When modifying a live workflow, only the changed parameters are updated. Full workflow replacement is avoided to minimize blast radius.
