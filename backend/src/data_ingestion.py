from datetime import datetime
from time import perf_counter

import requests

from backend.src.worldbank_governance import (
    evaluate_worldbank_quality_contract,
    get_last_worldbank_resolution,
    get_worldbank_metrics_snapshot,
    get_worldbank_quality_contract,
    record_fetch_attempt,
    remember_worldbank_resolution,
    reset_worldbank_metrics,
)

WORLD_BANK_API_BASE_URL = "https://api.worldbank.org/v2/country"
RISK_INDICATOR_CODE = "FR.INR.RISK" # Risk premium on lending (lending rate minus treasury bill rate, %)

def fetch_risk_indicator(country_code: str, year: int) -> float | None:
    """
    Fetches the 'Risk premium on lending' indicator for a given country and year
    from the World Bank API.

    Args:
        country_code (str): The 2-letter ISO country code (e.g., 'BR', 'US').
        year (int): The year for which to fetch the data.

    Returns:
        float | None: The risk premium value if available, otherwise None.
    """
    normalized_country_code = str(country_code).strip().upper()
    url = (
        f"{WORLD_BANK_API_BASE_URL}/{normalized_country_code}/indicator/{RISK_INDICATOR_CODE}?"
        f"date={year}&format=json"
    )

    response = None
    outcome = "empty"
    error_type = None
    started_at = perf_counter()

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # The World Bank API returns a list of two elements:
        # 1. Pagination information
        # 2. The actual data (list of dictionaries)
        if data and len(data) > 1 and data[1]:
            # Data for the requested indicator and year should be in the first item of the second list
            indicator_data = data[1][0]
            value = indicator_data.get("value")
            if value is not None:
                outcome = "success"
                return float(value)

        return None # Data not found for the given country and year

    except requests.exceptions.Timeout as timeout_err:
        outcome = "timeout"
        error_type = "timeout"
        print(f"Timeout error occurred: {timeout_err} for {url}")
    except requests.exceptions.HTTPError as http_err:
        outcome = "error"
        error_type = "http_error"
        print(f"HTTP error occurred: {http_err} for {url}")
    except requests.exceptions.ConnectionError as conn_err:
        outcome = "error"
        error_type = "connection_error"
        print(f"Connection error occurred: {conn_err} for {url}")
    except requests.exceptions.RequestException as req_err:
        outcome = "error"
        error_type = "request_error"
        print(f"An unexpected error occurred: {req_err} for {url}")
    except (TypeError, ValueError, IndexError, KeyError) as json_err:
        outcome = "error"
        error_type = "json_error"
        print(f"Error parsing JSON response: {json_err} from {url}")
        if response is not None:
            print(f"Response content: {response.text}")
    except Exception as unexpected_err:
        outcome = "error"
        error_type = "unexpected_error"
        # Keep fetch resilient against unexpected request library wrappers/mocks.
        print(f"Unexpected error occurred: {unexpected_err} for {url}")

    finally:
        record_fetch_attempt(
            normalized_country_code,
            year,
            perf_counter() - started_at,
            outcome,
            error_type,
        )

    return None

def get_current_year_risk(country_code: str) -> float | None:
    """
    Fetches the risk indicator for the current or most recent available year.
    """
    normalized_country_code = str(country_code).strip().upper()
    current_year = datetime.now().year
    attempts = 0
    resolved_year = None
    risk_value = None

    # Try current year, then previous years if data not available
    for year_offset in range(3): # Try current year, previous year, and year before that
        attempts += 1
        target_year = current_year - year_offset
        risk_value = fetch_risk_indicator(normalized_country_code, target_year)
        if risk_value is not None:
            resolved_year = target_year
            break

    remember_worldbank_resolution(
        country_code=normalized_country_code,
        requested_year=current_year,
        resolved_year=resolved_year,
        attempts=attempts,
        success=risk_value is not None,
        risk_value=risk_value,
    )
    return risk_value

def fetch_multiple_country_risk_data(country_codes: list[str]) -> list[dict]:
    """
    Fetches the most recent risk indicator for a list of country codes.

    Args:
        country_codes (list[str]): A list of 2-letter ISO country codes.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains
                    "country_code" and "risk_score" for each successfully
                    fetched country.
    """
    results = []
    for code in country_codes:
        normalized_code = str(code).strip().upper()
        risk_value = get_current_year_risk(normalized_code)
        if risk_value is not None:
            results.append({"country_code": normalized_code, "risk_score": risk_value})
        else:
            print(f"Warning: Could not retrieve risk premium for {normalized_code}.")
    return results


__all__ = [
    "WORLD_BANK_API_BASE_URL",
    "RISK_INDICATOR_CODE",
    "fetch_risk_indicator",
    "get_current_year_risk",
    "fetch_multiple_country_risk_data",
    "get_last_worldbank_resolution",
    "get_worldbank_metrics_snapshot",
    "get_worldbank_quality_contract",
    "evaluate_worldbank_quality_contract",
    "record_fetch_attempt",
    "remember_worldbank_resolution",
    "reset_worldbank_metrics",
]

if __name__ == "__main__":
    # Example Usage:
    print("Fetching risk indicator for Brazil (BR) for 2023:")
    risk_br = fetch_risk_indicator("BR", 2023)
    if risk_br is not None:
        print(f"Brazil risk premium (2023): {risk_br}")
    else:
        print("Could not retrieve risk premium for Brazil for 2023.")

    print("\nFetching risk indicator for United States (US) for 2023:")
    risk_us = fetch_risk_indicator("US", 2023)
    if risk_us is not None:
        print(f"United States risk premium (2023): {risk_us}")
    else:
        print("Could not retrieve risk premium for United States for 2023.")
    
    print("\nFetching current year risk for Germany (DE):")
    risk_de = get_current_year_risk("DE")
    if risk_de is not None:
        print(f"Germany risk premium (most recent): {risk_de}")
    else:
        print("Could not retrieve most recent risk premium for Germany.")

    print("\nFetching risk indicator for a non-existent country (XX) for 2023:")
    risk_xx = fetch_risk_indicator("XX", 2023)
    if risk_xx is not None:
        print(f"XX risk premium (2023): {risk_xx}")
    else:
        print("Could not retrieve risk premium for XX for 2023.")

    print("\nFetching multiple country risk data for BR, US, DE, FR:")
    countries_to_fetch = ["BR", "US", "DE", "FR", "XX"]
    multi_country_risk = fetch_multiple_country_risk_data(countries_to_fetch)
    print(f"Multi-country risk data: {multi_country_risk}")
