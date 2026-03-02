# Scheduling Assistant

An intelligent scheduling workflow system that processes scheduling requests, validates availability, detects conflicts, and manages calendar integrations.

## Purpose

The Scheduling Assistant automates the entire scheduling pipeline from intake to confirmation, handling:
- Scheduling request intake and parsing
- Data extraction and normalization
- Availability validation
- Conflict detection and resolution
- Multi-platform calendar routing
- Notification and confirmation delivery

## Architecture

The Scheduling Assistant is composed of 6 modular n8n workflows, each independently deployable and connected by a shared event payload schema.

### Workflow Pipeline

```
01_intake.json
    ↓
02_extract_normalize.json
    ↓
03_validate.json
    ↓
04_conflict_scan.json
    ↓
05_route_export.json
    ↓
06_notify.json
```

### Workflow Descriptions

| Workflow | Purpose | Key Functions |
|----------|---------|---------------|
| **01_intake** | Request Reception | Webhook listener, initial validation, queue management |
| **02_extract_normalize** | Data Processing | NLP extraction, datetime parsing, attendee normalization |
| **03_validate** | Business Logic Validation | Working hours check, duration validation, attendee verification |
| **04_conflict_scan** | Conflict Detection | Calendar scanning, overlap detection, alternative suggestions |
| **05_route_export** | Calendar Integration | Google/Outlook routing, event creation, sync management |
| **06_notify** | Notifications | Email confirmation, calendar invites, reminder scheduling |

## Folder Structure

```
scheduling-assistant/
├── README.md                    # This file
├── manifest.json                # Pipeline metadata and rules
├── specs/
│   └── event_payload.schema.json  # Shared payload schema across all stages
└── workflows/
    ├── 01_intake.json
    ├── 02_extract_normalize.json
    ├── 03_validate.json
    ├── 04_conflict_scan.json
    ├── 05_route_export.json
    └── 06_notify.json
```

## Getting Started

### Prerequisites
- n8n instance (v1.0+)
- Calendar API credentials (Google Calendar, Outlook, or both)
- SMTP credentials for email notifications
- PostgreSQL database (optional — for persistent logging)

### Installation

1. **Import Workflows** — Use the n8n UI: Settings → Import from File. Import all 6 workflows in order.

2. **Configure Credentials** in n8n:
   - `Google Calendar OAuth2` — for Google Calendar read/write
   - `Microsoft Outlook OAuth2` — for Outlook Calendar (optional)
   - `SMTP Credentials` — for email notification delivery

3. **Set Environment Variables**:
   ```bash
   WORKFLOW_ID_EXTRACT_NORMALIZE=<n8n workflow ID for stage 02>
   WORKFLOW_ID_VALIDATE=<n8n workflow ID for stage 03>
   WORKFLOW_ID_CONFLICT_SCAN=<n8n workflow ID for stage 04>
   WORKFLOW_ID_ROUTE_EXPORT=<n8n workflow ID for stage 05>
   WORKFLOW_ID_NOTIFY=<n8n workflow ID for stage 06>

   CALENDAR_TIMEZONE=America/New_York
   DEFAULT_MEETING_DURATION=30
   WORKING_HOURS_START=09:00
   WORKING_HOURS_END=17:00
   MIN_LEAD_TIME_MINUTES=60
   PREFERRED_CALENDAR_SYSTEM=google
   NOTIFICATION_EMAIL_FROM=noreply@yourcompany.com
   ```

4. **Activate Workflows** — Start with `01_intake.json`, then activate remaining stages.

### Testing

Send a test scheduling request:
```bash
curl -X POST <SCHEDULING_WEBHOOK_URL> \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Schedule a meeting with John tomorrow at 2pm for 1 hour",
    "requestor_email": "user@example.com",
    "meeting_type": "general"
  }'
```

Expected response (HTTP 202):
```json
{
  "success": true,
  "requestId": "REQ-1234567890-abc123",
  "status": "queued",
  "message": "Scheduling request received and queued for processing",
  "timestamp": "2026-01-19T20:00:00.000Z"
}
```

## Data Flow

Each stage reads from and appends to a shared payload object. No stage modifies fields written by earlier stages.

```json
{
  "requestId": "REQ-timestamp-random",
  "rawRequest": "original input text",
  "requestorEmail": "requester@example.com",
  "meetingType": "general | interview | sync | review | presentation | workshop",
  "priority": "low | normal | high | urgent",
  "extracted": { "title", "dateTime", "duration", "attendees", "location" },
  "normalized": { "startTime", "endTime", "duration", "attendees", "timezone" },
  "validation": { "isValid", "errors", "warnings", "checks" },
  "conflictScan": { "hasConflicts", "conflicts", "alternatives" },
  "routing": { "targetSystem", "routingReason" },
  "export": { "eventId", "eventUrl", "calendarSystem" },
  "notification": { "type", "recipients", "sent", "confirmationCode" },
  "stage": "current pipeline stage",
  "pipeline_status": "complete | failed | clarification_required"
}
```

See `specs/event_payload.schema.json` for the full JSON Schema definition.

## Design Decisions

**Workflow IDs via environment variables** — Stage-to-stage triggers use `$env.WORKFLOW_ID_*` references. No workflow contains hardcoded IDs for other workflows.

**Credential references by name** — All calendar and SMTP credentials are referenced by logical name, resolved by the n8n engine at runtime. No secrets are embedded in workflow logic.

**Validation before calendar access** — Stages 01–03 perform no calendar reads or writes. Calendar operations begin only at stage 04, after business logic validation passes.

**Conflict resolution produces alternatives** — Stage 04 does not hard-block on conflicts. It generates up to 3 alternative time suggestions (earlier same day, later same day, same time next day) and routes to notification so the requestor can choose.

**Notification decoupled from write** — Stage 06 is independent from stage 05. A notification failure does not roll back the calendar event.

**Optional database logging** — The Postgres node in stage 06 is disabled by default. Enable it if persistent scheduling logs are required.

## Troubleshooting

| Issue | Check |
|-------|-------|
| Webhook not triggering | Verify webhook URL is accessible; confirm workflow is activated |
| Date/time parsing errors | Check `CALENDAR_TIMEZONE` env var; review stage 02 extraction logic |
| Calendar API errors | Verify OAuth credentials; check API rate limits and calendar permissions |
| Notification failures | Verify SMTP credentials; check recipient addresses |

Enable debug logging: `N8N_LOG_LEVEL=debug`

## Version History

### v1 (Current)
- 6-stage pipeline
- Google Calendar and Outlook support
- Email notifications via SMTP
- NLP-based date/time extraction
- Conflict detection with alternative suggestions

### Planned (v2)
- AI-powered smart scheduling
- Multi-timezone support
- Recurring meeting automation
- Video conferencing platform integration

---

**Version:** 1.0.0 | **Part of:** JVI Multi-Agent Orchestration System
