# Centralized MCP Tool Discovery

**Status:** Design | **Version:** 1.0 | **Date:** 2026-03-10
**Related:** SOVEREIGN (JVI-CEO-028), multi-agent evidence validation

---

## Overview

Agents query a centralized MCP registry to discover available tools and services. Each tool exposes a standardized MCP interface that wraps external APIs or internal enterprise services. The orchestrator selects the appropriate tool, and requests are routed through secure gateways before reaching the underlying system.

## Architecture

```
                    ┌─────────────────────────────┐
                    │     SOVEREIGN / Orchestrator  │
                    │     (Tool Selection Layer)    │
                    └──────────┬──────────────────┘
                               │ queries
                               ▼
                    ┌─────────────────────────────┐
                    │    MCP Tool Registry          │
                    │    (JSON / Supabase table)    │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │ server: filesystem       │  │
                    │  │ capabilities: read,write │  │
                    │  │ auth: none (stdio)       │  │
                    │  │ scope: local files       │  │
                    │  ├─────────────────────────┤  │
                    │  │ server: github           │  │
                    │  │ capabilities: issues,prs │  │
                    │  │ auth: PAT (Bearer)       │  │
                    │  │ scope: jasonv2610/*      │  │
                    │  ├─────────────────────────┤  │
                    │  │ server: n8n              │  │
                    │  │ capabilities: workflows  │  │
                    │  │ auth: MCP Access Token   │  │
                    │  │ scope: cloud instance    │  │
                    │  ├─────────────────────────┤  │
                    │  │ server: supabase         │  │
                    │  │ capabilities: sql,rls    │  │
                    │  │ auth: Access Token       │  │
                    │  │ scope: project DB        │  │
                    │  ├─────────────────────────┤  │
                    │  │ server: context7         │  │
                    │  │ capabilities: docs       │  │
                    │  │ auth: API query          │  │
                    │  │ scope: library docs      │  │
                    │  ├─────────────────────────┤  │
                    │  │ server: notebooklm      │  │
                    │  │ capabilities: notebooks  │  │
                    │  │ auth: Google cookies     │  │
                    │  │ scope: user notebooks    │  │
                    │  ├─────────────────────────┤  │
                    │  │ server: GitKraken        │  │
                    │  │ capabilities: git devex  │  │
                    │  │ auth: GitHub PAT         │  │
                    │  │ scope: local repos       │  │
                    │  └─────────────────────────┘  │
                    └──────────┬──────────────────┘
                               │ dispatches
                               ▼
              ┌────────────────────────────────────────┐
              │         Secure Gateway Layer            │
              │                                        │
              │  ┌──────────┐ ┌──────────┐ ┌────────┐ │
              │  │ Auth      │ │ Rate     │ │ Audit  │ │
              │  │ Validator │ │ Limiter  │ │ Logger │ │
              │  └──────────┘ └──────────┘ └────────┘ │
              └────────────────┬───────────────────────┘
                               │
              ┌────────────────▼───────────────────────┐
              │         MCP Server Interfaces           │
              │                                        │
              │  filesystem │ github │ n8n │ supabase  │
              │  context7   │ notebooklm │ GitKraken   │
              └────────────────────────────────────────┘
                               │
              ┌────────────────▼───────────────────────┐
              │         External Systems                │
              │                                        │
              │  Local FS │ GitHub API │ n8n Cloud     │
              │  Supabase │ Google │ npm/docs          │
              └────────────────────────────────────────┘
```

## Registry Schema

