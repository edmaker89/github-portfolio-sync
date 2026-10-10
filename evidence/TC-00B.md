# TC-00B — schema V1 existente e válido (sem DDL)

- Data UTC: 2026-10-10 (execução 444, disparo 17:18:18Z via botão Execute do editor).
- Fixture/endpoint: sub-workflow `Ensure Database Schema` (`dEgxD41QSk0cCoXr`) chamado pelo principal, `api_mode=simulator`, `simulator_scenario=pagination_101`.
- Execução n8n: `444` (`manual`, `success`), início `2026-10-10T17:18:17.963Z`, fim `2026-10-10T17:18:26Z`.

## Output do node Ensure Database Schema (execução 444)

```json
{
  "ok": true,
  "schema_status": "ready",
  "expected_version": 1,
  "current_version": 1,
  "initial_state": "current",
  "schema_created": "false",
  "schema_valid": "true"
}
```

## Asserção SQL — sem DDL

```sql
SELECT version, description FROM public.schema_migrations ORDER BY version;
-- antes e depois: [{"version":1,"description":"Initial schema"}] (1 linha, inalterada)
```

- `schema_created=false` + `initial_state=current` + `schema_valid=true`: caminho `validated`, nenhum `CREATE` executado.
- A run 21 prosseguiu para o fluxo normal (prova de que o gate liberou).

Resultado: **PASS**.
