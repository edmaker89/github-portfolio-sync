# Architecture

## Initial context

```mermaid
flowchart LR
    Trigger[Manual or scheduled trigger] --> N8N[n8n integration workflow]
    GitHub[GitHub API] --> N8N
    N8N --> Normalize[Validation and normalization]
    Normalize --> Postgres[(PostgreSQL)]
    N8N --> Evidence[Execution logs and evidence]
```

## Status

This is the initial architectural boundary, not the final design. Authentication, incremental state, failure handling and test strategy will be documented before workflow implementation begins.

