#!/usr/bin/env python3
"""
Test script for H3 Geospatial Risk Mapping
Tests hexagonal grid creation and risk visualization
"""
import sys
import json
from pathlib import Path

# Add backend to path
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from risk.h3_service import (
    H3RiskMapper,
    RiskScenario,
    HazardType,
    create_municipal_risk_grid,
    get_geojson_for_municipality
)


def test_h3_basics():
    """Test basic H3 operations"""
    print("=" * 70)
    print("TEST 1: H3 Basic Operations")
    print("=" * 70)

    mapper = H3RiskMapper(resolution=7)

    # Test lat/lng to H3
    lat, lng = -23.5505, -46.6333  # São Paulo
    h3_idx = mapper.latlng_to_h3(lat, lng)

    print(f"\nSão Paulo coordinates: ({lat}, {lng})")
    print(f"H3 index (res 7):      {h3_idx}")

    # Test H3 to lat/lng
    center_lat, center_lng = mapper.h3_to_latlng(h3_idx)
    print(f"Cell center:           ({center_lat:.4f}, {center_lng:.4f})")

    # Test cell area
    area = mapper.get_cell_area(h3_idx)
    print(f"Cell area:             {area:.2f} km²")

    print("\n✓ H3 basic operations working")
    return True


def test_single_cell_risk():
    """Test risk calculation for a single H3 cell"""
    print("\n" + "=" * 70)
    print("TEST 2: Single H3 Cell Risk Calculation")
    print("=" * 70)

    mapper = H3RiskMapper(resolution=7, scenario=RiskScenario.SSP245)

    # São Paulo
    lat, lng = -23.5505, -46.6333
    h3_idx = mapper.latlng_to_h3(lat, lng)

    print(f"\nCalculating risk for H3 cell: {h3_idx}")

    cell = mapper.calculate_cell_risk(h3_idx)

    print(f"\nCell Data:")
    print(f"  Center:        ({cell.center_lat:.4f}, {cell.center_lng:.4f})")
    print(f"  Area:          {cell.area_km2:.2f} km²")
    print(f"  Overall Risk:  {cell.risk_score:.2%}")
    print(f"\n  Hazard Breakdown:")

    for hazard, risk in cell.hazard_breakdown.items():
        print(f"    {hazard:15} → {risk:.2%}")

    print("\n✓ Single cell risk calculation successful")
    return True


def test_risk_grid():
    """Test hexagonal risk grid creation"""
    print("\n" + "=" * 70)
    print("TEST 3: Hexagonal Risk Grid Creation")
    print("=" * 70)

    mapper = H3RiskMapper(resolution=8, scenario=RiskScenario.SSP585)

    # Create small grid around São Paulo center
    lat, lng = -23.5505, -46.6333
    rings = 2

    print(f"\nCreating hexagonal grid:")
    print(f"  Center:     ({lat}, {lng})")
    print(f"  Rings:      {rings}")
    print(f"  Resolution: 8 (~0.74 km² per cell)")

    cells = mapper.create_risk_grid(lat, lng, rings)

    print(f"\n✓ Grid created with {len(cells)} cells")

    # Calculate statistics
    risk_scores = [cell.risk_score for cell in cells]
    avg_risk = sum(risk_scores) / len(risk_scores)
    max_risk = max(risk_scores)
    min_risk = min(risk_scores)

    print(f"\n  Risk Statistics:")
    print(f"    Average:  {avg_risk:.2%}")
    print(f"    Maximum:  {max_risk:.2%}")
    print(f"    Minimum:  {min_risk:.2%}")

    # Show highest risk cell
    highest_risk_cell = max(cells, key=lambda c: c.risk_score)
    print(f"\n  Highest Risk Cell:")
    print(f"    H3 Index: {highest_risk_cell.h3_index}")
    print(f"    Location: ({highest_risk_cell.center_lat:.4f}, {highest_risk_cell.center_lng:.4f})")
    print(f"    Risk:     {highest_risk_cell.risk_score:.2%}")

    print("\n✓ Risk grid creation successful")
    return True


