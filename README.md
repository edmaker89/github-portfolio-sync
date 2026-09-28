# GitHub Portfolio Sync

Reliable ingestion of public GitHub portfolio data with n8n and PostgreSQL.

## Status

Scope and architecture are approved. Implementation has not started yet.

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
