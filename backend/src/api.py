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
