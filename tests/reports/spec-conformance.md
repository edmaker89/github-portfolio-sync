# Spec conformance — Etapas 6/7/8 — Portifolio Sync (u8oHC2DBgZUGMZUH)

- Fonte: `GET /api/v1/workflows/u8oHC2DBgZUGMZUH` exportado para `/tmp/fin.json` em 2026-10-10 (somente leitura, sem edição n8n, sem commit, sem expor chave).
- Workflow: `Portifolio Sync`, `active=false`, `settings.executionOrder=v1`, `settings.errorWorkflow=i7QXkiz6EXgXtYnH`.
- Contagem: 62 nós, 58 origens em `connections`, 75 arestas. 75/75 destinos existem. Alcançáveis a partir dos triggers: 61/62 (órfão: `Create Skipped Sync`).
- Spec: `maestri note read "regras"` (06.00–06.15, 07.00–07.02, 08.00–08.12, 90.00–90.02 + ajuste Error Handler + diagrama canvas). Estado: `state-md` C1 Etapa 7 (49 nós) e C1 Etapa 8 (62 nós/75 destinos).
- Legenda: `OK` = implementado conforme spec (lógica/conexão confere); `DIVERGÊNCIA` = nome/conteúdo/conexão difere (com o que falta).

## Etapa 6 — repositórios/paginação

- `Init Repository Pagination` [Code] — OK (cadeia `Update Run Profile Metadata → Init`; `owner_login=x.profile.login`, `page=1/attempt=0`). DIVERGÊNCIA textual: spec lê `$input.first().json`, workflow lê `$input.first().json.context` (adaptado ao upstream que retorna `input.j AS context`).
- `Prepare Repository Request` [Code, 25 linhas] — OK (valida `page>=1`, `stage/request_kind=repositories`). Conexões de entrada OK: `Init`, `06 | Next Page`, `08 | Retry Target`.
- `Repository API Mode` [IF] — OK funcional (2 saídas: Live/Simulator). DIVERGÊNCIA de tipo: spec diz “Switch”, workflow usa IF (mesmo padrão do `API Mode?` do perfil).
- `Live | Get Repositories` [HTTP] — OK (URL `/users/.../repos`, query type/sort/direction/per_page=100/page, headers Accept/Api-Version, `timeout={{$json.timeout_ms}}`, fullResponse+neverError+pagination OFF). Saídas OK: normal → `Classify Repository Response`, erro → `Classify Repository Transport Error`.
- `Simulator | Get Repositories` [HTTP] — OK (igual Live + `scenario/attempt`). Saídas OK idem.
- `Classify Repository Response` [Code, 264 linhas] — OK (classificação success/401/rate_limit/403/5xx, `retryable`, `link_header`, rate-limit parse). DIVERGÊNCIA textual: spec usa `$('06 | Prepare Repository Request')`, workflow usa `$('Prepare Repository Request')` (nó real sem prefixo; internamente consistente).
- `06 | Is Repository Success?` [IF, `classification==='success'`] — OK. Rewiring OK: true → `Normalize`, false → `08 | Is Retryable?` (fase pós-Etapa 8 da spec; placeholders `Build Profile/Repository HTTP Failure` removidos — confirmado ausentes).
- `06 | Normalize Repository Page` [Code, 492 linhas] — OK (helpers, body array, required `id/name/full_name/owner.login/visibility`, `has_next = length>0 && rel="next"`, `records_received`).
- `06 | Is Repository Page Valid?` [IF, `valid===true`] — OK (true → Upsert, false → Extract).
- `06 | Extract Repository Failure` [Code, 6 linhas] — OK (passthrough `$input.first().json.failure`, idêntico à spec 06.08) → `90 | Record Run Failure`.
- `06 | Upsert Repository Page` [Postgres, 4326] — OK (upsert por `github_repo_id`, preserva `first_seen_at`, `last_seen_run_id`, retorna `context` com inserted/updated) → `Restore Repository Context`.
- `06 | Restore Repository Context` [Code, 11 linhas] — OK (padrão `JSON.parse(context)`).
- `06 | Update Run Progress` [Postgres, 2151] — OK (`pages_fetched+1`, soma received/inserted/updated, rate-limit/request-id, retorna `context`) → `Restore Run Progress Context`.
- `06 | Restore Run Progress Context` [Code, 11 linhas] — DIVERGÊNCIA (nó extra vs spec: spec 06.11 diz “Depois: Restore Repository Context”; workflow tem este restore dedicado após Update + o anterior após Upsert). Funcional, só nomenclatura/quantidade.
- `06 | Has Next Page?` [IF, `has_next===true && records_received>0`] — OK (true → Reached Page Limit, false → Reconcile).
- `06 | Reached Page Limit?` [IF, `page>=max_pages`] — OK (true → Build Page Limit Failure, false → Next Page).
- `06 | Build Page Limit Failure` [Code, 38 linhas] — OK (`page_limit_exceeded`, `retryable=false`) → `90 | Record Run Failure`.
- `06 | Next Page` [Code, 18 linhas] — OK (versão preferida da spec com `delete` + `page+1/attempt=0`) → `Prepare Repository Request` (loop fecha).

## Etapa 7 — reconciliação

- `07 | Reconcile Repositories` [Postgres, 748] — OK (era `throw Etapa 7 pendente`; agora `UPDATE ... is_active=false` por `owner_login` + `last_seen_run_id IS DISTINCT FROM run_id`, retorna `records_deactivated`). Entrada OK: `Has Next Page?=false`.
- `07 | Restore Reconciliation Context` [Code, 11 linhas] — OK (padrão context).
- `07 | Complete Run` [Postgres, 897] — OK (`status='succeeded'`, `finished_at/heartbeat`, `records_deactivated`, RETURNING run). Terminal do caminho feliz — OK.

