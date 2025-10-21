#!/usr/bin/env python3
"""
Test script for physrisk-lib integration
Explores physrisk capabilities and creates example calculations
"""
import sys
from pathlib import Path

# Add backend to path
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))


def test_physrisk_basics():
    """Test basic physrisk functionality"""
    print("=" * 70)
    print("TEST 1: physrisk-lib Basic Exploration")
    print("=" * 70)

    try:
        from physrisk import api
        from physrisk.kernel.hazards import RiverineInundation, Drought, ChronicHeat
        from physrisk.data.pregenerated_hazard_model import ZarrHazardModel
        from physrisk.requests import AssetExposureRequest, AssetImpactRequest

        print("✓ physrisk imports successful")
        print(f"\nAvailable hazard types:")
        print(f"  - RiverineInundation")
        print(f"  - Drought")
        print(f"  - ChronicHeat")
        print(f"  - And more...")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_hazard_model():
    """Test hazard model initialization"""
    print("\n" + "=" * 70)
    print("TEST 2: Hazard Model Initialization")
    print("=" * 70)

    try:
        from physrisk.hazard_models.hazard_model_factory import HazardModelFactory

        # Initialize hazard model factory (uses OS-Climate public data)
        print("Initializing HazardModelFactory...")
        print("(This may take a moment on first run - downloading hazard data)")

        factory = HazardModelFactory()
        model = factory.hazard_model()

        print("✓ Hazard model initialized successfully")
        print(f"  Model type: {type(model).__name__}")

        return model

    except Exception as e:
        print(f"❌ Error initializing model: {e}")
        print("Note: physrisk requires internet connection for hazard data")
        import traceback
        traceback.print_exc()
        return None


def test_location_risk():
    """Test risk calculation for a specific location"""
    print("\n" + "=" * 70)
    print("TEST 3: Risk Calculation for Brazilian Location")
    print("=" * 70)

    try:
        from physrisk.kernel.hazards import RiverineInundation, ChronicHeat
        from physrisk.hazard_models.hazard_model_factory import HazardModelFactory
        from physrisk.data.hazard_data_provider import HazardDataRequest

        # São Paulo coordinates (example)
        latitude = -23.5505  # São Paulo, SP
        longitude = -46.6333

        print(f"\nCalculating climate hazards for:")
        print(f"  Location: São Paulo, SP")
        print(f"  Coordinates: ({latitude}, {longitude})")

        # Initialize model
        factory = HazardModelFactory()
        model = factory.hazard_model()

        # Note: physrisk uses specific scenarios and years
        scenario = "ssp585"  # High emissions scenario (replaces old rcp8.5)
        year = 2050

        print(f"\n  Scenario: {scenario}")
        print(f"  Year: {year}")

        # Create hazard data request for chronic heat
        print("\nQuerying chronic heat hazard...")
        hazard_type = ChronicHeat()

        request = HazardDataRequest(
            hazard_type=type(hazard_type),
            longitude=longitude,
            latitude=latitude,
            scenario=scenario,
            year=year,
            indicator_id="mean_degree_days/above/32c"
        )

        # Get hazard data
        response = model.get_hazard_data([request])

        if response and len(response) > 0:
            heat_data = response[0]
            print(f"✓ Heat hazard data retrieved:")
            print(f"  Indicator: {request.indicator_id}")
            print(f"  Response type: {type(heat_data).__name__}")

            # Try to extract value
            if hasattr(heat_data, 'intensity'):
                print(f"  Intensity: {heat_data.intensity}")
        else:
            print("⚠️  No hazard data returned (may be unavailable for this location)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nNote: This location may not be covered by default hazard datasets")
        print("We'll need to integrate Brazilian-specific data sources (Cemaden, INPE)")
        import traceback
        traceback.print_exc()
        return False


def test_h3_integration():
    """Test H3 geospatial indexing"""
    print("\n" + "=" * 70)
    print("TEST 4: H3 Geospatial Indexing")
    print("=" * 70)

    try:
        import h3

        # São Paulo coordinates
        lat = -23.5505
        lng = -46.6333

        # Create H3 index at different resolutions
        print(f"\nH3 indices for São Paulo ({lat}, {lng}):")

        for resolution in [5, 7, 9]:
            h3_index = h3.latlng_to_cell(lat, lng, resolution)
            print(f"  Resolution {resolution}: {h3_index}")

            # Get cell area
            area_km2 = h3.cell_area(h3_index, unit='km^2')
            print(f"    Cell area: {area_km2:.2f} km²")

        print("\n✓ H3 indexing working correctly")

        # Create hexagon ring around center
        center = h3.latlng_to_cell(lat, lng, 7)
        ring = h3.grid_disk(center, 1)
        print(f"\nHexagonal ring (k=1): {len(ring)} cells")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all physrisk tests"""
    print("\n🟣 PÚRPURA × physrisk-lib Integration Tests\n")

    results = []

    # Test 1: Basic imports
    results.append(("Basic imports", test_physrisk_basics()))

    # Test 2: Hazard model
    model = test_hazard_model()
    results.append(("Hazard model", model is not None))

    # Test 3: Location risk (may fail without internet)
    results.append(("Location risk", test_location_risk()))

    # Test 4: H3 integration
    results.append(("H3 indexing", test_h3_integration()))

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
        print("\nNext steps:")
        print("1. Create Brazilian hazard data adapter (Cemaden API)")
        print("2. Implement municipal risk calculator")
        print("3. Build H3 grid risk mapping service")
        print("4. Integrate with FastAPI endpoints")
    else:
        print("\n⚠️  Some tests failed - see details above")
        print("Note: Internet connection required for hazard data download")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
