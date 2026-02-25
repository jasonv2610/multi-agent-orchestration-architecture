# Agent Topology

## Primary Flow

```
                    ┌───────────────────────────┐
  Text    ─────────▶│                           │
  Voice   ─────────▶│    Master Orchestrator    │
  Image   ─────────▶│   (Intent Classification) │
  MCP     ─────────▶│                           │
                    └────────────┬──────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
   Shortcode match?         LLM classify        Unknown intent
   (deterministic)         (GPT-4o routing)       → clarify
              │                  │
              └────────┬─────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐  ┌─────▼────┐  ┌────▼──────┐
    │Prod-    │  │ Finance  │  │Operations │  ...
    │uctivity │  │  Agent   │  │  Agent    │
    └────┬────┘  └─────┬────┘  └────┬──────┘
         │             │             │
         ▼             ▼             ▼
    [Data Store]  [Data Store]  [Data Store]
    (Registry-    (Registry-    (Registry-
     resolved)     resolved)     resolved)
         │             │             │
         └─────────────┼─────────────┘
                       │
                    Response
                       │
                    ┌──▼──────────────────┐
                    │  Format + Deliver   │
                    │  Text / Voice / TTS │
                    └─────────────────────┘
```

## Error Path

```
  Workflow Failure
         │
         ▼
  ┌──────────────┐
  │ Error Handler │
  │   (capture)  │
  └──────┬───────┘
         │
         ▼
  Known fix pattern? ──yes──▶ Apply fix ──▶ Validate ──▶ Re-execute
         │
         no
         │
         ▼
  AI-assisted repair ──▶ Apply fix ──▶ Validate ──▶ Re-execute
```

## Scheduling Sub-Pipeline

```
  Calendar Request
         │
         ▼
  01_intake ──▶ 02_extract_normalize ──▶ 03_validate
                                               │
                                               ▼
                          06_notify ◀── 05_route_export ◀── 04_conflict_scan
```

Each stage is a discrete, independently deployable unit connected by a shared event payload schema.
