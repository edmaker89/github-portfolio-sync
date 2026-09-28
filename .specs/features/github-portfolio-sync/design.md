# Technical design index

**Status:** approved for implementation

The complete public design is maintained in [`docs/architecture.md`](../../../docs/architecture.md). It defines:

- system components and the main workflow;
- REST endpoints, headers and query parameters;
- pagination and workload guardrails;
- idempotent reconciliation behavior;
- version metadata plus four domain/audit tables;
- normalization contract;
- failure classification and bounded retry behavior;
- runtime boundary and schema-management sub-workflow.

## Requirement-to-design map

| Requirement group | Design section |
|---|---|
| FR-01–FR-04 | Main flow, schema gate, API contract, pagination |
| FR-05–FR-07 | Normalization contract, data model, idempotency |
| FR-08–FR-10 | Reconciliation and `sync_runs` model |
| FR-11–FR-12 | Failure policy |
| FR-13 | One active run per owner invariant |
| FR-14 | Error workflow and `sync_errors` model |
| FR-15 | n8n API simulator and test plan |
| NFR-01–NFR-07 | Idempotency, security, guardrails, runtime boundary and documentation status |

## Test relationship

The design is verified by the matrix in [`docs/test-plan.md`](../../../docs/test-plan.md). Tests must be added alongside the behavior they validate during implementation; end-of-project test retrofitting is not accepted.
