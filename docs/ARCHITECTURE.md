# Arquitetura inicial — lf-worldbank-risk-pricing

## Especialistas responsáveis
- Arquiteto: architect-tech
- Infra/CI-CD: sre-cost-specialist
- Backend: builder-repo
- Frontend/UI: architect-tech

## Componentes
- backend/src/service.py: núcleo de serviço
- backend/src/worldbank_governance.py: telemetry de baseline e contratos de qualidade por fonte
- frontend/index.html: camada de visualização inicial
- infra/docker-compose.yml: execução local mínima
- .github/workflows/ci.yml: validações básicas de CI

## Próximo incremento
1. Instrumentar o caminho atual do World Bank com baseline de custo/performance
2. Expor contratos de qualidade por fonte com owner e remediation path
3. Medir qualidade/cobertura sem expandir a superfície pública


## V0.3
- Endpoint HTTP `/health` e `/sample`
- Frontend consumindo endpoint com fallback local
- Teste de contrato de payload

## V0.4
- Telemetria do World Bank registra contagem por endpoint, latência de fetch, latência de batch, fallback-year usage, freshness age e contrato de qualidade
- Validação de boundary rejeita payloads JSON malformados e batches com country codes inválidos antes do dispatch
