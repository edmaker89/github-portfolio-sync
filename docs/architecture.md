# Architecture — V1

## System context

```mermaid
flowchart LR
    Trigger[Manual or daily trigger] --> Sync[n8n sync workflow]
    Sync --> Schema[n8n schema sub-workflow]
    GitHub[GitHub REST API] --> Sync
    Simulator[n8n test API simulator] -. test only .-> Sync
    Sync --> Normalize[Validate and normalize]
    Normalize --> Postgres[(Portfolio PostgreSQL)]
    Sync --> Error[Error workflow]
    Error --> Postgres
```

## Components

| Component | Responsibility |
|---|---|
| Main n8n workflow | Start a run, call the API, paginate, normalize, persist, reconcile and finish the run |
| Schema n8n sub-workflow | Validate schema version and required objects; create V1 when absent; report drift |
| Error n8n workflow | Sanitize and persist operational failure context |
| Test API simulator workflow | Return controlled GitHub-like bodies, status codes, delays and headers for deterministic tests |
| GitHub REST API | Supply public profile and repository metadata |
| PostgreSQL | Persist the portfolio projection, run history and sanitized errors |

The GitHub native node is intentionally not used. The HTTP Request node makes headers, query parameters, status codes, pagination and rate-limit behavior observable.

## Main flow

```mermaid
flowchart TD
    A[Manual or schedule trigger] --> B[Load and validate configuration]
    B --> C[Execute schema sub-workflow and wait]
    C --> D{Schema V1 ready?}
    D -- no --> E[Stop with schema diagnostic]
    D -- yes --> F{Another run active for owner?}
    F -- yes --> G[Finish as skipped]
    F -- no --> H[Create running sync_run]
    H --> I[GET public profile]
    I --> J[Upsert normalized profile]
    J --> K[GET repository pages serially]
    K --> L[Validate and normalize repositories]
    L --> M[Upsert by GitHub repository ID]
    M --> N{All pages persisted?}
    N -- no --> O[Mark run failed; keep current active flags]
    N -- yes --> P[Deactivate repositories not seen in this run]
    P --> Q[Mark run succeeded and store counters]
```

## Schema management

The main workflow calls `Ensure Database Schema` synchronously before creating a synchronization run. The sub-workflow owns project schema initialization, not PostgreSQL server provisioning.

The sub-workflow:

1. checks whether the project schema and migration metadata exist;
2. when absent, creates schema V1 and its objects in a transaction;
3. when version 1 is recorded, validates the required tables, columns, constraints and indexes;
4. returns without executing DDL when V1 is valid;
5. fails with `schema_drift` when metadata and actual objects disagree;
6. fails with `unsupported_schema_version` when the database is newer than the workflow understands.

Output contract:

```json
{
  "schema_ready": true,
  "version": 1,
  "action": "created | validated | migrated"
}
```

Existence of a single table is not enough to skip initialization. The version record and required-object validation prevent a partial schema from being treated as healthy.

## API contract

Base URL: `https://api.github.com`

| Purpose | Method and path | Query |
|---|---|---|
| Profile | `GET /users/{username}` | none |
| Repositories | `GET /users/{username}/repos` | `type=owner`, `sort=updated`, `direction=desc`, `per_page=100`, `page=N` |

Required request headers:

- `Accept: application/vnd.github+json`
- `Authorization: Bearer <credential managed by n8n>`
- `X-GitHub-Api-Version: 2026-03-10`

The workflow records safe diagnostic values from `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-used`, `x-ratelimit-reset`, `x-github-request-id`, `retry-after` and `link`. Authorization headers and response bodies that may contain unexpected data are never copied into operational logs.

## Pagination and workload limits

- Requests are serial.
- Each page contains at most 100 repositories.
- Pagination stops when the response has no `rel="next"` link.
- `MAX_PAGES` defaults to 10 to prevent runaway execution and is configurable.
- Exceeding the configured limit fails the run; it never silently truncates the portfolio.
- The request timeout defaults to 30 seconds.

## Reconciliation and idempotency

Every execution creates a `sync_runs` record. Profile and repository rows are upserted by stable numeric GitHub IDs. Each repository receives the current `run_id` as `last_seen_run_id`.

