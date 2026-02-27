from datetime import datetime, timezone

def get_sample_payload():
    return {
        "component": "lf-worldbank-risk-pricing",
        "source": "worldbank",
        "status": "ok",
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }


def get_pricing_signal():
    return {"issue": "ISSUE-003", "proposalTarget": 2, "regionalScoreEnabled": True}



def build_risk_score_response(country_code, risk_score):
    return {
        "issue": "ISSUE-003",
        "countryCode": country_code.upper(),
        "riskScore": float(risk_score),
        "sourceAttribution": "World Bank (CC BY 4.0)",
    }



def is_valid_country_code(code):
    c=str(code).strip()
    return len(c)==2 and c.isalpha()



def build_pricing_adjustment(risk_score):
    s=float(risk_score)
    if s >= 75: return {"tier":"high","adjustmentPct": 8}
    if s >= 50: return {"tier":"medium","adjustmentPct": 3}
    return {"tier":"low","adjustmentPct": 0}



def compute_pricing_multiplier(risk_score):
    adj = build_pricing_adjustment(risk_score)["adjustmentPct"]
    return round(1 + (adj / 100), 4)



def build_pricing_decision(country_code, risk_score):
    resp = build_risk_score_response(country_code, risk_score)
    adj = build_pricing_adjustment(risk_score)
    resp.update({"tier": adj["tier"], "adjustmentPct": adj["adjustmentPct"]})
    return resp


def score_pricing_portfolio(entries):
    """Aggregate pricing decisions for a country/risk portfolio."""
    if not entries:
        return {"total": 0, "highRiskCount": 0, "avgMultiplier": 1.0}

    decisions = [build_pricing_decision(e["countryCode"], e["riskScore"]) for e in entries]
    multipliers = [compute_pricing_multiplier(e["riskScore"]) for e in entries]
    high_risk = sum(1 for d in decisions if d["tier"] == "high")

    return {
        "total": len(entries),
        "highRiskCount": high_risk,
        "avgMultiplier": round(sum(multipliers) / len(multipliers), 4),
    }


def summarize_country_risk_bands(entries):
    """Return counts by risk tier for proposal-level reporting."""
    bands = {"high": 0, "medium": 0, "low": 0}
    for e in entries or []:
        tier = build_pricing_adjustment(e.get("riskScore", 0))["tier"]
        bands[tier] += 1
    return bands


def estimate_portfolio_adjustment_pct(entries):
    """Average adjustment percentage across a portfolio."""
    if not entries:
        return 0.0
    adjs = [build_pricing_adjustment(e.get("riskScore", 0))["adjustmentPct"] for e in entries]
    return round(sum(adjs) / len(adjs), 2)


def summarize_pricing_tiers_with_multiplier(entries):
    """Combine tier counts with portfolio average multiplier."""
    bands = summarize_country_risk_bands(entries)
    return {
        "bands": bands,
        "avgMultiplier": score_pricing_portfolio(entries)["avgMultiplier"] if entries else 1.0,
    }


def count_high_risk_countries(entries, threshold=75):
    """Count countries with risk score above high-risk threshold."""
    total = len(entries or [])
    high = sum(1 for e in (entries or []) if float(e.get("riskScore", 0)) >= float(threshold))
    return {"threshold": float(threshold), "total": total, "highRisk": high}


def estimate_high_risk_rate(entries, threshold=75):
    """Return share of countries in high-risk category."""
    if not entries:
        return 0.0
    cnt = count_high_risk_countries(entries, threshold)
    return round(cnt["highRisk"] / cnt["total"], 4)


def calculate_multiplier_delta(entries, baseline_multiplier):
    """Return percentage-point improvement vs baseline average multiplier."""
    if baseline_multiplier <= 0:
        return 0.0
    current = score_pricing_portfolio(entries)["avgMultiplier"] if entries else 1.0
    return round((current - baseline_multiplier) / baseline_multiplier * 100, 2)


def aggregate_regional_risk(countries, region_mapping=None):
    """
    Aggregate country risk scores by region for portfolio analysis.
    Returns regional risk summary with weighted averages.
    """
    if not countries:
        return {"regions": {}, "stats": {"total_countries": 0, "regions_count": 0}}
    
    default_regions = {
        "LATAM": ["BR", "MX", "AR", "CL", "CO"],
        "EMEA": ["DE", "FR", "GB", "IT", "ES", "ZA", "NG"],
        "APAC": ["CN", "JP", "IN", "AU", "KR", "SG"],
        "NA": ["US", "CA"]
    }
    mapping = region_mapping or default_regions
    
    # Invert mapping for lookup
    country_to_region = {}
    for region, codes in mapping.items():
        for code in codes:
            country_to_region[code] = region
    
    region_data = {}
    for country in countries:
        code = country.get("country_code", "")
        risk = country.get("risk_score", 0)
        region = country_to_region.get(code, "OTHER")
        
        if region not in region_data:
            region_data[region] = {"scores": [], "count": 0}
        region_data[region]["scores"].append(risk)
        region_data[region]["count"] += 1
    
    regions_summary = {}
    for region, data in region_data.items():
        scores = data["scores"]
        regions_summary[region] = {
            "avg_risk": round(sum(scores) / len(scores), 3) if scores else 0,
            "max_risk": max(scores) if scores else 0,
            "min_risk": min(scores) if scores else 0,
            "country_count": data["count"]
        }
    
    return {
        "regions": regions_summary,
        "stats": {
            "total_countries": len(countries),
            "regions_count": len(regions_summary)
        }
    }


def calculate_portfolio_exposure(positions, risk_data):
    """
    Calculate weighted portfolio exposure to country risk.
    Returns exposure metrics and risk-adjusted values.
    """
    if not positions or not risk_data:
        return {"exposure": 0.0, "risk_adjusted_value": 0.0, "positions_at_risk": 0}
    
    risk_lookup = {r.get("country_code"): r.get("risk_score", 0) for r in risk_data}
    
    total_value = 0
    weighted_risk = 0
    positions_at_risk = 0
    
    for pos in positions:
        value = pos.get("value", 0)
        country = pos.get("country_code", "")
        risk = risk_lookup.get(country, 0)
        
        total_value += value
        weighted_risk += value * risk
        if risk > 0.5:
            positions_at_risk += 1
    
    exposure = weighted_risk / total_value if total_value > 0 else 0
    risk_adjusted = total_value * (1 - exposure)
    
    return {
        "exposure": round(exposure, 4),
        "risk_adjusted_value": round(risk_adjusted, 2),
        "positions_at_risk": positions_at_risk,
        "total_positions": len(positions)
    }


def get_portfolio_risk_summary(portfolio_results):
    """
    Summarize multiple portfolio risk analyses for reporting.
    """
    if not portfolio_results:
        return {"total_portfolios": 0, "avg_exposure": 0.0, "total_at_risk": 0}
    
    total_exposure = sum(p.get("exposure", 0) for p in portfolio_results)
    total_at_risk = sum(p.get("positions_at_risk", 0) for p in portfolio_results)
    
    return {
        "total_portfolios": len(portfolio_results),
        "avg_exposure": round(total_exposure / len(portfolio_results), 4),
        "total_at_risk": total_at_risk
    }
