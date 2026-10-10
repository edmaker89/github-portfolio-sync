# Graph check — Etapa 6 — Portifolio Sync (u8oHC2DBgZUGMZUH)

- Fonte: `GET /api/v1/workflows/u8oHC2DBgZUGMZUH` exportado para `/tmp/e6m.json` em 2026-10-10 (somente leitura, sem commit, sem edição n8n).
- Workflow: `Portifolio Sync`, `active=false`, `settings.executionOrder=v1`, `settings.errorWorkflow=i7QXkiz6EXgXtYnH`.
- Contagem: 47 nós, 41 origens em `connections`, 52 arestas (destinos).
- Spec Etapa 6: `maestri note read "regras"` inicialmente falhou (`No connection`), depois conectada via canvas (`Connected "regras" ↔ "MuseSparkFree"`) e lida integralmente (2481 linhas: 06.00–06.15 + Etapa 7 + Etapa 8 + caminho comum 90). Comparação abaixo é contra `regras` + `state-md` + `docs/architecture.md` + `docs/test-plan.md`.

## 1. Conexões apontam para nó existente?

- OK: todas as 52 arestas apontam para nomes existentes. Nenhum `MISSING`.

## 2. Alcançabilidade a partir de trigger?

- Triggers: `Manual Trigger`, `Schedule Trigger` → `Runtime Configuration`.
- Alcançáveis: 46/47.
- Inalcançável / órfão:
  - `Create Skipped Sync` [Set] — `indeg=0`, sem entrada, sem saída, fora do fluxo. Era esperado para concorrência (TC-15 / arquitetura “skipped”), mas está desconectado.

## 3. Nós IF possuem exatamente true/false?

- 9 IFs, todos com `main[0]` + `main[1]` com 1 destino cada — OK estrutural:
  - `Is Schema Ready?` → `Close Stale Runs` / `Execute a SQL query`
  - `Is Profile Success` → `Normalize Profile` / `Build Profile HTTP Failure`
  - `Is Profile Valid?` → `Upsert Profile` / `Extract Profile Failure`
  - `API Mode?` → `Simulator | Profile Request1` / `Simulator | Profile Request`
  - `Repository API Mode` → `Live | Get Repositories` / `Simulator | Get Repositories`
  - `06 | Is Repository Success?` (`classification==='success'`) → `06 | Normalize Repository Page` / `06 | Build Repository HTTP Failure (Etapa 8 pendente)`
  - `06 | Is Repository Page Valid?` (`valid===true`) → `06 | Upsert Repository Page` / `06 | Extract Repository Failure`
  - `06 | Has Next Page?` (`has_next===true && records_received>0`) → `06 | Reached Page Limit?` / `07 | Reconcile Repositories`
  - `06 | Reached Page Limit?` (`page>=max_pages`) → `06 | Build Page Limit Failure` / `06 | Next Page`
- Condições plausíveis para paginação/limite (TC-02/TC-16), mas sem validação de `Link rel="next"` no grafo — depende de `Classify/Normalize` (não auditado aqui).

## 4. Stubs / órfãos suspeitos

- Code com poucas linhas (<30):
  - `06 | Extract Repository Failure` — 6 linhas, só `return $input.first().json.failure` (igual a `Extract Profile Failure`). Passthrough sem enriquecimento — suspeito/stub.
  - `Extract Profile Failure` — 6 linhas, idem.
  - `Classify Repository Transport Error` — 6 linhas, template padrão `myNewField=1`, terminal sem saída. Stub confirmado — erros de transporte de repositórios caem em dead-end.
  - `07 | Reconcile Repositories` — 1 linha `throw Etapa 7 pendente`, terminal sem saída. Placeholder Etapa 7 — happy-path (`Has Next Page?=false`) termina aqui.
  - `06 | Next Page` — 18 linhas (incrementa `page`, zera `attempt`, remove contadores). Curto mas funcional — não classificado como stub.
  - `06 | Restore Repository Context`, `06 | Restore Run Progress Context`, `Restore Profile Context` — 11 linhas cada (`JSON.parse(context)`). Funcionais, porém triplicados.
  - `Prepare Profile Request` — 12 linhas, `Prepare Repository Request` — 25 linhas (valida `page>=1`). Funcionais.
- Postgres com query vazia:
  - `Record Run Failure` — `op=executeQuery`, `query_len=0`. Placeholder quebrado. Recebe de `06 | Build Page Limit Failure`, `06 | Build Repository HTTP Failure`, `06 | Extract Repository Failure`, `Extract Profile Failure` — todos os caminhos de falha de Etapa 6 terminam em nó sem SQL.
  - Demais Postgres OK com SQL não-vazia: `06 | Update Run Progress` (2151), `06 | Upsert Repository Page` (4326), `Close Stale Runs`, `Create Running Sync`, `Execute a SQL query`, `Update Run Profile Metadata` (1276), `Upsert Profile` (2118).
- Terminais sem saída (6):
  - `07 | Reconcile Repositories`, `Classify Repository Transport Error`, `Build Profile HTTP Failure`, `Record Run Failure`, `Stop Schema Error`, `Create Skipped Sync`.
  - `Build Profile HTTP Failure` (47 linhas, bem formado) é terminal — deveria alimentar `Record Run Failure` mas não tem aresta.
  - HTTP profile (`Simulator | Profile Request`, `Simulator | Profile Request1`) têm só 1 saída para `Classify Profile Response`, sem ramo de erro — assimétrico com `Live/Simulator | Get Repositories` que têm 2 saídas (`Classify Repository Response` + `Classify Repository Transport Error`).

