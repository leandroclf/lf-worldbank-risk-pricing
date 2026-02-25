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