## Etapa 8 — retry/transporte/falha + caminho comum 90

- `08 | Is Retryable?` [IF, `retryable===true`] — OK (false → Non-Retryable, true → Has Attempts). Entradas OK (4 fontes): `Is Profile Success=false`, `Is Repository Success?=false`, `08 | Classify Profile Transport Error`, `Classify Repository Transport Error`.
- `08 | Has Attempts Left?` [IF, `attempt<max_retries`] — OK (true → Calculate, false → Max Retries).
- `08 | Calculate Retry Delay` [Code, 192 linhas] — OK (prioridade retry-after → reset primary → secundário 60/120/240 → transiente 5/15/45; chunk cap 3600, `wait_remaining/chunk`).
- `08 | Update Retry Heartbeat` [Postgres, 1279] — OK (heartbeat + rate-limit/request-id, retorna `context`) → `08 | Restore Retry Context`.
- `08 | Restore Retry Context` [Code, 11 linhas] — OK (spec 08.03 “Restore Context depois”, nomeado assim no workflow) → `Wait Retry Chunk`.
- `08 | Wait Retry Chunk` [Wait, `resume=timeInterval`, `amount={{$json.wait_chunk_seconds}} seconds`] — OK.
- `08 | Consume Wait Chunk` [Code, 32 linhas] — OK (`remaining=max(0,remaining-chunk)`, chunk=`min(remaining,3600)`) → `More Wait Remaining?`.
- `08 | More Wait Remaining?` [IF, `wait_remaining>0`] — OK (true → Update Retry Heartbeat = loop heartbeat/wait; false → Increment Attempt).
- `08 | Increment Attempt` [Code, 28 linhas] — OK (`attempt+1`, limpa delay/wait/status/classificação) → `Retry Target`.
- `08 | Retry Target` [Switch, `request_kind`] — OK (`profile → Prepare Profile Request`, `repositories → Prepare Repository Request`; retry volta à mesma página).
- `08 | Classify Profile Transport Error` [Code, 60 linhas] — OK (ctx de `Prepare Profile Request`, timeout/network, `retryable=true`, `safe_transport_message`, sem raw) → `Is Retryable?`. Entradas OK: erros dos 2 HTTP de perfil.
- `Classify Repository Transport Error` [Code, 59 linhas] — OK funcional, DIVERGÊNCIA nominal: spec 08.10 exige nome `08 | Classify Repository Transport Error`; workflow mantém nome sem prefixo `08 |` (era stub de 6 linhas, agora classificador completo espelhado ao de perfil, ctx de `Prepare Repository Request`) → `Is Retryable?`. Entradas OK: erros dos 2 HTTP de repositórios. Nó `08 | Classify Repository Transport Error` (com prefixo) AUSENTE — só existe o sem prefixo.
- `08 | Build Non-Retryable Failure` [Code, 54 linhas] — OK (`node_name` por `request_kind`, `retryable=false`, usa `safe_transport_message`) → `90 | Record Run Failure`.
- `08 | Build Max Retries Failure` [Code, 49 linhas] — OK (`max_retries_exceeded`) → `90 | Record Run Failure`.
- `90 | Record Run Failure` [Postgres, 1499] — OK (era query vazia; agora `UPDATE sync_runs SET status='failed'... error_code/safe_message/rate-limit/request-id`). Entradas OK (5 fontes): `Build Page Limit`, `Extract Repository`, `Extract Profile`, `Build Non-Retryable`, `Build Max Retries`.
- `90 | Restore Failure Context` [Code, 11 linhas] — OK → `Stop Main Workflow`.
- `90 | Stop Main Workflow` [StopAndError, `P01_SAFE_ERROR:{run_id/stage/node_name/http_status/request_id/category/attempt/retryable/message}`] — OK (chama Error Handler `i7QXkiz6EXgXtYnH` em execução automática).
- Rewiring perfil: `Is Profile Success=false` → `08 | Is Retryable?` — OK (spec Etapa 8). HTTP perfil agora com 2 saídas (normal + erro) — OK (antes assimétrico).

## Verificações especiais pedidas

- Has Next/Reached/Next: OK, condições e loop conferem.
- Reconcile/Complete Run: OK (Postgres + Restore + Complete; feliz termina em Complete Run).
- Is Retryable/Has Attempts/Delay/heartbeat/Wait/Consume/Increment/Retry Target: OK, cadeia completa + loop de heartbeat para rate-limit longo.
- Transport classifiers: OK funcional ambos; DIVERGÊNCIA só no nome do de repositórios (sem prefixo `08 |`).
- Record Run Failure query não vazia: OK (1499).
- Stop Main Workflow: OK (envelope `P01_SAFE_ERROR` com `node_name` do envelope — requer ajuste do Error Handler já registrado em `state-md` C1 Etapa 8).
- Rewiring Is Profile/Repository Success → Is Retryable: OK.

## Globais

- IFs: 12/12 com exatamente 2 saídas. Terminais: `07 | Complete Run`, `90 | Stop Main Workflow`, `Stop Schema Error`, `Create Skipped Sync` (órfão).
- Code<30 linhas restantes são padrão spec (restores 11, prepares 12/25, extracts 6, Next 18, Increment 28) — nenhum template `myNewField`.
- Postgres: 11/11 com query não vazia.
- Único órfão: `Create Skipped Sync` (Set, `indeg=0`, sem conexões; TC-15 pendente).
- Somente grafo; sem execução ponta-a-ponta nesta verificação.
