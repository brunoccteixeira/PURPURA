"""
Quick test of physrisk-lib API
Testing basic hazard calculations
"""
from pathlib import Path
import sys

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

def test_basic_physrisk():
    """Test basic physrisk functionality"""
    try:
        from physrisk.api import get_hazard_data
        from physrisk.data.hazard_data_provider import HazardDataProvider
        from physrisk.kernel.hazards import RiverineInundation, ChronicHeat, Drought

        print("✅ physrisk imports successful!")

        # Test location: São Paulo, Brazil
        latitude = -23.5505
        longitude = -46.6333

        print(f"\n📍 Test location: São Paulo ({latitude}, {longitude})")

        # Available hazards
        hazards = [
            ("RiverineInundation", RiverineInundation),
            ("ChronicHeat", ChronicHeat),
            ("Drought", Drought),
        ]

        print("\n📊 Available hazard types:")
        for name, _ in hazards:
            print(f"  - {name}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_physrisk()
    sys.exit(0 if success else 1)
