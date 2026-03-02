# Observability

Observability in a multi-agent orchestration system requires instrumentation at each architectural layer. A single metric point (e.g., end-to-end latency) is insufficient to distinguish between a slow LLM call, a cache miss, an agent data store bottleneck, and a notification delivery delay. Each layer must be independently observable.

This document defines the signal taxonomy, alert thresholds, and dashboard structure for the system.

---

## Signal Taxonomy

### Routing Layer

The routing layer is the highest-leverage observation point. Problems here affect every downstream agent.

| Signal | Type | What It Tells You |
|--------|------|-------------------|
| Intent classification confidence distribution | Histogram | Proportion of inputs resolved with high vs. low confidence. A shift toward lower confidence indicates input pattern drift or model degradation. |
| Shortcode hit rate | Rate | Percentage of inputs resolved deterministically. A drop here increases LLM calls and latency. |
| LLM classification call rate | Rate | Volume of inputs requiring AI classification. Rising rate with flat shortcode hit rate indicates new input patterns not yet mapped to shortcodes. |
| Clarification request rate | Rate | Percentage of inputs that triggered a clarification rather than a routing decision. Sustained high rate indicates routing policy needs tuning. |
| Routing latency (p50 / p95 / p99) | Latency | End-to-end time from input receipt to agent dispatch. Separates orchestrator overhead from agent execution time. |
| Unknown intent rate | Rate | Inputs that matched no shortcode and produced no classifiable intent. These should trend toward zero over time as routing coverage expands. |

---

### Agent Layer

Each domain agent is independently observable. Aggregate metrics mask domain-specific issues.

| Signal | Type | Dimensions |
|--------|------|------------|
| Agent execution latency | Latency (p50/p95/p99) | Per agent domain |
| Execution status distribution | Rate | success / partial / failed — per agent domain |
| Data store write rate | Rate | Per agent domain — distinguishes read-heavy from write-heavy agents |
| Cache hit rate | Rate | Per agent domain — see Cache Layer for full detail |
| LLM calls per agent execution | Count | Per agent domain — agents with high LLM call counts per execution have higher cost and latency variance |
| Follow-up suggested rate | Rate | Per agent domain — indicates how often agents return open-ended rather than terminal responses |

**Why per-domain:** A failure in the Finance Agent has different severity and remediation than a failure in the Intelligence Agent. Aggregated agent metrics mask the domain context needed for diagnosis.

---

### Cache Layer

Cache behavior directly affects perceived response latency and LLM call volume. Observing it independently reveals whether slowdowns are execution problems or cache configuration problems.

| Signal | Type | What It Tells You |
|--------|------|-------------------|
| Cache hit rate by TTL class | Rate | Whether TTL assignments match actual data volatility. A high miss rate on a "long" TTL class indicates data is changing faster than the policy assumes. |
| Cache miss rate by agent | Rate | Per-agent misses reveal which domains generate the most uncached LLM calls. |
| Cache key collision rate | Rate | Unexpected collisions indicate key format issues in the scoping logic. |
| Cache eviction rate | Rate | High eviction rate against a constrained cache budget indicates TTL or capacity tuning is needed. |
| Stale-read frequency | Rate | Reads that hit cache but return data whose underlying source has since changed. Indicates TTL classes set too long for specific domains. |

---

### Error Layer

The error handler's effectiveness is measured by how much work it absorbs without human intervention.

| Signal | Type | What It Tells You |
|--------|------|-------------------|
| Error rate by type | Rate | Distribution across the error type registry. Concentration in one type indicates a systemic issue. |
| Known-pattern match rate | Rate | Percentage of errors resolved via the fix pattern catalog vs. requiring AI-assisted repair. Declining rate indicates new error patterns emerging. |
| AI-assisted repair success rate | Rate | Percentage of AI-repair attempts that produce a valid fix. Low rate indicates the repair model needs additional context or the error type is fundamentally non-recoverable. |
| Retry consumption rate | Rate | How often errors exhaust max_retries. Consistently hitting max_retries before resolution signals a need to expand the fix catalog. |
| Human escalation rate | Rate | Errors that exhaust all recovery options. This metric should trend toward zero as the fix catalog grows. |
| Mean time to recovery (MTTR) | Duration | Per error type — separates fast-recovering transient errors from slow-recovering structural ones. |

