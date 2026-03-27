# Changelog

## 2026-03-26
- **ISSUE-014 concluída**: adicionada telemetria do caminho World Bank com contagem por endpoint, latência de fetch, latência de batch, fallback-year usage, freshness age e cost proxy
- **ISSUE-015 concluída**: adicionados contratos de qualidade por fonte para World Bank com owner/remediation path e validação determinística do boundary para payloads malformados
- Adicionados testes para snapshot de telemetria e validação HTTP do batch

## 2026-02-28
- **ISSUE-003 concluída**: Merge da feature branch `feature/issue-003-worldbank-risk-score-api` para main
- Implementado API endpoint `/v1/risk-score` (single e batch queries)
- Adicionado módulo `risk_score_endpoint.py` com validação de country codes
- Criada documentação completa: `API_ENDPOINT_SPEC.md` e `PILOT_PROPOSALS.md`
- Adicionados testes: `test_risk_score_endpoint.py` e `smoke_test_endpoint.py`
- KPIs evidenciados: 99.94% redução de tempo, $26,600/ano de valor
- Smoke tests passando: endpoint, features e check original

## 2026-02-25
- Bootstrap do repositório.