## 5. Divergências vs spec Etapa 6 (`regras` 06.00–06.15)

- Conformes (Etapa 6):
  - `Init → Prepare → Repository API Mode → Live/Simulator → Classify → Is Success → Normalize (492 linhas) → Is Valid → Upsert → Restore → Update Progress → Has Next → Reached Limit → Next → loop Prepare`: cadeia presente, `If (http_status===200)` removido, `Init` usa `owner_login=x.profile.login`, `Next Page` usa versão preferida com `delete` (18 linhas), HTTP Live/Sim com URL `/users/.../repos`, query `type=owner/sort=updated/direction=desc/per_page=100/page`, headers `Accept/X-GitHub-Api-Version`, `timeout={{$json.timeout_ms}}`, `neverError=true/fullResponse/pagination OFF`, Simulator com `scenario/attempt` — todos OK. `Upsert Repository Page` e `Update Run Progress` com SQL completa e `queryReplacement={{JSON.stringify($json)}}` — OK. `Is Success=false` → `Build Repository HTTP Failure` corresponde ao “Etapa 6 inicialmente” da spec (Etapa 8 ainda pendente) — esperado.
  - `Extract Repository Failure` (6 linhas passthrough) é idêntico à spec 06.08 — spec-conforme, não stub extra.
- Divergentes (Etapa 6):
  - `06.00 Init`: spec lê `$input.first().json` direto; workflow lê `$input.first().json.context` (adaptado ao upstream `Update Run Profile Metadata` que retorna `input.j AS context`). Funcional, mas diverge do texto da spec.
  - `06.02 Repository API Mode`: spec diz “Switch”; workflow usa `IF` (2 saídas, funcionalmente equivalente, mesma divergência já existente em `API Mode?` do perfil).
  - `06.05 Classify`: spec referencia `$('06 | Prepare Repository Request')`; workflow usa `$('Prepare Repository Request')` (nó real é sem prefixo `06 |`). Internamente consistente, mas quebra se copiar o código da spec literalmente.
  - `06.11 pós-Update`: spec diz “Depois: Restore Repository Context”; workflow tem nó extra `06 | Restore Run Progress Context` (duplicata de 11 linhas) entre `Update Run Progress` e `Has Next` — além do `Restore Repository Context` após Upsert. Extra vs spec.
  - Saídas de erro HTTP: spec exige `Error output → 08 | Classify Repository Transport Error`; workflow tem `Error output → Classify Repository Transport Error` (nome sem `08 |`, 6 linhas template `myNewField=1`, terminal). Nome + conteúdo divergem da spec 08.10 (classificador completo com `ctx` + timeout/network + `retryable=true` → `Is Retryable?`).
- Pendentes fora da Etapa 6 (bloqueios):
  - `90 | Record Run Failure`: spec 90.00 define `UPDATE sync_runs SET status='failed'...`; workflow tem `Record Run Failure` com `query_len=0` (vazio). Todos os fails da Etapa 6 (`Build Page Limit`, `Build Repository HTTP`, `Extract Repository/Profile Failure`) terminam aqui sem persistir — quebra TC-06/TC-13/TC-16.
  - Etapa 7: spec 07.00–07.02 exige `Reconcile (Postgres)` + `Restore Reconciliation Context` + `Complete Run (succeeded)`; workflow tem `07 | Reconcile Repositories` = `throw Etapa 7 pendente`, terminal. Happy-path termina em erro — viola reconciliação/TC-05. Obs: `maestri check OpenCode` mostra C1 etapa7 em andamento (49 nós) após este export de 47 nós.
  - Etapa 8: sem `Is Retryable?/Has Attempts/Calculate Delay/Update Retry Heartbeat/Wait/Consume/More Wait?/Increment/Retry Target/Build Non-Retryable/Build Max Retries` (TC-07..TC-12); `Build Profile HTTP Failure` terminal sem aresta para falha comum; HTTP de perfil sem ramo de erro (assimétrico).
  - `Create Skipped Sync` órfão desconectado — quebra TC-15.
- Vs `state-md` C1: 11 nós FALTANTES agora presentes + `Restore Run Progress Context` extra; contagens conferem (47 nós / 52 arestas / `errorWorkflow` / `v1` / `active=false`).

## 6. Resumo objetivo

- Grafo íntegro em referências (52/52) e IFs (9/9 com 2 saídas), 46/47 alcançáveis.
- Etapa 6 conforme `regras` na cadeia principal e HTTP/Classify/Normalize/Upsert/Update/HasNext/Limit/Next; divergências pontuais: `Init` lê `.json.context`, `Mode` é IF não Switch, `Classify` usa `$('Prepare...')` sem prefixo, `Restore Run Progress Context` extra, erro HTTP vai para stub sem prefixo `08 |`.
- Bloqueios fora da Etapa 6: `Record Run Failure` vazio, `Classify Transport` stub terminal, `07 Reconcile` placeholder terminal, `Create Skipped Sync` órfão, `Build Profile Failure` terminal, HTTP perfil sem ramo erro.
- Somente grafo, sem execução ponta-a-ponta; export reflete 47 nós pré-etapa7.
