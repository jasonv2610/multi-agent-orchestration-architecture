# Setup Guide

This document covers the tools used in this project and how to configure them for local use or to run the scheduling assistant pipeline against a live n8n instance.

---

## Tools Used

These are the external services and credentials used directly by the 6 scheduling assistant workflow files in this repository.

### Runtime

| Tool | Used In | Role | Credential Type |
|------|---------|------|-----------------|
| [n8n](https://n8n.io) | All stages | Workflow automation runtime — executes all pipeline stages | — |
| [Google Calendar API](https://developers.google.com/calendar/api/guides/overview) | Stage 04, 05 | Stage 04: reads existing events to detect conflicts. Stage 05: creates new calendar events and sends invitations. | Google Calendar OAuth2 |
| [Microsoft Outlook API](https://learn.microsoft.com/en-us/graph/api/resources/calendar) | Stage 05 | Alternative calendar — creates Outlook events when attendee domain is Microsoft. Optional; Google Calendar is the default. | Microsoft Outlook OAuth2 |
| SMTP | Stage 06 | Sends email notifications (confirmation, conflict alert, validation failure) to requestor. | SMTP |
| PostgreSQL | Stage 06 | Persists scheduling logs to a database table. **Disabled by default** — enable the node in stage 06 only if you need persistent logs. | Postgres |

### Developer Interface

| Tool | Role | Where to Get |
|------|------|--------------|
| [Claude Code](https://claude.ai/claude-code) | AI-assisted development via CLI | [claude.ai/claude-code](https://claude.ai/claude-code) |
| [n8n MCP Server](https://github.com/leonardsellem/n8n-mcp-server) | Connects Claude Code to n8n for workflow inspection and management | [github.com/leonardsellem/n8n-mcp-server](https://github.com/leonardsellem/n8n-mcp-server) |
| Git | Version control for all workflow, contract, and governance files | [git-scm.com](https://git-scm.com) |

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

The credential names below must match **exactly** — the workflow files reference them by these names.

---

### 1. Google Calendar OAuth2

**Used in:** Stage 04 (conflict scan — read), Stage 05 (event creation — write)

**How to obtain:**

1. Go to [Google Cloud Console](https://console.cloud.google.com) and create or select a project
2. Navigate to **APIs & Services → Library** and enable the **Google Calendar API**
3. Navigate to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
   - Application type: **Web application**
   - Add authorized redirect URI: `https://<your-n8n-domain>/rest/oauth2-credential/callback`
4. Copy the **Client ID** and **Client Secret**

**In n8n:**
- **Settings → Credentials → Add Credential → Google Calendar OAuth2 API**
- Name: `Google Calendar OAuth2` (exact match required)
- Paste Client ID and Client Secret
- Click **Connect** — a Google authorization window opens; sign in and grant calendar access

---

### 2. Microsoft Outlook OAuth2 (Optional)

**Used in:** Stage 05 only — routed when attendee domain is `outlook.com`, `office365.com`, or `microsoft.com`. Skip this credential if you only use Google Calendar.

**How to obtain:**

1. Go to [Azure Portal](https://portal.azure.com) → **Azure Active Directory → App Registrations → New Registration**
   - Name: any descriptive name
   - Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
   - Redirect URI: `https://<your-n8n-domain>/rest/oauth2-credential/callback`
2. After registration, note the **Application (Client) ID**
3. Go to **Certificates & Secrets → New Client Secret** — copy the secret value
4. Go to **API Permissions → Add a permission → Microsoft Graph → Delegated**
   - Add: `Calendars.ReadWrite`, `offline_access`, `User.Read`
5. Click **Grant admin consent**

**In n8n:**
- **Settings → Credentials → Add Credential → Microsoft Outlook OAuth2 API**
- Name: `Microsoft Outlook OAuth2` (exact match required)
- Paste Application (Client) ID and Client Secret
- Click **Connect** and authorize with a Microsoft account

---

### 3. SMTP

**Used in:** Stage 06 (email notifications — confirmation, conflict alert, validation failure)

**How to obtain:**

Choose any SMTP provider. Common options:

| Provider | SMTP Host | Port | Notes |
|----------|-----------|------|-------|
| Gmail | `smtp.gmail.com` | 587 | Requires an [App Password](https://myaccount.google.com/apppasswords) — not your Gmail password |
| SendGrid | `smtp.sendgrid.net` | 587 | Use `apikey` as username; API key as password |
| Postmark | `smtp.postmarkapp.com` | 587 | Use API token as both username and password |
| Mailgun | `smtp.mailgun.org` | 587 | Use SMTP credentials from Mailgun domain settings |

**In n8n:**
- **Settings → Credentials → Add Credential → SMTP**
- Name: `SMTP Credentials` (exact match required)
- Enter: Host, Port, Username, Password
- TLS: enabled (recommended)

**Also set this environment variable:**
```bash
NOTIFICATION_EMAIL_FROM=noreply@yourdomain.com
```

---

### 4. PostgreSQL (Optional — Disabled by Default)

**Used in:** Stage 06 — the `Store in Database` node is present but **disabled**. Enable it only if you want persistent scheduling logs.

**How to obtain:**

Provide connection details for any PostgreSQL-compatible database:

| Option | How to Get Connection Details |
|--------|-------------------------------|
| Self-hosted PostgreSQL | Server hostname, port (5432), database name, username, password |
| Supabase | Project → Settings → Database → Connection string (use Transaction Pooler) |
| Railway / Render / Neon | Connection details from your dashboard |

**Create the log table first:**

```sql
CREATE TABLE scheduling_logs (
  request_id       TEXT,
  status           TEXT,
  notification_type TEXT,
  completed_at     TIMESTAMPTZ,
  processing_time_ms BIGINT
);
```

**In n8n:**
- **Settings → Credentials → Add Credential → Postgres**
- Name: `Postgres Credentials` (or update the node to match your credential name)
- Enter: Host, Port, Database, Username, Password
- SSL Mode: `require` (recommended for hosted databases)

**To enable:** Open `06_notify.json` in n8n, find the `Store in Database (Optional)` node, and toggle it on.

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

2. Register the server with Claude Code via CLI:
   ```bash
   claude mcp add n8n n8n-mcp-server \
     --env N8N_API_URL=https://<your-n8n-instance>/api/v1 \
     --env N8N_API_KEY=<your-n8n-api-key>
   ```

   Or add manually to `~/.claude/settings.json` under `mcpServers`:
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
