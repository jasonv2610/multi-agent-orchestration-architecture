# Setup Guide

This document covers the tools used in this project and how to configure them for local use or to run the scheduling assistant pipeline against a live n8n instance.

---

## Tools Used

### Runtime

| Tool | Role | Version |
|------|------|---------|
| [n8n](https://n8n.io) | Workflow automation runtime — executes all pipeline stages | v1.0+ |
| [Google Calendar API](https://developers.google.com/calendar) | Calendar read (conflict scan) and write (event creation) | v3 |
| [Microsoft Outlook API](https://learn.microsoft.com/en-us/graph/api/resources/calendar) | Outlook Calendar event creation (optional alternative to Google) | MS Graph v1.0 |
| SMTP | Email notification delivery in stage 06 | Any provider |
| PostgreSQL | Optional persistent logging in stage 06 (disabled by default) | v13+ |

### Developer Interface

| Tool | Role |
|------|------|
| [Claude Code](https://claude.ai/claude-code) | AI-assisted development via CLI |
| [n8n MCP Server](https://github.com/leonardsellem/n8n-mcp-server) | MCP integration for Claude Code → n8n workflow management |
| Git | Version control for all workflow and architecture files |

---

## n8n Installation

### Option A — n8n Cloud (Recommended)

1. Create an account at [n8n.io](https://n8n.io)
2. No local installation required — workflows import directly via the UI

### Option B — Self-Hosted via Docker

```bash
docker volume create n8n_data

docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

Access the editor at `http://localhost:5678`.

### Option C — Self-Hosted via npm

```bash
npm install n8n -g
n8n start
```

---

## Credential Setup

All credentials are referenced by logical name in the workflow JSON. The actual secrets are stored in n8n's credential vault and never appear in workflow logic.

### Google Calendar OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable the **Google Calendar API**
3. Create OAuth 2.0 credentials (Web Application type)
4. Add authorized redirect URI: `https://<your-n8n-domain>/rest/oauth2-credential/callback`
5. In n8n: **Settings → Credentials → Add Credential → Google Calendar OAuth2 API**
   - Name it exactly: `Google Calendar OAuth2`
   - Enter Client ID and Client Secret
   - Click Connect and authorize

### Microsoft Outlook OAuth2 (Optional)

1. Go to [Azure Portal](https://portal.azure.com) → App Registrations → New Registration
2. Set redirect URI: `https://<your-n8n-domain>/rest/oauth2-credential/callback`
3. Under API Permissions, add: `Calendars.ReadWrite`, `offline_access`
4. In n8n: **Settings → Credentials → Add Credential → Microsoft Outlook OAuth2 API**
   - Name it exactly: `Microsoft Outlook OAuth2`
   - Enter Application (Client) ID and Client Secret

### SMTP

1. Obtain SMTP credentials from your email provider (Gmail, SendGrid, Postmark, etc.)
2. In n8n: **Settings → Credentials → Add Credential → SMTP**
   - Name it exactly: `SMTP Credentials`
   - Enter host, port, username, and password

---

## Import and Activate Workflows

1. In n8n, go to **Workflows → Import from File**
2. Import the 6 scheduling assistant workflows in order:
   ```
   01_intake.json
   02_extract_normalize.json
   03_validate.json
   04_conflict_scan.json
   05_route_export.json
   06_notify.json
   ```
3. After importing, note the **workflow ID** assigned by n8n to each stage (visible in the URL when editing: `/workflow/<id>`)

---

## Environment Variables

Set these in n8n: **Settings → Variables** (n8n Cloud) or via `.env` file (self-hosted).

```bash
# Workflow IDs — replace with the actual IDs assigned after import
WORKFLOW_ID_EXTRACT_NORMALIZE=<id of 02_extract_normalize>
WORKFLOW_ID_VALIDATE=<id of 03_validate>
WORKFLOW_ID_CONFLICT_SCAN=<id of 04_conflict_scan>
WORKFLOW_ID_ROUTE_EXPORT=<id of 05_route_export>
WORKFLOW_ID_NOTIFY=<id of 06_notify>

# Scheduling rules
CALENDAR_TIMEZONE=America/New_York
DEFAULT_MEETING_DURATION=30
WORKING_HOURS_START=09:00
WORKING_HOURS_END=17:00
MIN_LEAD_TIME_MINUTES=60

# Calendar routing
PREFERRED_CALENDAR_SYSTEM=google   # or: outlook

# Notifications
NOTIFICATION_EMAIL_FROM=noreply@yourcompany.com
```

---

## Activate Workflows

Activate in this order to avoid trigger errors:

1. `06_notify` → activate first (terminal stage, no outbound triggers)
2. `05_route_export` → activate
3. `04_conflict_scan` → activate
4. `03_validate` → activate
5. `02_extract_normalize` → activate
6. `01_intake` → activate last (webhook becomes live when this activates)

---

## Verify the Setup

Send a test request to the intake webhook:

```bash
curl -X POST https://<your-n8n-webhook-url>/webhook/scheduling/intake \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Schedule a 1 hour meeting with john@example.com tomorrow at 2pm",
    "requestor_email": "you@yourcompany.com",
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

Monitor execution progress in n8n: **Executions** tab for each workflow stage.

---

## Claude Code + MCP (Developer Interface)

To manage n8n workflows directly from Claude Code:

1. Install the [n8n MCP server](https://github.com/leonardsellem/n8n-mcp-server):
   ```bash
   npm install -g n8n-mcp-server
   ```

2. Add to your Claude Code MCP config (`~/.claude/claude_desktop_config.json` or equivalent):
   ```json
   {
     "mcpServers": {
       "n8n": {
         "command": "n8n-mcp-server",
         "env": {
           "N8N_API_URL": "https://<your-n8n-instance>/api/v1",
           "N8N_API_KEY": "<your-n8n-api-key>"
         }
       }
     }
   }
   ```

3. Restart Claude Code. You can now use natural language to inspect, update, and deploy workflows directly from the Claude Code CLI.

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| Webhook returns 404 | Confirm `01_intake` is activated; check the webhook URL matches `scheduling/intake` path |
| Stage 02–06 not triggering | Verify all `WORKFLOW_ID_*` env vars are set to the correct n8n IDs |
| Google Calendar errors | Re-authorize OAuth2 credential; check Calendar API is enabled in Google Cloud |
| Conflict scan runs but skips | Confirm Merge node is present in `04_conflict_scan`; check both inputs are wired |
| No email notifications | Verify SMTP credential; check `NOTIFICATION_EMAIL_FROM` is set |
| Enable debug logging | Set `N8N_LOG_LEVEL=debug` in your n8n environment |
