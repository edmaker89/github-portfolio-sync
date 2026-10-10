# Relatório de sintaxe JS — nós Code (Etapa 6)

**Workflow:** Portifolio Sync (`u8oHC2DBgZUGMZUH`) — https://n8n-homelab.edmaker.dev.br

**Escopo:** todos os nós com `type == "n8n-nodes-base.code"`; validação de sintaxe do campo `parameters.jsCode` via `node --check`. Somente leitura — nenhum commit ou alteração no n8n.

**Resultado:** 20 ok / 0 erro(s) — 20 nós no total.

| Nó | ok/erro | nº de linhas | mensagem de erro (se houver) |
|---|---|---|---|
| `Validate Configuration` | ok | 138 | — |
| `Build Sync Context` | ok | 39 | — |
| `Prepare Profile Request` | ok | 12 | — |
| `Classify Profile Response` | ok | 292 | — |
| `Build Profile HTTP Failure` | ok | 47 | — |
| `Normalize Profile` | ok | 358 | — |
| `Extract Profile Failure` | ok | 6 | — |
| `Restore Profile Context` | ok | 11 | — |
| `Init Repository Pagination` | ok | 49 | — |
| `Prepare Repository Request` | ok | 25 | — |
| `Classify Repository Response` | ok | 264 | — |
| `Classify Repository Transport Error` | ok | 6 | — |
| `06 \| Normalize Repository Page` | ok | 492 | — |
| `06 \| Extract Repository Failure` | ok | 6 | — |
| `06 \| Restore Repository Context` | ok | 11 | — |
| `06 \| Restore Run Progress Context` | ok | 11 | — |
| `06 \| Build Page Limit Failure` | ok | 38 | — |
| `06 \| Next Page` | ok | 18 | — |
| `06 \| Build Repository HTTP Failure (Etapa 8 pendente)` | ok | 47 | — |
| `07 \| Reconcile Repositories` | ok | 1 | — |
