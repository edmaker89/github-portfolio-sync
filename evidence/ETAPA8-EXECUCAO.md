# Suíte Etapa 8 e reconciliação — execução de 2026-10-10

## Mecanismo

O workflow principal `Portifolio Sync` (`u8oHC2DBgZUGMZUH`) permaneceu **inativo**. Cada caso foi configurado por GET/PUT da API n8n alterando somente os valores `api_mode` e `simulator_scenario` do node `Runtime Configuration` e preservando `name`, `nodes`, `connections`, `settings`, `pinData={}`. A execução foi iniciada no editor n8n pelo botão **Execute workflow**, com `Manual Trigger` selecionado, exceto TC-08, disparado manualmente com `Schedule Trigger` selecionado (modo n8n `manual`). O ID e o traço de nodes vêm de `GET /api/v1/executions/{id}?includeData=true`.

O banco foi consultado pelo workflow ativo `P01 | DB Read (TEMP)` (`98V5bUs5zBc6gsn9`), via Webhook POST com Header Auth. O token fica apenas em `/tmp/p01-db-read-token`; o valor não integra nenhuma evidência. O harness aceita somente uma consulta `SELECT`/`WITH` de leitura por vez. Ele permaneceu ativo para testes posteriores.

O Error Handler (`i7QXkiz6EXgXtYnH`) está ativo, mas as execuções **manuais** do workflow principal não dispararam novas execuções do Error Handler nem gravaram linhas em `public.sync_errors`. Todas as falhas produziram `public.sync_runs.status='failed'` e o envelope seguro no node `90 | Stop Main Workflow`; as evidências individuais mostram `sync_errors=[]`. A persistência via Error Handler requer uma execução de produção separada para ser coberta.

## Ajustes do simulador feitos para tornar os fixtures executáveis

- `Respond to Webhook`: resposta JSON passou a ser o corpo GitHub direto, sem envelope adicional `{body: ...}`. A primeira tentativa de TC-09 (`289`) evidenciou esse defeito; a repetição (`299`) passou.
- `Respond to Webhook`: `Retry-After` passou a ser enviado somente quando existe, usando nome condicional de cabeçalho. A primeira execução de TC-10 (`313`) esperou 60 s no primeiro 429 pela ausência do cabeçalho; a repetição (`327`) usou 2 s em todos os três retries.
- `invalid_payload`: o perfil agora é válido; a falha intencional fica no repositório (`owner.login` ausente), conforme TC-13.
- `server_error`: HTTP 500 persistente para exercitar o limite de 3 retries do TC-11.
- `page2_error`: novo scenario; perfil e página 1 válidos, página 2 retorna HTTP 500 em todas as tentativas, conforme TC-06.

Backups do simulador antes de cada ajuste: `workflows/github-api-simulator.pre-tests.json`, `workflows/github-api-simulator.pre-page2-error.json`, `workflows/github-api-simulator.pre-retry-header.json` e `workflows/github-api-simulator.pre-server-error-test.json`.

## Consulta de invariância usada nos casos de falha

```sql
SELECT count(*) AS total,
       count(*) FILTER (WHERE is_active) AS active,
       md5(coalesce(string_agg(github_repo_id::text, ',' ORDER BY github_repo_id)
           FILTER (WHERE is_active), '')) AS active_id_hash
FROM public.github_repositories;
```

A comparação dos três campos antes/depois detecta inserções ou desativações no conjunto ativo. Nos casos com sucesso completo, a desativação de ausentes é esperada **após** `07 | Reconcile Repositories`; TC-05 verifica o ciclo de reativação live.

## Resultado consolidado

| Caso | Execução válida | Run | Resultado |
|---|---:|---:|---|
| [TC-05](TC-05.md) | 397 / 403 / 412 | 18 / 19 / 20 | Passou: 67 reais ativos → 3 do fixture ativos → 67 reais ativos |
| [TC-06](TC-06.md) | 365 | 16 | Passou: página 1 persistida, falha na página 2, nenhuma desativação |
| [TC-07](TC-07.md) | 259 | 8 | Passou: 401, falha imediata sem retry |
| [TC-08](TC-08.md) | 280 | 9 | Passou: 403 com cota, falha imediata sem retry |
| [TC-09](TC-09.md) | 299 | 11 | Passou após correção do fixture: 3 esperas por reset e sucesso completo |
| [TC-10](TC-10.md) | 327 | 13 | Passou após correção do fixture: 3 esperas de 2 s por `Retry-After` |
| [TC-11](TC-11.md) | 341 | 14 | Passou: 4 respostas 500, 3 esperas 5/15/45 s, falha final |
| [TC-12](TC-12.md) | 383 | 17 | Passou: 4 timeouts, 3 esperas 5/15/45 s, categoria `timeout` |
| [TC-13](TC-13.md) | 355 | 15 | Passou: validação de repositório, sem retry e sem desativação |

Após a suíte, GET do workflow principal confirmou `api_mode=live`, `simulator_scenario=happy`, `active=false`, `pinData={}`, `settings.errorWorkflow=i7QXkiz6EXgXtYnH`, `settings.executionOrder=v1` e todos os destinos de conexões existentes. Consulta SQL final: 70 repositórios cadastrados, 67 ativos (todos reais), 3 do fixture inativos, 0 runs `running` e 0 linhas em `sync_errors` para as runs 8–20. O workflow de leitura TEMP continua ativo.

As execuções de sucesso dos cenários de rate limit seguem a regra de reconciliação: a desativação de IDs ausentes é permitida somente após todas as páginas concluírem. Por isso TC-09 desativou 67 IDs reais ao concluir no simulador; o TC-05 demonstrou a reativação live final. Em todos os cenários que terminaram `failed`, `records_deactivated=0` e o conjunto de IDs ativos permaneceu igual ao anterior.
