# Project state

**Updated:** 2026-09-28
**Phase:** design complete; ready for implementation
**Active feature:** GitHub Portfolio Sync V1

## Decisions

- AD-001: use the n8n HTTP Request node, not the native GitHub node, so integration mechanics remain visible.
- AD-002: synchronize the public profile and owned public repositories only.
- AD-003: use full paginated reconciliation; deactivate missing rows only after total success.
- AD-004: persist the portfolio in PostgreSQL while allowing n8n V1 internal state to remain in persistent SQLite.
- AD-005: use a read-only GitHub token stored as an n8n credential; OAuth2 is deferred.
- AD-006: execute API requests serially with bounded pages, timeouts and retries.
- AD-007: use WireMock and sanitized fixtures for deterministic failure testing.
- AD-008: keep execution instructions in the working conversation; this repository stores the approved product and technical contract.

## Current handoff

The scope, architecture, data boundaries, failure policy and test matrix are approved. No workflow, schema or runtime stack has been implemented yet.

## Next action

Create the reproducible Docker Compose environment and pin the n8n, PostgreSQL and WireMock image versions before adding the database schema.

## Blockers

None.
