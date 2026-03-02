# Integrations

The integrations layer connects the orchestration system to external services across four categories: AI and reasoning, data storage, communication interfaces, and developer tooling. All credentials are managed externally by the workflow engine and referenced by logical name through the credential registry. No secrets, endpoints, or environment-specific values appear in workflow logic.

---

## Integration Categories

### AI and Reasoning

| Service | Role in System |
|---------|---------------|
| LLM Router | Intent classification for unstructured inputs. Returns target agent, confidence score, and extracted parameters. Used only when deterministic shortcode matching fails. |
| Speech-to-Text | Transcribes voice input to text before it enters the orchestration layer. Voice is treated as an I/O concern — the orchestrator receives plain text regardless of input channel. |
| Text-to-Speech | Synthesizes agent responses into audio for voice reply delivery. Applied post-response, after the orchestrator formats the output. |
| Reasoning / Repair | AI-assisted workflow repair invoked by the error handler when a failure matches no known fix pattern. Receives failure context and workflow structure; returns a proposed fix for validation before application. |

**Design principle:** LLM calls are gated by confidence thresholds and bypassed entirely for known shortcode patterns. AI services are invoked only where deterministic logic is insufficient — this controls cost, latency, and failure surface.

---

### Data Storage

| Service | Role in System | TTL Class |
|---------|---------------|-----------|
| Google Sheets — Operations | Operational data store for inventory, status, and quick-log entries. Read and written by the Operations Agent. | Short / No-cache |
| Google Sheets — Finance | Expense and receipt records. Written by the Finance Agent on submission; read for reporting queries. | Medium |
| Supabase (PostgreSQL) | Primary knowledge base. Stores embedded documents for retrieval-augmented queries. The Intelligence Agent queries this store using vector similarity search. | Long / Reference |
| Redis | Response cache. Stores agent outputs keyed by agent ID, user context hash, and query hash. TTL class is assigned per agent domain by caching policy. | Per TTL class |
| Google Drive | File storage for receipts and generated documents. Finance Agent writes receipt files; Document Agent reads and writes document files. | Reference |

**Cache key format:** `system:{agent_id}:{user_context_hash}:{query_hash}`

User-specific data is never shared across cache contexts. The user context hash is an opaque scope identifier — it is not exposed to agent logic.

**Registry resolution:** No workflow contains a raw data store ID. All references use logical names (e.g., `operations_sheet`, `knowledge_base`) resolved at runtime through the registry. Changing a data store requires one registry update — no workflow modifications.

---

### Communication Interfaces

| Interface | Role in System |
|-----------|---------------|
| Telegram | Primary user-facing interface. Receives text messages, voice attachments, and images. Returns text and voice responses. Serves as the live interaction surface for all end-user requests. |
| Notification Channels | Used by the scheduling sub-pipeline (stage 06) to dispatch event confirmations to participants. Channel resolution is registry-driven per participant record. |

**Design note:** The communication layer is treated as a pure I/O concern. All content decisions — what to say, how to format, what to retrieve — occur inside the orchestration and agent layers. The communication interface receives a formatted response and delivers it; it has no influence on routing or agent logic.

---

### Developer Tooling

| Tool | Role in System |
|------|---------------|
| Claude Code via MCP | Developer interface to the orchestration system. Allows workflow inspection, registry queries, and configuration changes through natural language during development and debugging sessions. Does not participate in production routing. |
| Git | Version control for all workflow files, contracts, registry, and governance documents. Pre-commit validation gates enforce contract compliance and version increments before changes reach the repository. |

**Pre-commit gate:** A validation script runs on every commit that modifies workflow JSON files. It checks:
- All modified workflows carry a version increment
- No workflow references an undefined registry key
- No contract violations are introduced

Commits that fail validation are blocked. This prevents contract drift between what workflows declare and what they actually require.

---

## Credential Management

Credentials are managed by the workflow engine's native credential store. The integration registry maps logical names to credential identifiers:

```
"credentials": {
  "logical_name": "engine-managed-credential-identifier"
}
```

Workflow nodes reference the logical name. The engine resolves the actual credential at runtime. Rotating a credential requires updating the engine's credential store — no workflow files change.

**What is never stored in the repository:**
- API keys, tokens, or secrets of any kind
- OAuth client IDs or refresh tokens
- Database connection strings
- Environment-specific endpoints or hostnames

---

## Integration Failure Handling

Each integration type has a defined failure posture:

| Category | Failure Posture |
|----------|----------------|
| LLM Router | Classification failure → confidence gate triggers clarification request, not speculation |
| STT | Transcription failure → orchestrator requests re-submission |
| TTS | Synthesis failure → text response delivered as fallback |
| Data stores | Read/write failure → error handler invoked; retried per max_retries policy |
| Cache (Redis) | Cache miss → agent executes normally; cache failure does not block agent execution |
| Communication (Telegram) | Delivery failure → logged; response not retried automatically |
| Developer tooling | Development-time only; failures do not affect production path |

The error handler receives structured failure context including the integration type, error classification, and whether the error matches a known fix pattern. See `architecture/error-handler.md` for the full recovery model.