Only after every page has been fetched, validated and persisted may the workflow set `is_active = false` for repositories belonging to the owner that were not seen in the current run. A partial or failed run may update records it already saw, but it must not deactivate any record. Re-running the same payload produces the same current-state projection and a new audit run, without duplicate profile or repository rows.

Only one run per owner may have status `running`. A concurrent trigger is recorded or reported as `skipped` instead of starting a second reconciliation.

## Data model

All project objects live under the `github_portfolio_sync` PostgreSQL schema.

### `schema_migrations`

- `version INTEGER PRIMARY KEY`
- `description TEXT NOT NULL`
- `applied_at TIMESTAMPTZ NOT NULL`

### `github_profiles`

- `github_user_id BIGINT PRIMARY KEY`
- `login TEXT NOT NULL`
- `name`, `bio`, `company`, `location`, `blog`, `html_url`, `avatar_url`
- `public_repos`, `followers`, `following`
- `github_created_at`, `github_updated_at`, `synced_at` as `TIMESTAMPTZ`

### `github_repositories`

- `github_repo_id BIGINT PRIMARY KEY`
- `owner_login`, `name`, `full_name`, `description`, `html_url`
- `language`, `topics JSONB`, `visibility`, `default_branch`
- `fork`, `archived`, `disabled`
- `stargazers_count`, `watchers_count`, `forks_count`, `open_issues_count`, `size`
- `github_created_at`, `github_updated_at`, `github_pushed_at`
- `first_seen_at`, `last_seen_at`, `last_seen_run_id`, `is_active`

### `sync_runs`

- identity `id`, `owner_login`, `started_at`, `finished_at`
- `status`: `running`, `succeeded`, `failed` or `skipped`
- counters: pages, received, inserted, updated and deactivated
- last safe request/rate-limit metadata
- sanitized `error_code` and `error_message`

### `sync_errors`

- identity `id`, `run_id`, `occurred_at`, workflow stage and node
- error category, HTTP status, request ID, attempt and retryable flag
- sanitized message without credentials or raw sensitive headers

## Normalization contract

- Required profile fields: `id` and `login`.
- Required repository fields: `id`, `name`, `full_name`, `owner.login` and `visibility`.
- Timestamps are stored as `TIMESTAMPTZ`.
- Blank optional strings become `NULL`; arrays default to `[]`; counts must be non-negative integers.
- Forks and archived repositories remain in the dataset and are represented by flags.
- An invalid required field fails the run and prevents deactivation.

## Failure policy

| Failure | Behavior |
|---|---|
| Missing or invalid credential (`401`) | Fail without retry; persist sanitized context |
| Forbidden without exhaustion (`403`) | Fail without automatic retry |
| Primary rate limit exhausted | Wait until `x-ratelimit-reset`, then retry |
| `retry-after` present | Wait for the supplied number of seconds, then retry |
| Secondary limit without `retry-after` | Wait 60, 120 and 240 seconds; then fail |
| Timeout, network error or `5xx` | Retry after 5, 15 and 45 seconds; then fail |
| Invalid payload | Fail without retry and identify the validation stage |
| PostgreSQL unavailable | Retry the database operation with bounded attempts; then fail |

There are at most three retries after the initial attempt. Repeated failures never enter an infinite loop.

## Runtime boundary

The project starts at the workflow and application-schema layer. It assumes that the operator already has:

- a working n8n environment capable of importing workflows;
- a PostgreSQL database reachable from n8n;
- permission to create and use the `github_portfolio_sync` schema;
- outbound access to the GitHub REST API.

How n8n and PostgreSQL are installed, secured, updated, backed up or monitored is intentionally outside V1. This keeps the portfolio evidence portable across homelab, VPS, Coolify, Docker-based and managed/Enterprise environments.

## Deterministic HTTP test adapter

Instead of an external mock server, a test-only n8n workflow exposes GitHub-like Webhook routes. Switch/If nodes select a scenario from a query parameter, and Respond to Webhook controls JSON bodies, response codes and headers. A Wait node can reproduce a delayed response for timeout testing.

The main workflow uses configurable `GITHUB_API_BASE_URL`, so tests point it to the simulator while live evidence points it to `https://api.github.com`. While active, the simulator uses a dedicated Header Auth credential and only sanitized fixtures. It is never on the production execution path and is disabled after test evidence is collected.
