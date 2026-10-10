# GitHub Portfolio Sync

Reliable ingestion of public GitHub portfolio data with n8n and PostgreSQL.

## Status

Scope and architecture are approved. V1 core (Stages 5–8) is **implemented and tested**:

- **Implemented and evidenced:** profile ingestion, repository ingestion with pagination (`Link`), full reconciliation (deactivate only after a fully successful run), idempotent upserts and metadata updates, primary/secondary rate-limit handling, bounded retry/backoff for `5xx` and timeouts, repository validation failures, concurrent-run skip, the `MAX_PAGES` guardrail, schema validation without DDL, live end-to-end, and Error Handler persistence to `sync_errors` on a production execution. Test evidence: [`evidence/`](evidence/) (TC-00B, TC-01 … TC-13, TC-15 … TC-17, [`ERROR-HANDLER.md`](evidence/ERROR-HANDLER.md), [`ETAPA8-EXECUCAO.md`](evidence/ETAPA8-EXECUCAO.md)); checklist: [`evidence/CHECKLIST.md`](evidence/CHECKLIST.md).
- **Pending dedicated evidence (need infrastructure not available in this run):** schema bootstrap/drift cases that require a disposable database (TC-00A, TC-00C) and PostgreSQL outage handling (TC-14).
- **Planned, not implemented (NFR-07):** nothing outside the approved V1 scope; see [`docs/scope.md`](docs/scope.md) for what is explicitly deferred.

Details: [`docs/`](docs/) for architecture, scope and test plan; [`evidence/`](evidence/) for executed-test traces; [`workflows/sanitized/`](workflows/sanitized/) for reviewable workflow exports.

## Objective

Build a reproducible integration that reads a public GitHub profile and its owned public repositories, normalizes the data and maintains a consistent representation in PostgreSQL.

The project will focus on the engineering concerns that appear after the first successful API call:

- token-based authentication and credential management;
- real pagination through the GitHub REST API;
- rate limits and transient failures;
- data validation and normalization;
- idempotent persistence;
- full reconciliation without unsafe deactivation after partial failures;
- execution traceability;
- safe reprocessing and troubleshooting.

## V1 at a glance

| Area | Decision |
|---|---|
| Source | GitHub REST API |
| Resources | Public user profile and owned public repositories |
| Orchestration | n8n HTTP Request workflow |
| Persistence | PostgreSQL |
| Sync model | Full paginated reconciliation |
| Triggers | Manual and daily at 03:00 `America/Sao_Paulo` |
| Schema management | Idempotent n8n sub-workflow with version validation |
| Test strategy | Versioned fixtures and an n8n API simulator workflow |
| Default example | `edmaker89` |

## Planned stack

- n8n
- GitHub API
- PostgreSQL

The project is deployment-agnostic. It assumes an existing n8n environment and a PostgreSQL database reachable by n8n, whether they run in a homelab, VPS, Coolify, Docker-based platform or managed/Enterprise installation.

## Project principles

- No credentials or personal secrets committed to Git.
- Happy-path execution alone is not considered complete.
- Failure scenarios must be reproducible and documented.
- Every demonstrated capability must point to a workflow, test and evidence.

## Documentation

- [Architecture](docs/architecture.md)
- [Approved scope](docs/scope.md)
- [Test plan](docs/test-plan.md)
- [Security policy](SECURITY.md)

The next milestone is the database schema bootstrap and validation sub-workflow.
