# lf-worldbank-risk-pricing

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

API de scoring de risco-país e pricing dinâmico regional, construída sobre dados públicos do **World Bank**. Permite calcular o risco de um país, processar portfólios em lote e gerar cotações de preço ajustadas ao risco em tempo real.

**URL de Produção:** [`https://lf-worldbank-risk-pricing.onrender.com`](https://lf-worldbank-risk-pricing.onrender.com)

---

## Sumário

- [Descrição](#descrição)
- [Endpoints](#endpoints)
- [Regras de Tier](#regras-de-tier)
- [Quick Start](#quick-start)
- [Exemplos curl](#exemplos-curl)
- [Integração Sistêmica](#integração-sistêmica)
- [Documentação e Postman](#documentação-e-postman)
- [Como importar no Postman](#como-importar-no-postman)
- [Attribution](#attribution)

---

## Descrição

O `lf-worldbank-risk-pricing` é um motor de pricing dinâmico que:

- Calcula o **score de risco** de países usando indicadores macroeconômicos do World Bank
- Classifica países em **tiers de risco** (low, medium, high)
- Aplica **multiplicadores de preço** com base no tier
- Processa **lotes de países** para análise de portfólios
- Gera **cotações detalhadas** com rastreabilidade completa do cálculo

---

## Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Verificação de saúde do serviço |
| `GET` | `/sample` | Payload de exemplo da API |
| `GET` | `/v1/risk-score` | Score de risco de um país (`?country_code=BR`) |
| `POST` | `/v1/risk-score/batch` | Scores de risco em lote para múltiplos países |
| `POST` | `/v1/pricing/bands` | Bandas de pricing com tier e multiplicador |
| `POST` | `/v1/pricing/quote` | Cotação de preço ajustada ao risco |

---

## Regras de Tier

| Tier | Condição | Ajuste aplicado |
|------|----------|-----------------|
| `high` | riskScore >= 75 | +8% |
| `medium` | 50 <= riskScore < 75 | +3% |
| `low` | riskScore < 50 | +0% |

---

## Quick Start

### 1. Clone o repositório

```bash
git clone https://github.com/leandroclf/lf-worldbank-risk-pricing.git
cd lf-worldbank-risk-pricing
```

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Rode o servidor localmente

```bash
uvicorn src.main:app --reload --port 8000
# ou
python -m src.main
```

A API estará disponível em `http://localhost:8000`.

### 5. Execute os testes

```bash
PYTHONPATH=. pytest
# ou
PYTHONPATH=. python3 tools/smoke_check.py
```

---

## Exemplos curl

### Health check

```bash
curl https://lf-worldbank-risk-pricing.onrender.com/health
```

```json
{"status":"ok","service":"lf-worldbank-risk-pricing"}
```

### Payload de exemplo

```bash
curl https://lf-worldbank-risk-pricing.onrender.com/sample
```

### Score de risco — país único

```bash
curl "https://lf-worldbank-risk-pricing.onrender.com/v1/risk-score?country_code=BR"
```

```json
{
  "countryCode": "BR",
  "riskScore": 62,
  "tier": "medium",
  "sourceAttribution": "World Bank (CC BY 4.0)"
}
```

### Score de risco — lote

```bash
curl -X POST https://lf-worldbank-risk-pricing.onrender.com/v1/risk-score/batch \
  -H "Content-Type: application/json" \
  -d '{"country_codes": ["BR", "US", "DE"]}'
```

```json
[
  {"countryCode": "BR", "riskScore": 62, "tier": "medium", "sourceAttribution": "World Bank (CC BY 4.0)"},
  {"countryCode": "US", "riskScore": 22, "tier": "low",    "sourceAttribution": "World Bank (CC BY 4.0)"},
  {"countryCode": "DE", "riskScore": 18, "tier": "low",    "sourceAttribution": "World Bank (CC BY 4.0)"}
]
```

### Bandas de pricing

```bash
curl -X POST https://lf-worldbank-risk-pricing.onrender.com/v1/pricing/bands \
  -H "Content-Type: application/json" \
  -d '{"entries": [{"countryCode": "BR", "riskScore": 62, "basePrice": 1000}]}'
```

### Cotação de preço

```bash
curl -X POST https://lf-worldbank-risk-pricing.onrender.com/v1/pricing/quote \
  -H "Content-Type: application/json" \
  -d '{"countryCode": "BR", "riskScore": 62, "basePrice": 1000, "currency": "USD"}'
```

```json
{
  "countryCode": "BR",
  "riskScore": 62,
  "tier": "medium",
  "adjustment": 3,
  "multiplier": 1.03,
  "basePrice": 1000,
  "finalPrice": 1030.0,
  "currency": "USD",
  "generatedAtHttp": "..."
}
```

---

## Integração Sistêmica

### Python

```python
import requests

BASE_URL = "https://lf-worldbank-risk-pricing.onrender.com"

# Score de risco único
response = requests.get(f"{BASE_URL}/v1/risk-score", params={"country_code": "BR"})
data = response.json()
print(data["riskScore"], data["tier"])

# Lote de países
batch = requests.post(
    f"{BASE_URL}/v1/risk-score/batch",
    json={"country_codes": ["BR", "US", "DE"]}
)
for country in batch.json():
    print(f"{country['countryCode']}: {country['riskScore']} ({country['tier']})")

# Cotação de preço
quote = requests.post(
    f"{BASE_URL}/v1/pricing/quote",
    json={"countryCode": "BR", "riskScore": 62, "basePrice": 1000, "currency": "USD"}
)
result = quote.json()
print(f"Preço final: {result['finalPrice']} {result['currency']}")
```

### JavaScript / Node.js

```javascript
const BASE_URL = "https://lf-worldbank-risk-pricing.onrender.com";

// Score de risco único
const riskRes = await fetch(`${BASE_URL}/v1/risk-score?country_code=BR`);
const risk = await riskRes.json();
console.log(risk.riskScore, risk.tier);

// Cotação de preço
const quoteRes = await fetch(`${BASE_URL}/v1/pricing/quote`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    countryCode: "BR",
    riskScore: 62,
    basePrice: 1000,
    currency: "USD"
  })
});
const quote = await quoteRes.json();
console.log(`Preço final: ${quote.finalPrice} ${quote.currency}`);
```

### curl (script shell)

```bash
#!/bin/bash
BASE="https://lf-worldbank-risk-pricing.onrender.com"

# Score de risco
curl -s "$BASE/v1/risk-score?country_code=BR" | jq .

# Cotação
curl -s -X POST "$BASE/v1/pricing/quote" \
  -H "Content-Type: application/json" \
  -d '{"countryCode":"BR","riskScore":62,"basePrice":1000,"currency":"USD"}' | jq .
```

---

## Documentação e Postman

| Arquivo | Descrição |
|---------|-----------|
| [`docs/openapi.yaml`](docs/openapi.yaml) | Especificação OpenAPI 3.0 completa |
| [`docs/postman_collection.json`](docs/postman_collection.json) | Coleção Postman com todos os endpoints |
| [`docs/postman_environment.json`](docs/postman_environment.json) | Environment Postman (produção e local) |

---

## Como importar no Postman

### Importar a coleção

1. Abra o **Postman**
2. Clique em **Import** (botão no canto superior esquerdo)
3. Selecione **File** e escolha `docs/postman_collection.json`
4. Clique em **Import**

### Importar o environment

1. No Postman, clique em **Environments** (ícone de olho ou painel lateral)
2. Clique em **Import**
3. Selecione `docs/postman_environment.json`
4. Após importar, selecione o environment **lf-worldbank-risk-pricing** no seletor do canto superior direito
5. Todas as requests usarão automaticamente a variável `{{base_url}}`

### Trocar entre produção e local

- Para usar produção: a variável `base_url` já está configurada como `https://lf-worldbank-risk-pricing.onrender.com`
- Para usar local: edite o environment e mude o valor de `base_url` para `{{base_url_local}}` (`http://localhost:8000`)

---

## Attribution

Os dados de risco-país utilizados neste projeto são derivados de indicadores públicos do **World Bank**, disponíveis sob a licença **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

- Fonte: [World Bank Open Data](https://data.worldbank.org)
- Licença: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

_Desenvolvido por Leandro Freire — Ref.: ISSUE-003_
