# Feature specification: GitHub Portfolio Sync V1

**Status:** approved
**Last updated:** 2026-09-28

## Overview

Synchronize one public GitHub user profile and all public repositories owned by that user into PostgreSQL through an observable, idempotent and failure-aware n8n workflow.

The reader-facing source of truth is [`docs/scope.md`](../../../docs/scope.md). Requirement IDs `FR-01` through `FR-15`, `NFR-01` through `NFR-07` and all ten acceptance criteria in that document are approved.

## Critical invariants

1. Domain rows are unique by stable GitHub numeric ID.
2. Replaying unchanged source data never duplicates profile or repository rows.
3. Missing repositories are made inactive only after a complete successful snapshot.
4. A failed or truncated execution never performs reconciliation deactivation.
5. Only one run per owner is active at a time.
6. Secrets never enter versioned exports, fixtures, logs or evidence.
7. Bounded pages, timeouts and retries prevent infinite or silently truncated execution.

## Scope boundary

The feature uses only the public user and public owned-repository REST endpoints. It intentionally excludes private data, repository contents, activity resources, GraphQL, webhooks, bidirectional synchronization, AI and platform-scale n8n operation.

## Verification

The acceptance criteria are covered by `TC-01` through `TC-17` in [`docs/test-plan.md`](../../../docs/test-plan.md). An item is not complete without the expected database assertion and sanitized execution evidence.

## Open questions

None. Runtime image versions will be selected and pinned as the first implementation action because they are implementation dependencies, not unresolved product scope.
