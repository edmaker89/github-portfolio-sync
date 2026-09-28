# Project state

**Updated:** 2026-09-28
**Phase:** design complete; ready for implementation
**Active feature:** GitHub Portfolio Sync V1

## Decisions

- AD-001: use the n8n HTTP Request node, not the native GitHub node, so integration mechanics remain visible.
- AD-002: synchronize the public profile and owned public repositories only.
- AD-003: use full paginated reconciliation; deactivate missing rows only after total success.
- AD-004 (superseded by AD-009): persist the portfolio in PostgreSQL while allowing n8n V1 internal state to remain in persistent SQLite.
- AD-005: use a read-only GitHub token stored as an n8n credential; OAuth2 is deferred.
- AD-006: execute API requests serially with bounded pages, timeouts and retries.
- AD-007 (superseded by AD-010): use WireMock and sanitized fixtures for deterministic failure testing.
- AD-008: keep execution instructions in the working conversation; this repository stores the approved product and technical contract.
- AD-009: treat the existing n8n and PostgreSQL environments as operator-supplied prerequisites; runtime provisioning is outside V1.
- AD-010: use a test-only n8n Webhook/Respond to Webhook API simulator and versioned fixtures instead of WireMock.
- AD-011: manage application schema V1 through a synchronous, version-aware n8n sub-workflow before synchronization begins.

## Current handoff

The revised scope, architecture, data boundaries, failure policy and test matrix are approved. Runtime provisioning was removed. No schema, synchronization or test workflow has been implemented yet.

## Next action

Build the `Ensure Database Schema` sub-workflow with V1 creation, validation, drift detection and its three schema test cases.

## Blockers

None.
