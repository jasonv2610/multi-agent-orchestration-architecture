# Agent Contracts - Overview

## Purpose

Each domain agent declares a formal input/output contract that specifies what the orchestrator must provide and what the agent guarantees in return. Contracts serve three functions:

1. **Validation gate** - pre-commit hooks reject workflow changes that break a declared contract
2. **Documentation** - contracts are the authoritative description of each agent's interface
3. **Testing anchor** - integration tests assert contract compliance before deployment

## Contract Structure

Every agent contract declares:

### Input Schema
- Required fields from the orchestrator dispatch payload
- Optional contextual fields (cache hints, priority flags)
- Data types and validation rules for each field

### Output Schema
- Guaranteed response fields (text response, confidence score)
- Optional enrichment fields (data written, sources cited, follow-up suggested)
- Error shape for failure cases

### Execution Constraints
- Maximum expected execution duration
- Caching eligibility (TTL class)
- Retry behavior on partial failure

---

## Contract Enforcement

Contracts are enforced at two points:

**At commit time** - A validation script checks all workflow JSON files against their declared contracts. Commits that produce contract violations are blocked.

**At runtime** - The orchestrator validates the dispatch payload before invoking an agent. Invalid payloads are rejected with a structured error rather than passed to the agent.

## Versioning

Contracts are versioned alongside workflows. A contract version increment is required whenever:

- A new required input field is added
- An existing output field is removed or renamed
- The error shape changes

Minor changes (e.g., adding optional fields or expanding enum values) do not require a version bump.

## See Also

- `governance/policy-summary.md` - routing, caching, and verification policies
- `examples/redacted-agent-contract.yaml` - sanitized example contract structure
