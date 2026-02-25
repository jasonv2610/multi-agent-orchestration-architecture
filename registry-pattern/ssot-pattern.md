# Registry as Single Source of Truth

## Problem

In workflow automation systems, data store references — spreadsheet IDs, database connection strings, folder identifiers, API endpoint URLs — are commonly hardcoded directly inside workflow nodes. This creates several failure modes:

- Configuration values are duplicated across dozens of nodes and workflows
- A single ID change requires hunting down every reference manually
- The same ID may appear differently in different workflows (stale copies)
- There is no authoritative record of what connects to what

## Pattern

The Registry-as-SSOT pattern centralizes all environment-specific identifiers in a dedicated registry layer. Workflows never contain hard values for data store references — they contain only logical keys. At runtime, each workflow resolves its logical keys against the registry before executing.

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

## Registry Structure

The registry is split by concern:

| Registry | Holds |
|---|---|
| Data Store Registry | Spreadsheet IDs, database names, Drive folder IDs |
| Workflow Registry | Workflow names, IDs, version metadata |
| Routing Registry | Shortcode patterns, intent-to-agent mappings |
| Error Type Registry | Error patterns and associated fix strategies |
| Cache Registry | TTL class definitions and key format rules |
| Credential Registry | Logical credential names (no secrets — just names) |

Secrets are never stored in the registry. The registry holds logical names that map to credentials configured separately in the workflow engine.

## Benefits

**Single update point** — Changing a spreadsheet ID means updating one registry entry. All workflows that reference that logical key automatically resolve the new value.

**Auditable** — The registry is a complete map of what the system connects to. A new team member can read the registry to understand all external dependencies without reading individual workflows.

**Portable** — Moving from one environment to another (staging → production) requires only a registry swap, not editing individual workflow nodes.

**Validated** — Registry entries can be validated against known schemas. Malformed entries fail validation before deployment, not at runtime.

## Implementation Notes

- The registry is file-based and version-controlled alongside workflows
- A startup validation script verifies registry integrity on session open
- Workflows are blocked from deployment if they reference unregistered keys
- The registry is not a database — it is a structured configuration artifact, not runtime state
