# lf-worldbank-risk-pricing: Módulo de Risco-País e Pricing (ISSUE-003)

## Visão Geral

Este repositório contém o Mínimo Produto Viável (MVP) do componente de Risco-País e Pricing, utilizando dados do World Bank para analisar e aplicar fatores de risco em estratégias de precificação. O objetivo é permitir uma precificação regionalizada e dinâmica, ajustada aos riscos e oportunidades de cada mercado.

## Contexto e Issue

Desenvolvido sob a **ISSUE-003: Módulo de risco-país e pricing regional com World Bank**, este componente é fundamental para a otimização de receita e a mitigação de riscos em operações globais, garantindo que os preços reflitam as realidades econômicas locais.

## Problema Resolvido

A precificação uniforme em diferentes mercados pode levar à perda de oportunidades (em mercados estáveis) ou a prejuízos (em mercados voláteis). Este componente resolve esse problema, fornecendo uma estrutura baseada em dados para calcular e aplicar multiplicadores de preço e ajustes de risco por país e região.

## Objetivo do MVP

O MVP visa criar uma base para a análise de risco e pricing regional, com as seguintes capacidades:

*   **Scoring de Risco:** Validar e utilizar scores de risco por país.
*   **Agregação de Portfólio:** Calcular o risco agregado de um portfólio de ativos distribuídos em diferentes países.
*   **Cálculo de Multiplicador:** Definir e calcular multiplicadores de preço com base no risco-país.
*   **Análise de Risco Regional:** Agregar dados de risco por região (LATAM, EMEA, APAC, NA) para análise macro.
*   **Estimativa de Ajuste:** Estimar o percentual de ajuste necessário para um portfólio com base no risco.

## Objetivo Final em Produção (Visão Estratégica)

Quando em produção, o `lf-worldbank-risk-pricing` será um motor de pricing dinâmico e inteligente, capaz de:

*   **Pricing Automatizado e Dinâmico:** Ajustar preços de produtos e serviços em tempo real, com base em flutuações de risco e indicadores macroeconômicos.
*   **Simulação de Cenários:** Permitir a simulação de diferentes cenários de risco e seu impacto na receita e margens.
*   **Otimização de Margem:** Maximizar a margem de lucro por região, equilibrando competitividade e exposição ao risco.
*   **Forecasting de Risco:** Utilizar modelos preditivos para antecipar mudanças no risco-país e ajustar a estratégia de pricing proativamente.

## Funcionalidades Chave Implementadas (MVP)

*   `score_pricing_portfolio()`: Agrega o risco e o multiplicador médio para um portfólio.
*   `summarize_country_risk_bands()`: Sumariza países por banda de risco.
*   `estimate_portfolio_adjustment_pct()`: Estima o ajuste percentual do portfólio.
*   `summarize_pricing_tiers_with_multiplier()`: Sumariza tiers de preço com multiplicadores.
*   `aggregate_regional_risk()`: Agrega scores de risco por região.
*   `calculate_portfolio_exposure()`: Calcula a exposição ponderada do portfólio ao risco.

## Estratégia e Abordagem

O desenvolvimento segue uma abordagem modular, onde novos fatores de risco e modelos de pricing podem ser adicionados incrementalmente. A validação contínua dos dados do World Bank e a testabilidade das funções de cálculo são cruciais para a confiabilidade do sistema.

## Stack Técnica

*   **Linguagem:** Python
*   **Ferramentas:** Git, GitHub Actions (CI/CD)
*   **Dados:** World Bank (fonte primária).

## Como Começar

Para configurar e executar o projeto localmente:

1.  **Clone o repositório:**
    `git clone https://github.com/leandroclf/lf-worldbank-risk-pricing.git`
    `cd lf-worldbank-risk-pricing`
2.  **Instale as dependências:**
    `pip install -r requirements.txt` (se houver, ou adicione conforme necessário)
3.  **Execute testes:**
    `PYTHONPATH=. python3 -c "from backend.src.api import aggregate_regional_risk; ..."` (Exemplo de execução de função)
    `# Ou se pytest estiver configurado: pytest`
    `PYTHONPATH=. python3 tools/smoke_check.py` (para smoke tests)

## Diretrizes de Contribuição

Este projeto adota um fluxo de trabalho de desenvolvimento que permite **commit direto na branch `main`**. Pull Requests são opcionais e encorajados para revisão colaborativa, mas não são obrigatórios para a integração de código.

## Governança

*   **Proprietário Primário (`ownerPrimary`):** Builder-repo
*   **Categoria Primária (`categoryPrimary`):** Engenharia-Arquitetura
*   **KPI de Valor (`valueKpi`):** % de otimização de margem por região; redução de perdas em mercados voláteis.

---
_Gerado por Stephen (agente) em 2026-02-27. Ref.: ISSUE-003._
