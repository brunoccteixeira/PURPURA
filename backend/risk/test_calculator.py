#!/usr/bin/env python3
"""
Test script for PÚRPURA Risk Calculator
Tests Brazilian climate risk calculations with mock data
"""
import sys
from pathlib import Path

# Add backend to path
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from risk.calculator import (
    RiskCalculator,
    RiskScenario,
    calculate_municipal_risk,
    calculate_location_risk
)


def test_location_risk():
    """Test risk calculation for specific coordinates"""
    print("=" * 70)
    print("TEST 1: Location Risk Calculation (São Paulo)")
    print("=" * 70)

    # São Paulo coordinates
    lat, lng = -23.5505, -46.6333

    print(f"\nLocation: São Paulo, SP")
    print(f"Coordinates: ({lat}, {lng})")
    print(f"Scenario: SSP2-4.5 (moderate emissions)\n")

    risk = calculate_location_risk(lat, lng, RiskScenario.SSP245)

    print(f"Overall Risk Score: {risk.overall_risk_score:.2%}")
    print(f"\nHazard Breakdown:")
    print("-" * 70)

    for hazard in risk.hazards:
        print(f"\n{hazard.hazard_type.value.upper()}:")
        print(f"  Current risk:     {hazard.current_risk:.2%}")
        print(f"  Projected 2030:   {hazard.projected_2030:.2%}")
        print(f"  Projected 2050:   {hazard.projected_2050:.2%}")
        print(f"  Confidence:       {hazard.confidence:.2%}")
        print(f"  Data source:      {hazard.data_source}")
        if hazard.raw_value:
            print(f"  Raw value:        {hazard.raw_value} {hazard.unit}")

    print("\n✓ Location risk calculation successful")
    return True


def test_municipal_risk():
    """Test risk calculation for Brazilian municipalities"""
    print("\n" + "=" * 70)
    print("TEST 2: Municipal Risk Calculations")
    print("=" * 70)

    municipalities = [
        ("3550308", "São Paulo"),
        ("3304557", "Rio de Janeiro"),
        ("2927408", "Salvador"),
        ("5300108", "Brasília"),
        ("4106902", "Curitiba"),
    ]

    print(f"\nCalculating risks for {len(municipalities)} municipalities...")
    print(f"Scenario: SSP5-8.5 (high emissions)")
    print()

    results = []

    for ibge_code, expected_name in municipalities:
        risk = calculate_municipal_risk(ibge_code, RiskScenario.SSP585)
        results.append((ibge_code, expected_name, risk))

        print(f"{expected_name:20} (IBGE {ibge_code}): {risk.overall_risk_score:.2%}")

    print("\n✓ Municipal risk calculations successful")

    # Show highest risk municipality
    print("\nHighest Risk Municipality:")
    print("-" * 70)

    highest_risk = max(results, key=lambda x: x[2].overall_risk_score)
    ibge, name, risk = highest_risk

    print(f"\n{name} (IBGE {ibge})")
    print(f"Overall Risk: {risk.overall_risk_score:.2%}")
    print("\nTop hazards:")

    sorted_hazards = sorted(risk.hazards, key=lambda h: h.projected_2050, reverse=True)
    for i, hazard in enumerate(sorted_hazards[:3], 1):
        print(f"  {i}. {hazard.hazard_type.value}: {hazard.projected_2050:.2%} by 2050")

    return True


def test_scenario_comparison():
    """Test different climate scenarios"""
    print("\n" + "=" * 70)
    print("TEST 3: Climate Scenario Comparison")
    print("=" * 70)

    ibge_code = "3550308"  # São Paulo
    scenarios = [
        (RiskScenario.SSP126, "Low emissions (SSP1-2.6)"),
        (RiskScenario.SSP245, "Moderate emissions (SSP2-4.5)"),
        (RiskScenario.SSP585, "High emissions (SSP5-8.5)"),
    ]

    print(f"\nComparing scenarios for São Paulo (IBGE {ibge_code}):\n")

    for scenario, description in scenarios:
        risk = calculate_municipal_risk(ibge_code, scenario)
        print(f"{description:35} → Overall Risk: {risk.overall_risk_score:.2%}")

    print("\n✓ Scenario comparison successful")
    print("\nNote: These are mock values. Real values will come from Cemaden/INPE.")
    return True


def test_brazilian_data_adapter():
    """Test Brazilian climate data adapter"""
    print("\n" + "=" * 70)
    print("TEST 4: Brazilian Climate Data Adapter")
    print("=" * 70)

    from risk.calculator import BrazilianClimateData

    adapter = BrazilianClimateData()

    print(f"\nAdapter status: {'mock mode' if adapter.mock_mode else 'live mode'}")
    print("\nTesting individual hazard queries...")

    # Test coordinates (Rio de Janeiro)
    lat, lng = -22.9068, -43.1729

    # Test flood risk
    flood = adapter.get_flood_risk(lat, lng, RiskScenario.SSP245, 2050)
    print(f"\n✓ Flood risk query:    {flood.projected_2050:.2%} (source: {flood.data_source})")

    # Test drought risk
    drought = adapter.get_drought_risk(lat, lng, RiskScenario.SSP245, 2050)
    print(f"✓ Drought risk query:  {drought.projected_2050:.2%} (source: {drought.data_source})")

    # Test heat stress
    heat = adapter.get_heat_stress_risk(lat, lng, RiskScenario.SSP245, 2050)
    print(f"✓ Heat stress query:   {heat.projected_2050:.2%} (source: {heat.data_source})")

    print("\n✓ All hazard adapters working")

    print("\n📝 Next steps for real implementation:")
    print("  1. Integrate Cemaden API (flood/precipitation data)")
    print("  2. Integrate INPE climate projections (temperature, drought)")
    print("  3. Integrate ANA hydrological data (water stress)")
    print("  4. Add historical event validation")

    return True


def main():
    """Run all risk calculator tests"""
    print("\n🟣 PÚRPURA Risk Calculator Test Suite\n")

    tests = [
        ("Location Risk", test_location_risk),
        ("Municipal Risk", test_municipal_risk),
        ("Scenario Comparison", test_scenario_comparison),
        ("Brazilian Data Adapter", test_brazilian_data_adapter),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n✅ All tests passed!")
        print("\n🎯 Next implementation steps:")
        print("  1. Create H3 geospatial indexing service")
        print("  2. Implement API endpoints in FastAPI")
        print("  3. Integrate real Cemaden/INPE/ANA APIs")
        print("  4. Add PostgreSQL persistence layer")
        print("  5. Build frontend risk dashboard")
    else:
        print("\n⚠️  Some tests failed - see details above")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