---

### System Health

Top-level signals for operational monitoring.

| Signal | Type | What It Tells You |
|--------|------|-------------------|
| End-to-end latency (p50 / p95 / p99) | Latency | Full cycle from input receipt to response delivery. Baseline for detecting systemic slowdowns. |
| Workflow execution queue depth | Gauge | Buildup indicates throughput constraint — either in the orchestrator, an agent, or an external integration. |
| Pipeline stage latency — scheduling sub-pipeline | Latency per stage | Isolates which scheduling stage is the bottleneck when scheduling requests are slow. |
| Active workflow count | Gauge | Concurrent executions. Useful for capacity planning and detecting runaway loops. |
| Version validation failures at commit | Count | Pre-commit gate rejections. Persistent failures indicate contract drift or team process issues. |

---

## Alert Thresholds

Thresholds are policy-configured and adjusted based on observed baselines. The values below are structural examples, not production targets.

| Condition | Threshold | Severity | Response |
|-----------|-----------|----------|----------|
| Classification confidence < threshold on sustained % of requests | Configurable % over rolling window | Warning | Review routing policy and shortcode coverage |
| Agent failure rate exceeds threshold for any single domain | Configurable % over rolling window | Critical | Trigger agent health check; inspect data store and contract compliance |
| Cache hit rate drops below baseline | Configurable % drop from 7-day average | Warning | Review TTL class assignments for affected agents |
| AI-assisted repair success rate drops below threshold | Configurable % | Warning | Expand error type catalog; review repair prompt context |
| Human escalation rate exceeds threshold | Any sustained rate above near-zero | Critical | Immediate investigation; indicates unknown error class not covered by catalog |
| End-to-end latency p99 exceeds threshold | Configurable ms | Warning | Layer-by-layer latency review to isolate bottleneck |
| Execution queue depth exceeds threshold | Configurable queue depth | Warning | Throughput investigation; may indicate agent or integration bottleneck |

---

## Dashboard Structure

Four dashboards cover the full observability surface. Each is independent — an operator can load the routing dashboard without the agent dashboard loading unnecessary data.

### Dashboard 1 — System Health Overview

Single-pane summary for operational awareness:
- End-to-end latency trends (p50 / p95 / p99)
- Active workflow count
- Global error rate and human escalation count
- Shortcode hit rate vs. LLM call rate ratio
- Top 3 slowest agents (current rolling window)

### Dashboard 2 — Routing Layer

Deep routing observability:
- Confidence distribution histogram (live and 7-day trend)
- Shortcode hit rate vs. LLM call rate over time
- Clarification request rate and unknown intent rate
- Routing latency breakdown (shortcode path vs. LLM path)
- Most frequent unresolved intent patterns

### Dashboard 3 — Agent Performance

Per-domain agent health:
- Execution status distribution per agent (success / partial / failed)
- Execution latency per agent (p50 / p95 / p99)
- Cache hit rate per agent
- LLM calls per execution per agent
- Data write rate per agent

### Dashboard 4 — Error Recovery

Error handler effectiveness:
- Error rate by type (stacked bar, rolling window)
- Known-pattern match rate vs. AI-repair rate
- AI-assisted repair success rate trend
- Retry consumption rate by agent domain
- Human escalations (count and context log)
- MTTR by error type

---

## Instrumentation Points

Each architectural component has a defined set of events to emit:

| Component | Events to Instrument |
|-----------|---------------------|
| Orchestrator — routing layer | Input received, shortcode match result, LLM call dispatched, confidence score, agent dispatched, clarification triggered |
| Each domain agent | Execution started, cache check result, LLM call (if applicable), data store read/write, execution status, response returned |
| Cache layer | Cache hit, cache miss, cache write, eviction |
| Error handler | Error captured, error type classified, fix pattern matched (or not), repair attempted, repair result, retry count, escalation |
| Scheduling sub-pipeline | Stage entered, stage completed, stage failed, conflict found, export written, notification dispatched |
| Pre-commit validation gate | Validation run, violations found (with type), commit blocked |

All events include: `timestamp`, `workflow_id`, `agent_domain` (where applicable), `execution_id` for correlation across a single request lifecycle.
