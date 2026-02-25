# Registry as Single Source of Truth

## Problem

In workflow automation systems, environment-specific identifiers such as spreadsheet IDs, database names, folder ID, and API endpoints are often hardcoded directly inside workflow nodes. This introduces structural risk:

- Configuration values become duplicated across workflows
- Identifier changes require manual updates in multiple locations
- Stale or inconsistent references accumulate over time
- There is no authoritative map of system dependencies
  
Hardcoded identifiers increase coupling and reduce operational clarity.

## Pattern

The Registry-as-SSOT pattern centralizes all environment-specific identifiers in a dedicated configuration layer. Workflows reference logical keys rather than concrete values. At runtime, each workflow resolves logical keys against the registry before execution.

```
Workflow Node
    │
    │  "lookup: ops_spreadsheet"
    ▼
Registry Lookup
    │
    │  resolves → actual_spreadsheet_id
    ▼
Data Store Operation
```
This enforces indirection between workflow logic and environment configuration.
## Registry Structure

The registry is partitioned by responsibility:

| Registry | Holds |
|---|---|
| Data Store Registry | Spreadsheet IDs, database names, storage locations |
| Workflow Registry | Workflow names, IDs, version metadata |
| Routing Registry | Intent mappings and deterministic patterns |
| Error Type Registry | Error classifications and remediation mappings |
| Cache Registry | TTL class definitions and key format rules |
| Credential Registry | Logical credential names only |

Secrets are never stored in the registry. The registry maps logical identifiers to credentials managed externally by the workflow engine.

## Benefits

**Single update point** — Updating a spreadsheet ID requires modifying one registry entry. All dependent workflows automatically resolve the new value.

**Auditable configuration** — The registry provides a complete map of external dependencies without requiring inspection of workflow implementations.

**Environment Portable** — Transitioning between environments requires replacing the registry configuration rather than editing workflow nodes.

**Pre-deployment validation** — Registry entries are validated against declared schemas. Invalid configuration fails validation before deployment.

## Implementation Notes

- The registry is file-based and version-controlled alongside workflows
- A validation script verifies registry integrity during session initialization
- Deployment is blocked if workflows reference undefined keys
- The registry is configuration, not runtime state
