#!/usr/bin/env python3
"""Smoke test for new features: data ingestion and portfolio risk summary."""

import sys
import os
sys.path.insert(0, '.')

from backend.src.api import get_portfolio_risk_summary

def test_portfolio_risk_summary():
    """Test get_portfolio_risk_summary with sample data."""
    print("Testing get_portfolio_risk_summary...")
    
    # Test with empty list
    result = get_portfolio_risk_summary([])
    assert result["total_portfolios"] == 0
    assert result["avg_exposure"] == 0.0
    assert result["total_at_risk"] == 0
    print("✓ Empty portfolio test passed")
    
    # Test with sample data
    portfolio_results = [
        {"exposure": 0.2, "positions_at_risk": 2},
        {"exposure": 0.4, "positions_at_risk": 5},
        {"exposure": 0.3, "positions_at_risk": 3}
    ]
    result = get_portfolio_risk_summary(portfolio_results)
    assert result["total_portfolios"] == 3
    assert result["avg_exposure"] == 0.3
    assert result["total_at_risk"] == 10
    print("✓ Multiple portfolios test passed")
    
    print("✓ All get_portfolio_risk_summary tests passed!\n")


def test_data_ingestion():
    """Test data ingestion module structure."""
    print("Testing data_ingestion module...")
    
    # Verify the module file exists
    module_path = "backend/src/data_ingestion.py"
    assert os.path.exists(module_path), f"Module {module_path} not found"
    print("✓ Module file exists")
    
    # Read and verify basic structure
    with open(module_path, 'r') as f:
        content = f.read()
        assert 'def fetch_risk_indicator' in content
        assert 'def get_current_year_risk' in content
        assert 'WORLD_BANK_API_BASE_URL' in content
        assert 'RISK_INDICATOR_CODE' in content
    print("✓ Required functions and constants present")
    
    # Note: We don't test actual API calls to avoid network dependency and missing 'requests' lib
    print("✓ Data ingestion module structure verified!\n")
    print("⚠  Note: Actual API calls not tested (requires 'requests' library and network)")


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("SMOKE TEST: New Features")
    print("=" * 60 + "\n")
    
    try:
        test_portfolio_risk_summary()
        test_data_ingestion()
        
        print("=" * 60)
        print("✓ ALL SMOKE TESTS PASSED")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
