"""
Risk Score API Endpoint Implementation for ISSUE-003.

Provides a simple endpoint interface that integrates with World Bank data ingestion
to return risk scores with proper attribution.
"""

from datetime import datetime, timezone
from backend.src.api import build_risk_score_response, is_valid_country_code

# Try to import data_ingestion, but handle case where 'requests' is not available
try:
    from backend.src.data_ingestion import get_current_year_risk
    DATA_INGESTION_AVAILABLE = True
except ImportError:
    DATA_INGESTION_AVAILABLE = False
    def get_current_year_risk(country_code):
        """Fallback stub when data_ingestion is not available."""
        return None


def get_risk_score_for_country(country_code: str) -> dict:
    """
    Get risk score for a country from World Bank data.
    
    This function implements the contract for:
    GET /v1/risk-score?country_code=BR
    
    Args:
        country_code (str): 2-letter ISO country code (e.g., 'BR', 'US')
        
    Returns:
        dict: Response with risk score data or error information
        
    Example response:
        {
            "country_code": "BR",
            "risk_score": 5.23,
            "data_freshness": "2023",
            "source_attribution": "World Bank (CC BY 4.0)",
            "timestamp": "2026-02-27T22:00:00Z"
        }
    """
    # Validate country code
    if not is_valid_country_code(country_code):
        return {
            "error": "Invalid country code",
            "message": "Country code must be a 2-letter ISO code",
            "country_code": country_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Fetch risk data from World Bank
    risk_value = get_current_year_risk(country_code.upper())
    
    # Handle case where no data is available
    if risk_value is None:
        return {
            "error": "Data not available",
            "message": f"No risk data available for country: {country_code.upper()}",
            "country_code": country_code.upper(),
            "source_attribution": "World Bank (CC BY 4.0)",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Calculate approximate data freshness (year)
    current_year = datetime.now().year
    # Most recent data is typically 1-2 years old
    estimated_data_year = current_year - 1
    
    # Build successful response
    return {
        "country_code": country_code.upper(),
        "risk_score": round(risk_value, 2),
        "data_freshness": str(estimated_data_year),
        "source_attribution": "World Bank (CC BY 4.0)",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def batch_get_risk_scores(country_codes: list) -> dict:
    """
    Get risk scores for multiple countries in a single call.
    
    Args:
        country_codes (list): List of 2-letter ISO country codes
        
    Returns:
        dict: Batch response with results for each country
        
    Example:
        {
            "results": [
                {"country_code": "BR", "risk_score": 5.23, ...},
                {"country_code": "US", "risk_score": 2.1, ...}
            ],
            "total": 2,
            "successful": 2,
            "failed": 0
        }
    """
    results = []
    successful = 0
    failed = 0
    
    for code in country_codes:
        result = get_risk_score_for_country(code)
        results.append(result)
        
        if "error" in result:
            failed += 1
        else:
            successful += 1
    
    return {
        "results": results,
        "total": len(country_codes),
        "successful": successful,
        "failed": failed,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    # Example usage and manual testing
    print("=" * 60)
    print("Risk Score Endpoint - Manual Test")
    print("=" * 60)
    
    # Test single country
    print("\n1. Testing Brazil (BR):")
    result_br = get_risk_score_for_country("BR")
    print(f"   {result_br}")
    
    print("\n2. Testing United States (US):")
    result_us = get_risk_score_for_country("US")
    print(f"   {result_us}")
    
    print("\n3. Testing invalid country code (XX):")
    result_invalid = get_risk_score_for_country("XX")
    print(f"   {result_invalid}")
    
    print("\n4. Testing batch request:")
    batch_result = batch_get_risk_scores(["BR", "US", "DE", "CN"])
    print(f"   Total: {batch_result['total']}")
    print(f"   Successful: {batch_result['successful']}")
    print(f"   Failed: {batch_result['failed']}")
    
    print("\n" + "=" * 60)
