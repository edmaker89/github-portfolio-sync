# Implementation context

## Current repository

The repository currently contains specification and policy documents only. No Docker stack, SQL schema, workflow export, fixture or automated verification command exists yet.

## Relevant files

- `README.md` — public project summary and current status.
- `docs/scope.md` — approved functional and non-functional contract.
- `docs/architecture.md` — API, flow, persistence, normalization and failure design.
- `docs/test-plan.md` — deterministic and live test coverage.
- `SECURITY.md` — public security and secret-handling rules.
- `.specs/STATE.md` — implementation handoff and architectural decisions.

## External contracts

- GitHub REST API version `2026-03-10`.
- `GET /users/{username}`.
- `GET /users/{username}/repos` with `type=owner`, `sort=updated`, `direction=desc`, `per_page=100` and `page=N`.
- n8n HTTP Request node with response headers and status enabled.
- PostgreSQL for domain and audit persistence.
- WireMock for deterministic API responses during tests.

## Constraints for implementation

- Do not replace the HTTP Request workflow with the native GitHub node.
- Do not add a private-data path to V1.
- Do not reconcile inactive rows before every expected page is persisted.
- Do not rely only on live GitHub responses to test failures.
- Do not claim a test, feature or skill is demonstrated before its artifact and evidence exist.
