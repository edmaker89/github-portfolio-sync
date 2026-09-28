# Test plan — V1

Tests use sanitized, versioned fixtures served by a test-only n8n API simulator workflow unless the case explicitly says `live`. The simulator is protected with a dedicated Header Auth credential while active, is disabled after testing and is not part of the production flow. Live tests are evidence checks, not the only way to validate failure behavior.

## Coverage matrix

| ID | Scenario | Expected result | Layer |
|---|---|---|---|
| TC-00A | Database has no project schema | Sub-workflow creates V1 atomically and returns `schema_ready=true`, `version=1`, `action=created` | Schema |
| TC-00B | Database already has a valid V1 schema | Sub-workflow applies no DDL and returns `action=validated` | Schema |
| TC-00C | Migration version and required objects disagree | Synchronization stops with `schema_drift`; no API request starts | Schema |
| TC-01 | Valid profile and one repository page | Profile, repositories and successful run persisted | Integration |
| TC-02 | More than 100 repositories with `Link: rel="next"` | All pages fetched once in order | Integration |
| TC-03 | Same payload executed twice | One profile row and one row per repository ID; two successful run records | Integration |
| TC-04 | Existing repository metadata changes | Existing row updated; no duplicate | Integration |
| TC-05 | Repository disappears after a complete successful run | Repository set to `is_active=false` | Integration |
| TC-06 | Page two fails after page one persisted | Run fails and no repository is deactivated | Failure |
| TC-07 | Invalid or missing token returns `401` | Immediate sanitized failure; no retry | Failure |
| TC-08 | Permission failure returns `403` with remaining quota | Immediate sanitized failure | Failure |
| TC-09 | Primary rate limit returns `403/429` and reset header | Wait until reset, retry within limit, record headers | Failure |
| TC-10 | Secondary limit returns `429` with `retry-after` | Respect header before retry | Failure |
| TC-11 | Repeated `500` response | Backoff is bounded and run ultimately fails | Failure |
| TC-12 | Request timeout | Bounded retries; diagnostic category is `timeout` | Failure |
| TC-13 | Required repository field missing | Validation failure; no deactivation | Contract |
| TC-14 | PostgreSQL becomes unavailable during persistence | Bounded retry; failed run remains diagnosable | Failure |
| TC-15 | Two executions start for the same owner | One runs; the other is skipped/rejected | Concurrency |
| TC-16 | API exposes an eleventh page while `MAX_PAGES=10` | Run fails as `page_limit_exceeded`; no truncation or deactivation | Guardrail |
| TC-17 | Live sync for `edmaker89` | Counts reconcile with the fetched snapshot and no secrets appear in evidence | End to end |

## Evidence required per test

- test case ID and date;
- fixture or live endpoint used;
- n8n execution identifier;
- resulting `sync_runs` row;
- relevant SQL assertion result;
- sanitized screenshot or captured output for portfolio evidence;
- defect link when the expected result is not met.

## Exit gate

- TC-00A through TC-16 pass deterministically.
- TC-17 passes once against the live API.
- No unresolved critical or high-severity defect remains.
- Workflow exports and documentation match the tested version.
- Secret scanning of the repository returns no credential.