def test_municipal_grid():
    """Test municipality risk grid"""
    print("\n" + "=" * 70)
    print("TEST 4: Municipal Risk Grid")
    print("=" * 70)

    municipalities = [
        ("3550308", "São Paulo"),
        ("3304557", "Rio de Janeiro"),
        ("2927408", "Salvador"),
    ]

    print(f"\nCreating risk grids for {len(municipalities)} municipalities...")
    print(f"Resolution: 7 (~5.2 km² per cell)")
    print(f"Rings: 2\n")

    for ibge_code, name in municipalities:
        cells = create_municipal_risk_grid(ibge_code, resolution=7, rings=2)

        avg_risk = sum(c.risk_score for c in cells) / len(cells)

        print(f"{name:20} → {len(cells):3} cells, avg risk: {avg_risk:.2%}")

    print("\n✓ Municipal grids created successfully")
    return True


def test_geojson_export():
    """Test GeoJSON export for mapping"""
    print("\n" + "=" * 70)
    print("TEST 5: GeoJSON Export for Web Mapping")
    print("=" * 70)

    ibge_code = "3550308"  # São Paulo
    print(f"\nExporting risk grid as GeoJSON for IBGE {ibge_code}...")

    geojson = get_geojson_for_municipality(ibge_code, resolution=7, rings=1)

    print(f"\nGeoJSON Structure:")
    print(f"  Type:          {geojson['type']}")
    print(f"  Features:      {len(geojson['features'])}")
    print(f"  IBGE Code:     {geojson['properties']['ibge_code']}")
    print(f"  Resolution:    {geojson['properties']['resolution']}")

    # Show sample feature
    if geojson['features']:
        sample = geojson['features'][0]
        print(f"\n  Sample Feature:")
        print(f"    Geometry type: {sample['geometry']['type']}")
        print(f"    Coordinates:   {len(sample['geometry']['coordinates'][0])} points")
        print(f"    Properties:    {list(sample['properties'].keys())}")
        print(f"    Risk score:    {sample['properties']['risk_score']:.2%}")

    # Save to file for inspection
    output_file = Path("/tmp/purpura_risk_grid.geojson")
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"\n✓ GeoJSON exported to {output_file}")
    print("\nThis file can be used with:")
    print("  - Leaflet.js (frontend)")
    print("  - Mapbox GL JS")
    print("  - QGIS (desktop GIS)")
    print("  - deck.gl (3D visualization)")

    return True


def test_heatmap_data():
    """Test heatmap data generation"""
    print("\n" + "=" * 70)
    print("TEST 6: Risk Heatmap Data")
    print("=" * 70)

    mapper = H3RiskMapper(resolution=7)

    # Create grid
    cells = mapper.create_risk_grid(-23.5505, -46.6333, rings=1)

    print(f"\nGenerating heatmap data from {len(cells)} cells...")

    # Overall risk heatmap
    overall_heatmap = mapper.get_risk_heatmap_data(cells)
    print(f"\n  Overall risk heatmap: {len(overall_heatmap)} cells")

    # Flood risk heatmap
    flood_heatmap = mapper.get_risk_heatmap_data(cells, HazardType.FLOOD)
    print(f"  Flood risk heatmap:   {len(flood_heatmap)} cells")

    # Sample data
    print(f"\n  Sample heatmap values:")
    for i, (h3_idx, risk) in enumerate(list(overall_heatmap.items())[:3]):
        print(f"    {h3_idx}: {risk:.2%}")

    print("\n✓ Heatmap data generation successful")
    print("\nHeatmap format (h3_index → risk_score) is optimized for:")
    print("  - Frontend visualization libraries")
    print("  - Rapid lookups")
    print("  - Memory efficiency")

    return True


def main():
    """Run all H3 service tests"""
    print("\n🟣 PÚRPURA H3 Geospatial Risk Mapping Tests\n")

    tests = [
        ("H3 Basics", test_h3_basics),
        ("Single Cell Risk", test_single_cell_risk),
        ("Risk Grid", test_risk_grid),
        ("Municipal Grid", test_municipal_grid),
        ("GeoJSON Export", test_geojson_export),
        ("Heatmap Data", test_heatmap_data),
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
        print("\n✅ All H3 tests passed!")
        print("\n🎯 H3 Service Ready For:")
        print("  ✓ Municipal risk grids")
        print("  ✓ GeoJSON export for web maps")
        print("  ✓ Heatmap visualization")
        print("  ✓ Multi-resolution analysis")
        print("\n📍 Next steps:")
        print("  1. Integrate with FastAPI endpoints")
        print("  2. Add caching for computed grids")
        print("  3. Build frontend map visualization")
        print("  4. Add real IBGE municipality boundaries")
    else:
        print("\n⚠️  Some tests failed - see details above")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
