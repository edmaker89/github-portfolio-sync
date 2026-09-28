# Approved scope — V1

**Status:** approved and ready for implementation
**Approved on:** 2026-09-28

## Outcome

A person can clone the repository, supply a GitHub username and a read-only token, start the local stack, run the n8n workflow and inspect a current, traceable PostgreSQL projection of that user's public profile and owned public repositories.

## Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Support both manual execution and a daily schedule at 03:00 `America/Sao_Paulo`. |
| FR-02 | Validate configuration before creating an active synchronization run. |
| FR-03 | Read `GET /users/{username}` using the n8n HTTP Request node. |
| FR-04 | Read every page of `GET /users/{username}/repos` with `type=owner` and `per_page=100`. |
| FR-05 | Include owned public forks and archived repositories, preserving their flags. |
| FR-06 | Validate and normalize the selected profile and repository fields. |
| FR-07 | Upsert profile and repository rows using GitHub numeric IDs. |
| FR-08 | Create an auditable run record with status, timestamps, counters and safe diagnostics. |
| FR-09 | After a completely successful fetch and persistence cycle, mark previously known repositories not seen in the run as inactive. |
| FR-10 | Never deactivate repositories after a partial or failed run. |
| FR-11 | Handle GitHub primary and secondary rate limits using response headers and bounded waits. |
| FR-12 | Retry transient network, `5xx` and database failures with bounded backoff. |
| FR-13 | Reject overlapping runs for the same owner. |
| FR-14 | Route unhandled failures to an error workflow that persists sanitized context. |
| FR-15 | Export sanitized workflows and provide deterministic success and failure fixtures. |

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | A repeated successful synchronization with unchanged source data creates no duplicate profile or repository rows. |
| NFR-02 | No credential, authorization header or private repository data may be committed or exposed in evidence. |
| NFR-03 | Requests are serial and bounded by timeout, page and retry limits. |
| NFR-04 | The local environment is reproducible with Docker Compose and pinned image versions. |
| NFR-05 | The workflow is diagnosable from the run record, sanitized errors, GitHub request ID and n8n execution. |
| NFR-06 | All destructive-looking reconciliation occurs only after the full source snapshot is known to be valid. |
| NFR-07 | Public documentation must distinguish implemented behavior from planned behavior. |

## Configuration contract

| Setting | Default | Rule |
|---|---:|---|
| `GITHUB_USERNAME` | `edmaker89` in examples | 1–39 characters; letters, digits and single hyphens; no leading or trailing hyphen |
| `GITHUB_API_BASE_URL` | `https://api.github.com` | Overridable only to support the local mock API |
| `GITHUB_API_VERSION` | `2026-03-10` | Sent in the version header |
| `SYNC_TIMEZONE` | `America/Sao_Paulo` | Used by the schedule trigger |
| `MAX_PAGES` | `10` | Fail if another page exists after this limit |
| `REQUEST_TIMEOUT_MS` | `30000` | Abort requests that do not begin a response in time |
| GitHub token | none | Read-only credential stored in n8n, never in workflow JSON or `.env.example` |

## Included data

- public user identity and profile metadata;
- owned public repository identity and descriptive metadata;
- language, topics, visibility and lifecycle flags;
- public counters exposed by the selected endpoints;
- source creation/update/push timestamps;
- synchronization state, counters and sanitized diagnostic metadata.

## Explicitly out of scope

- private repositories or corporate data;
- issues, pull requests, commits, releases, repository contents and traffic analytics;
- organizations and repositories merely contributed to by the user;
- GraphQL, webhooks, bidirectional synchronization or a custom user interface;
- AI, agents, LLMs or RAG;
- Kubernetes, queue mode, multi-worker n8n, GitOps or a production n8n database;
- publishing a generic CRUD solely to demonstrate every HTTP verb;
- OAuth2: a read-only token is the proportionate authentication model for V1.

## Acceptance criteria

The V1 scope is complete only when:

1. a clean clone can start the documented local environment;
2. the manual and scheduled paths reach the same synchronization logic;
3. live GitHub data for a public user is persisted with every repository page;
4. a second unchanged run creates no duplicate domain rows;
5. a renamed or updated repository changes the existing row identified by GitHub ID;
6. a repository absent from a fully successful later run becomes inactive;
7. a repository absent only because page two failed remains active;
8. `401`, `403`, `429`, `5xx`, timeout, invalid payload and database outage paths are evidenced;
9. credentials are absent from Git history, workflow exports, fixtures, screenshots and logs;
10. architecture, troubleshooting, test evidence and sanitized workflows are present in the repository.

## Capability boundary

V1 demonstrates a real `GET` integration, Bearer authentication, headers, query parameters, pagination, response metadata, rate-limit handling and REST use without a native node. It does **not** by itself prove mastery of every HTTP verb or every authentication mechanism. Those composite skills remain partial until later projects provide coherent evidence.
