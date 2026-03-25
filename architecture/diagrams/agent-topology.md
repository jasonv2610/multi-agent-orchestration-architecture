# Agent Topology

## Primary Flow

```
<<<<<<< HEAD
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
=======
                    +---------------------------+
  Text    --------->|                           |
  Voice   --------->|    Master Orchestrator    |
  Image   --------->|   (Intent Classification) |
  MCP     --------->|                           |
                    +------------+--------------+
                                 |
              +------------------+------------------+
              |                  |                  |
   Shortcode match?         LLM classify        Unknown intent
   (deterministic)         (GPT-4o routing)       > clarify
              |                  |
              +--------+---------+
                       |
         +-------------+-------------+
         |             |             |
    +----▼----+  +-----▼----+  +----▼------+
    |Prod-    |  | Finance  |  |Operations |  ...
    |uctivity |  |  Agent   |  |  Agent    |
    +----+----+  +-----+----+  +----+------+
         |             |             |
>>>>>>> 421a0ce6258687ef4d2cea57badc917fb0f5eb8a
         ▼             ▼             ▼
    [Data Store]  [Data Store]  [Data Store]
    (Registry-    (Registry-    (Registry-
     resolved)     resolved)     resolved)
<<<<<<< HEAD
         │             │             │
         └─────────────┼─────────────┘
                       │
                    Response
                       │
                    ┌──▼──────────────────┐
                    │  Format + Deliver   │
                    │  Text / Voice / TTS │
                    └─────────────────────┘
=======
         |             |             |
         +-------------+-------------+
                       |
                    Response
                       |
                    +--▼------------------+
                    |  Format + Deliver   |
                    |  Text / Voice / TTS |
                    +---------------------+
>>>>>>> 421a0ce6258687ef4d2cea57badc917fb0f5eb8a
```

## Error Path

```
  Workflow Failure
<<<<<<< HEAD
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
=======
         |
         ▼
  +--------------+
  | Error Handler |
  |   (capture)  |
  +------+-------+
         |
         ▼
  Known fix pattern? --yes--> Apply fix --> Validate --> Re-execute
         |
         no
         |
         ▼
  AI-assisted repair --> Apply fix --> Validate --> Re-execute
>>>>>>> 421a0ce6258687ef4d2cea57badc917fb0f5eb8a
```

## Scheduling Sub-Pipeline

```
  Calendar Request
<<<<<<< HEAD
         │
         ▼
  01_intake ──▶ 02_extract_normalize ──▶ 03_validate
                                               │
                                               ▼
                          06_notify ◀── 05_route_export ◀── 04_conflict_scan
=======
         |
         ▼
  01_intake --> 02_extract_normalize --> 03_validate
                                               |
                                               ▼
                          06_notify ◀-- 05_route_export ◀-- 04_conflict_scan
>>>>>>> 421a0ce6258687ef4d2cea57badc917fb0f5eb8a
```

Each stage is a discrete, independently deployable unit connected by a shared event payload schema.

See `architecture/scheduling-pipeline.md` for full stage reference, event payload schema, and design decisions.
