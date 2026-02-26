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
