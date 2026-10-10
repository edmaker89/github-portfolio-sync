# Evidence — Error Handler end-to-end (2026-10-10)

- Disparo: `GET /webhook/github-sync/error-handler-test` → `{"message":"Workflow was started"}` HTTP 200 às 2026-10-10T16:57:55Z.
- Contexto de teste: `Set Test Context.run_id` temporariamente = `20` (`SELECT max(id) FROM public.sync_runs`), revertido para `SEU-RUN-ID-REAL` às 16:58:25Z (verificado via GET).
- Envelope emitido pelo `Stop and Error`: `P01_SAFE_ERROR` com `stage=error_handler_gate`, `category=authentication`, `http_status=401`, `retryable=false` e mensagem com Bearer de token falso (prefixo `ghp_FAKE…`, valor completo nunca persistido em claro).

## Execução do Error Handler (i7QXkiz6EXgXtYnH)

- execution id: `423`, `mode=error`, `status=success`
- `startedAt`: 2026-10-10T16:57:55.080Z · `stoppedAt`: 2026-10-10T16:57:58.768Z
- cadeia: Error Trigger → Normalize Error → Sanitize Error → Has Run ID? → Insert sync_errors

## Linha persistida em public.sync_errors

| id | run_id | stage | node_name | category | http_status | retryable | safe_message |
|---|---|---|---|---|---|---|---|
| 1 | 20 | error_handler_gate | Stop and Error | authentication | 401 | false | `Authorization=[REDACTED] [REDACTED] controlled failure` |

- `occurred_at`: 2026-10-10T16:57:58.745Z (coerente com `stoppedAt` da execução 423).

## Verificação de sanitização — PASS

- `SELECT count(*) AS leaks ... WHERE safe_message LIKE '%ghp_FAKE%' OR LIKE '%FAKE%'` → `0`.
- O token falso NÃO aparece em claro; sai redigido como `[REDACTED]`.
- Asserções: nova linha ✓ · `category=authentication` ✓ · `http_status=401` ✓ · sem vazamento ✓.

Resultado: **PASS**. Nenhum segredo real utilizado; somente leitura no banco (harness SELECT-only) + 2 PUTs revertidos no workflow de teste. Sem commit.
