# GitHub Portfolio Sync

Reliable ingestion of public GitHub portfolio data with n8n and PostgreSQL.

## Status

Architecture and requirements are currently being defined. Workflow implementation has not started yet.

## Objective

Build a reproducible integration that reads public repository data from the GitHub API, normalizes it and persists a consistent representation in PostgreSQL.

The project will focus on the engineering concerns that appear after the first successful API call:

- authentication and credential management;
- pagination and processing in batches;
- rate limits and transient failures;
- data validation and normalization;
- idempotent persistence;
- incremental updates;
- execution traceability;
- safe reprocessing and troubleshooting.

## Planned stack

- n8n
- GitHub API
- PostgreSQL
- Docker Compose

## Project principles

- No credentials or personal secrets committed to Git.
- Happy-path execution alone is not considered complete.
- Failure scenarios must be reproducible and documented.
- Every demonstrated capability must point to a workflow, test and evidence.

## Documentation

- [Architecture](docs/architecture.md)
- [Security policy](SECURITY.md)

The repository will be expanded after the project specification is validated.

