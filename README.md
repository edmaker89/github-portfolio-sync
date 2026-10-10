# GitHub Portfolio Sync

Reliable ingestion of public GitHub portfolio data with n8n and PostgreSQL.

## Status

Scope and architecture are approved. V1 core (Stages 5–8) is **implemented and tested**:

- **Implemented and evidenced:** profile ingestion, repository ingestion with pagination, full reconciliation (deactivate only after a fully successful run), primary/secondary rate-limit handling, bounded retry/backoff for `5xx` and timeouts, repository validation failures, and Error Handler persistence to `sync_errors` on a production execution. Test evidence: [`evidence/`](evidence/) (TC-05 … TC-13, [`ERROR-HANDLER.md`](evidence/ERROR-HANDLER.md), plus [`ETAPA8-EXECUCAO.md`](evidence/ETAPA8-EXECUCAO.md)); checklist: [`evidence/CHECKLIST.md`](evidence/CHECKLIST.md).
- **Implemented, still pending dedicated evidence:** schema sub-workflow scenarios (TC-00A/B/C), happy-path/idempotency cases (TC-01 … TC-04), PostgreSQL outage (TC-14), concurrent runs (TC-15), `MAX_PAGES` guardrail (TC-16) and live end-to-end (TC-17).
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
