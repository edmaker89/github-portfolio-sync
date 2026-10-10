# Workflows n8n — snapshots

Os arquivos `01` a `05` nesta pasta são snapshots brutos obtidos por `GET /api/v1/workflows/{id}` em 2026-10-10, após a implementação e testes das Etapas 6, 7 e 8 (versão testada da suíte descrita em [`evidence/ETAPA8-EXECUCAO.md`](../evidence/ETAPA8-EXECUCAO.md)). Os snapshots brutos ficam locais e são ignorados pelo Git. Cópias de linha de base anteriores às Etapas 6–8 permanecem como `*.pre-etapa*.json` nesta pasta.

As cópias em [`sanitized/`](sanitized/) são para revisão e versionamento. O script [`scripts/sanitize_workflows.py`](../scripts/sanitize_workflows.py) substitui, em todo o JSON (inclusive `activeVersion`), cada ID e nome real de credencial por placeholders `REPLACE_WITH_CREDENTIAL_XX_ID` e `REPLACE_WITH_CREDENTIAL_XX_NAME`. A mesma credencial recebe o mesmo placeholder nos cinco arquivos. O script também limpa `pinData` (amostras de execução) e `shared` (vínculos do projeto n8n). Não edite os snapshots brutos para fazer a sanitização.

## Ordem para restaurar em outra instância

1. `02-ensure-database-schema.json` — cria ou valida o schema V1.
2. `03-error-handler.json` — recebe erros do fluxo principal.
3. `04-github-api-simulator.json` — endpoint usado nos testes.
4. `05-error-handler-test.json` — apoio ao teste do tratamento de erros.
5. `01-portifolio-sync.json` — fluxo principal; depende do schema e do tratamento de erros.

Antes de ativar, associe as credenciais no destino e atualize referências a IDs de workflows, URLs do simulador e configuração de Error Workflow. Os arquivos da API contêm metadados da instância original; a importação pode exigir ajuste ao formato aceito pela versão do n8n. Confirme a configuração dos webhooks e ative apenas os fluxos necessários.
