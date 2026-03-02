import requests
from datetime import datetime

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
    url = (
        f"{WORLD_BANK_API_BASE_URL}/{country_code}/indicator/{RISK_INDICATOR_CODE}?"
        f"date={year}&format=json"
    )
    
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
                return float(value)
        
        return None # Data not found for the given country and year
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} for {url}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err} for {url}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err} for {url}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err} for {url}")
    except (TypeError, IndexError, KeyError) as json_err:
        print(f"Error parsing JSON response: {json_err} from {url}")
        print(f"Response content: {response.text}")
    
    return None

def get_current_year_risk(country_code: str) -> float | None:
    """
    Fetches the risk indicator for the current or most recent available year.
    """
    current_year = datetime.now().year
    
    # Try current year, then previous years if data not available
    for year_offset in range(3): # Try current year, previous year, and year before that
        target_year = current_year - year_offset
        risk_value = fetch_risk_indicator(country_code, target_year)
        if risk_value is not None:
            return risk_value
            
    return None

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
        risk_value = get_current_year_risk(code)
        if risk_value is not None:
            results.append({"country_code": code, "risk_score": risk_value})
        else:
            print(f"Warning: Could not retrieve risk premium for {code}.")
    return results

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
