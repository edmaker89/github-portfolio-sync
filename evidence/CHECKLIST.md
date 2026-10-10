# Checklist de evidências — V1

Preencher após cada teste com data, fixture ou endpoint, ID da execução n8n, linha de `sync_runs`, resultado da asserção SQL, evidência sanitizada e defeito associado quando houver. `Pendente` não indica aprovação. Critérios completos: [`docs/test-plan.md`](../docs/test-plan.md).

| ID | Cenário | Resultado | Execução n8n | Asserção SQL | Evidência |
|---|---|---|---|---|---|
| TC-00A | Schema ausente; criação atômica V1 | Pendente | — | — | — |
| TC-00B | Schema V1 existente e válido | Passou | 444 | `schema_valid=true`, `schema_created=false`, migrations inalterada | [TC-00B.md](TC-00B.md) |
| TC-00C | Divergência entre versão e objetos | Pendente | — | — | — |
| TC-01 | Perfil válido e uma página de repositórios | Passou | 397 | Perfil edmaker89; run 18 succeeded, 1 página, 67 recebidos/atualizados | [TC-01.md](TC-01.md) |
| TC-02 | Mais de 100 repositórios; paginação por `Link` | Passou | 444 | 2 páginas, 101 inseridos (3001–3101), run 21 succeeded | [TC-02.md](TC-02.md) |
| TC-03 | Mesmo payload executado duas vezes | Passou | 238, 243 | Runs 3 e 4 succeeded; inserted=0, updated=67 cada; sem duplicatas | [TC-03.md](TC-03.md) |
| TC-04 | Metadados de repositório alterados | Passou | 462, 468 | 2001 JS→Python, 1 linha (UPDATE), runs 23–24 succeeded | [TC-04.md](TC-04.md) |
| TC-05 | Repositório ausente após execução completa | Passou | 397, 403, 412 | 67 reais → 3 fixture → 67 reais; runs 18–20 succeeded | [TC-05.md](TC-05.md) |
| TC-06 | Falha na página 2 após persistir página 1 | Passou | 365 | Página 1 persistida; run 16 failed; ativos inalterados | [TC-06.md](TC-06.md) |
| TC-07 | Token inválido ou ausente; HTTP 401 | Passou | 259 | Run 8 failed sem retry; ativos inalterados | [TC-07.md](TC-07.md) |
| TC-08 | Falha de permissão; HTTP 403 com cota | Passou | 280 | Run 9 failed sem retry; ativos inalterados | [TC-08.md](TC-08.md) |
| TC-09 | Limite primário; HTTP 403/429 e reset | Passou após correção do fixture | 289, 299 | 3 retries por reset; run 11 succeeded, reconciliação após snapshot completo | [TC-09.md](TC-09.md) |
| TC-10 | Limite secundário; HTTP 429 e `retry-after` | Passou após correção do fixture | 313, 327 | 3 esperas de 2 s por Retry-After; run 13 succeeded | [TC-10.md](TC-10.md) |
| TC-11 | Resposta HTTP 500 repetida | Passou | 341 | 4 HTTP 500; esperas 5/15/45 s; run 14 failed | [TC-11.md](TC-11.md) |
| TC-12 | Timeout de requisição | Passou | 383 | 4 timeouts; esperas 5/15/45 s; run 17 failed | [TC-12.md](TC-12.md) |
| TC-13 | Campo obrigatório do repositório ausente | Passou | 355 | Run 15 failed na validação de repositório; ativos inalterados | [TC-13.md](TC-13.md) |
| TC-14 | PostgreSQL indisponível na persistência | Pendente | — | — | — |
| TC-15 | Duas execuções simultâneas para o mesmo owner | Passou | 248, 249 | Run 5 succeeded; run 7 skipped, error_code=concurrent_run | [TC-15.md](TC-15.md) |
| TC-16 | API oferece 11ª página com `MAX_PAGES=10` | Passou | 477 | 10 páginas, run 25 failed `page_limit_exceeded`, page11 nunca pedida, 0 desativados | [TC-16.md](TC-16.md) |
| TC-17 | Sincronização live de `edmaker89` | Passou | 412 | Run 20 succeeded; perfil+67 repositórios live; sem segredos em evidências | [TC-17.md](TC-17.md) |
| EH-01 | Error Handler persiste contexto sanitizado em `sync_errors` em execução de produção | Passou | 423 | `sync_errors` id=1 (run 20), category=authentication, http 401, sem vazamento | [ERROR-HANDLER.md](ERROR-HANDLER.md) |

Nota: nas execuções **manuais** da suíte Etapa 8 (ver [`ETAPA8-EXECUCAO.md`](ETAPA8-EXECUCAO.md)), o Error Handler (`i7QXkiz6EXgXtYnH`) estava ativo, mas falhas de execução manual não disparam o Error Handler do n8n nem gravam `sync_errors`. A persistência foi comprovada separadamente em **execução de produção** via webhook (`github-sync/error-handler-test`, execução 423), registrada em `EH-01`/`ERROR-HANDLER.md`.
