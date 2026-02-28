# Risk Score API Endpoint Specification

**Issue:** ISSUE-003  
**Version:** v1  
**Created:** 2026-02-27  
**Status:** Implementation Complete

## Overview

This document specifies the API endpoint for retrieving country risk scores based on World Bank data. The endpoint supports both single country queries and batch requests.

## Base Endpoint

### Single Country Query

```
GET /v1/risk-score?country_code={COUNTRY_CODE}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| country_code | string | Yes | 2-letter ISO country code (e.g., 'BR', 'US', 'DE') |

#### Success Response (200 OK)

```json
{
  "country_code": "BR",
  "risk_score": 5.23,
  "data_freshness": "2023",
  "source_attribution": "World Bank (CC BY 4.0)",
  "timestamp": "2026-02-27T22:00:00Z"
}
```

#### Error Response - Invalid Country Code (400 Bad Request)

```json
{
  "error": "Invalid country code",
  "message": "Country code must be a 2-letter ISO code",
  "country_code": "BRA",
  "timestamp": "2026-02-27T22:00:00Z"
}
```

#### Error Response - Data Not Available (404 Not Found)

```json
{
  "error": "Data not available",
  "message": "No risk data available for country: XX",
  "country_code": "XX",
  "source_attribution": "World Bank (CC BY 4.0)",
  "timestamp": "2026-02-27T22:00:00Z"
}
```

### Batch Query

```
POST /v1/risk-score/batch
```

#### Request Body

```json
{
  "country_codes": ["BR", "US", "DE", "CN"]
}
```

#### Success Response (200 OK)

```json
{
  "results": [
    {
      "country_code": "BR",
      "risk_score": 5.23,
      "data_freshness": "2023",
      "source_attribution": "World Bank (CC BY 4.0)",
      "timestamp": "2026-02-27T22:00:00Z"
    },
    {
      "error": "Data not available",
      "message": "No risk data available for country: XX",
      "country_code": "XX",
      "source_attribution": "World Bank (CC BY 4.0)",
      "timestamp": "2026-02-27T22:00:00Z"
    }
  ],
  "total": 4,
  "successful": 3,
  "failed": 1,
  "timestamp": "2026-02-27T22:00:00Z"
}
```

## Response Fields

### Common Fields

| Field | Type | Description |
|-------|------|-------------|
| country_code | string | Uppercase 2-letter ISO country code |
| timestamp | string | ISO 8601 timestamp of the response |
| source_attribution | string | Always "World Bank (CC BY 4.0)" for licensing compliance |

### Success Fields

| Field | Type | Description |
|-------|------|-------------|
| risk_score | number | Risk premium value (0-100 scale) |
| data_freshness | string | Year of the data (e.g., "2023") |

### Error Fields

| Field | Type | Description |
|-------|------|-------------|
| error | string | Error type identifier |
| message | string | Human-readable error description |

## Data Source

- **Source:** World Bank Open Data
- **Indicator:** FR.INR.RISK - Risk premium on lending (lending rate minus treasury bill rate, %)
- **License:** CC BY 4.0
- **Attribution Required:** Yes (included in all responses)
- **API Documentation:** https://api.worldbank.org/v2/

## Implementation Notes

### Data Freshness

- World Bank data is typically updated annually
- The API attempts to fetch the most recent available data
- Fallback mechanism tries current year, then previous years (up to 3 years back)
- The `data_freshness` field indicates the year of the data

### Error Handling

1. **Invalid Country Code:** Validated before API call (format check)
2. **Data Not Available:** When World Bank has no data for the country/year
3. **Network Errors:** Handled internally, returns "Data not available" error
4. **Timeout Errors:** 10-second timeout, returns error if exceeded

### Performance Considerations

- Single country query: ~1-2 seconds (network dependent)
- Batch queries: Sequential processing (can be optimized with async in production)
- Caching recommended for production deployment

## Testing

### Smoke Tests

```bash
# Test endpoint validation and structure
python3 tools/smoke_test_endpoint.py

# Test new features
python3 tools/smoke_test_new_features.py

# Original smoke test
PYTHONPATH=. python3 tools/smoke_check.py
```

### Unit Tests

```bash
# Requires pytest
pytest tests/test_risk_score_endpoint.py
pytest tests/test_data_ingestion.py
pytest tests/test_portfolio_summary.py
```

## Integration with Pricing Module

The risk score endpoint integrates with the existing pricing module:

```python
from backend.src.risk_score_endpoint import get_risk_score_for_country
from backend.src.api import build_pricing_decision

# Get risk score from World Bank
risk_data = get_risk_score_for_country("BR")

# Build pricing decision based on risk
if "risk_score" in risk_data:
    pricing = build_pricing_decision("BR", risk_data["risk_score"])
    # pricing will contain tier and adjustmentPct
```

## Future Enhancements

1. **Caching Layer:** Redis cache for frequently accessed countries
2. **Async Processing:** Parallel batch requests for better performance
3. **Rate Limiting:** Implement rate limiting to comply with World Bank API limits
4. **Historical Data:** Endpoint for historical risk score trends
5. **Regional Aggregation:** Endpoint for regional risk summaries

## Compliance

- ✅ World Bank CC BY 4.0 license attribution included in all responses
- ✅ API contract matches ISSUE-003 specification
- ✅ Validation and error handling implemented
- ✅ Smoke tests and unit tests created
- ✅ Documentation complete

## PR Checklist Reference

As per `/home/node/clawd/ops/multiagent/delivery/issue-003-api-pr-checklist-2026-02-25-2200.md`:

- ✅ Branch: `feature/issue-003-worldbank-risk-score-api`
- ✅ Teste de contrato executado (smoke tests)
- ✅ Atribuição CC BY 4.0 validada na resposta
- ⏳ KPI de valor anexado (2 propostas com score) - **TODO**
- ⏳ CI verde + 1 aprovação - **TODO**

---

**Agente:** builder-repo  
**Skill:** n/a (execução direta)  
**Workflow:** build-mvp
