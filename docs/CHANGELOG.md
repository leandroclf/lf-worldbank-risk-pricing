# Changelog

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
