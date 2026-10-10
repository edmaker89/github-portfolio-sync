# Verificação técnica final — workflow Portifolio Sync (u8oHC2DBgZUGMZUH)

**Instância:** https://n8n-homelab.edmaker.dev.br · **Export:** `/tmp/final.json` (GET somente-leitura)

**Regras respeitadas:** sem edição no n8n, sem commit, chave não exposta (lida via `.env`).

## Contagens

| Métrica | Valor |
|---|---|
| Nós totais | 62 |
| Conexões | 75 |
| Nós Code | 26 (26 sintaxe ok / 0 erro) |
| Nós IF | 12 (12 ok / 0 aviso / 0 erro) |
| Triggers (sem entrada) | 3 |
| Nós terminais (sem saída) | 4 |
| Nós inalcançáveis | 0 |
| Erros | 0 |
| Avisos | 0 |

## Checagens

### (a) Conexões → nós existentes

Todas as 75 conexões apontam para nós existentes. Nenhuma origem ou destino órfão de conexão.

### (b) Sintaxe JS dos nós Code (`node --check`)

26/26 `parameters.jsCode` válidos sintaticamente.

| Nó | ok/erro | linhas |
|---|---|---|
| `Validate Configuration` | ok | 138 |
| `Build Sync Context` | ok | 39 |
| `Prepare Profile Request` | ok | 12 |
| `Classify Profile Response` | ok | 292 |
| `Normalize Profile` | ok | 358 |
| `Extract Profile Failure` | ok | 6 |
| `Restore Profile Context` | ok | 11 |
| `Init Repository Pagination` | ok | 49 |
| `Prepare Repository Request` | ok | 25 |
| `Classify Repository Response` | ok | 264 |
| `Classify Repository Transport Error` | ok | 59 |
| `06 | Normalize Repository Page` | ok | 492 |
| `06 | Extract Repository Failure` | ok | 6 |
| `06 | Restore Repository Context` | ok | 11 |
| `06 | Restore Run Progress Context` | ok | 11 |
| `06 | Build Page Limit Failure` | ok | 38 |
| `06 | Next Page` | ok | 18 |
| `07 | Restore Reconciliation Context` | ok | 11 |
| `08 | Calculate Retry Delay` | ok | 192 |
| `08 | Restore Retry Context` | ok | 11 |
| `08 | Consume Wait Chunk` | ok | 32 |
| `08 | Increment Attempt` | ok | 28 |
| `08 | Classify Profile Transport Error` | ok | 60 |
| `08 | Build Non-Retryable Failure` | ok | 54 |
| `08 | Build Max Retries Failure` | ok | 49 |
| `90 | Restore Failure Context` | ok | 11 |

### (c) Saídas dos nós IF

12/12 nós IF com ambas as saídas (true/false) conectadas.

| Nó | saída true | saída false | status |
|---|---|---|---|
| `Is Schema Ready?` | 1 | 1 | ok |
| `API Mode?` | 1 | 1 | ok |
| `Is Profile Success` | 1 | 1 | ok |
| `Is Profile Valid?` | 1 | 1 | ok |
| `Repository API Mode` | 1 | 1 | ok |
| `06 | Is Repository Success?` | 1 | 1 | ok |
| `06 | Is Repository Page Valid?` | 1 | 1 | ok |
| `06 | Has Next Page?` | 1 | 1 | ok |
| `06 | Reached Page Limit?` | 1 | 1 | ok |
| `08 | Is Retryable?` | 1 | 1 | ok |
| `08 | Has Attempts Left?` | 1 | 1 | ok |
| `08 | More Wait Remaining?` | 1 | 1 | ok |

### (d) Terminais e inalcançáveis

**Gatilhos (nós sem entrada):**
- `Manual Trigger` (n8n-nodes-base.manualTrigger)
- `Schedule Trigger` (n8n-nodes-base.scheduleTrigger)
- `Create Skipped Sync` (n8n-nodes-base.set)

**Nós terminais (sem saída):**
- `07 | Complete Run` (n8n-nodes-base.postgres)
- `90 | Stop Main Workflow` (n8n-nodes-base.stopAndError)
- `Create Skipped Sync` (n8n-nodes-base.set)
- `Stop Schema Error` (n8n-nodes-base.stopAndError)

**Nós inalcançáveis a partir dos triggers:** nenhum.

**Nó sem conexão alguma (isolado):** `Create Skipped Sync` — atua como gatilho e terminal simultaneamente (nó de fallback/skip sem wiring no export).

## Erros e avisos

- **Erros:** nenhum.
- **Avisos:** `Create Skipped Sync` está isolado (sem conexões), o que o torna alcançável apenas se referenciado por `errorWorkflow` ou execução direta; os demais checks passaram limpos.