```json
{
  "version": "1.0",
  "servers": [
    {
      "name": "github",
      "type": "stdio",
      "package": "@modelcontextprotocol/server-github",
      "capabilities": ["issues", "pull_requests", "repos", "code_search"],
      "auth_type": "bearer",
      "auth_source": "JVI-Secrets",
      "scope": "jasonv2610/*",
      "rate_limit": "5000/hour",
      "health_check": "gh auth status",
      "required_for": ["SOVEREIGN", "Debug Master", "Development Agent"]
    },
    {
      "name": "n8n",
      "type": "stdio",
      "package": "@anthropic/mcp-n8n",
      "capabilities": ["workflow_read", "workflow_update", "execution_list"],
      "auth_type": "mcp_access_token",
      "auth_source": ".mcp.json",
      "scope": "cloud_instance",
      "rate_limit": "100/minute",
      "health_check": "n8n_health_check",
      "required_for": ["Debug Master", "Development Agent"],
      "regulations": ["REG-001", "REG-002"]
    },
    {
      "name": "supabase",
      "type": "stdio",
      "package": "@anthropic/mcp-supabase",
      "capabilities": ["sql_execute", "migrations", "edge_functions"],
      "auth_type": "access_token",
      "auth_source": "JVI-Secrets",
      "scope": "project_db",
      "rate_limit": "1000/minute",
      "health_check": "execute_sql SELECT 1",
      "required_for": ["Data Scientist", "Finance Bridge"]
    },
    {
      "name": "filesystem",
      "type": "stdio",
      "package": "@modelcontextprotocol/server-filesystem",
      "capabilities": ["read", "write", "search", "list"],
      "auth_type": "none",
      "auth_source": null,
      "scope": "C:\\Users\\18323\\Projects",
      "rate_limit": null,
      "health_check": "list_directory",
      "required_for": ["all"]
    },
    {
      "name": "context7",
      "type": "stdio",
      "package": "@anthropic/mcp-context7",
      "capabilities": ["library_docs", "code_examples"],
      "auth_type": "api_query",
      "auth_source": null,
      "scope": "public_libraries",
      "rate_limit": null,
      "health_check": "resolve-library-id",
      "required_for": ["Development Agent"]
    },
    {
      "name": "notebooklm",
      "type": "stdio",
      "package": "notebooklm-mcp-cli",
      "capabilities": ["notebooks", "sources", "studio", "research"],
      "auth_type": "google_cookies",
      "auth_source": "nlm login",
      "scope": "user_notebooks",
      "rate_limit": null,
      "health_check": "server_info",
      "required_for": ["Intelligence Agent"]
    },
    {
      "name": "GitKraken",
      "type": "stdio",
      "package": "gitkraken-mcp",
      "capabilities": ["git_status", "git_log", "git_blame", "git_branch"],
      "auth_type": "github_pat",
      "auth_source": "JVI-Secrets",
      "scope": "local_repos",
      "rate_limit": null,
      "health_check": "git_status",
      "required_for": ["SOVEREIGN", "Debug Master"]
    }
  ]
}
```

## Discovery Flow

```
1. Agent receives task
2. Agent queries MCP Tool Registry:
   "What tools do I need for [task_type]?"
3. Registry returns matching servers with capabilities
4. Orchestrator validates:
   a. Auth is available (check auth_source)
   b. Rate limit not exceeded
   c. No regulation conflicts (REG-001, REG-002)
5. Request routed through Secure Gateway:
   a. Auth Validator: confirms token/credentials valid
   b. Rate Limiter: enforces per-server limits
   c. Audit Logger: logs tool invocation for lineage
6. MCP server handles request
7. Response returned through gateway (sanitized)
```

## SOVEREIGN Integration

SOVEREIGN uses the registry to:

1. **Morning Brief**: Query `github` for issues/PRs, `GitKraken` for repo status, `n8n` for workflow health
2. **Portfolio Health**: Batch queries across all `required_for: SOVEREIGN` servers
3. **Tool Availability Check**: Before dispatching subagents, verify their required MCP servers are healthy

```
SOVEREIGN.dispatch_subagent(task):
  1. Determine required_tools from registry
  2. Health-check each required server
  3. If server unhealthy → log to data_gaps, skip that data source
  4. Dispatch subagent with confirmed tool set
  5. Collect results through consensus engine
```

## Security Constraints

- Registry file itself is NOT committed (contains server names but no credentials)
- Auth tokens remain in `.mcp.json` (gitignored) and JVI-Secrets
- Gateway layer enforces the same rules as root CLAUDE.md Section 5 (MCP Server Policy)
- All tool invocations are logged for audit (CHRONICLER integration in Phase 4)

## Implementation Phases

| Phase | What | When |
|-------|------|------|
| Phase 1 (current) | Design doc + SOVEREIGN references registry conceptually | Now |
| Phase 2 | JSON registry file at `jv-dev-config/registry/mcp_tool_registry.json` | Next sprint |
| Phase 3 | Health-check script that validates all servers on session start | Phase 3 |
| Phase 4 | Supabase table for dynamic registry + audit logging | Phase 4 |
| Phase 5 | Rate limiter middleware + cross-machine registry sync | Phase 5 |

## References

- Root policy: `Projects/CLAUDE.md` Section 5 (MCP Server Policy)
- SOVEREIGN agent: `jvi-core/.claude/agents/01_orchestration/JVceo-executive.md`
- Evidence validation: SOVEREIGN's `<evidence_validation>` block
- MCP config: `~/.claude.json` (machine-level), `.mcp.json` (project-level)
