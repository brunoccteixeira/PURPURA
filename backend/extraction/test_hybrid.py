#!/usr/bin/env python3
"""
Test script for hybrid extraction system
Tests both transformer and LLM extraction methods
"""
import sys
import json
from pathlib import Path

# Add backend to path
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from extraction.hybrid import HybridExtractor, ExtractionMethod
from extraction.llm.openai_extractor import LLMClient


def test_transformer_extraction():
    """Test OS-Climate transformer extraction"""
    print("=" * 60)
    print("TEST 1: Transformer-Only Extraction")
    print("=" * 60)

    extractor = HybridExtractor(use_transformer=True, use_llm=False)

    # Test with sample text
    test_text = """
    A empresa reporta emissões totais de Escopo 1 de 1.250 toneladas de CO2e
    para o ano fiscal de 2024. As emissões de Escopo 2 foram de 3.500 toneladas.
    """

    result = extractor.extract(
        text=test_text,
        method=ExtractionMethod.TRANSFORMER,
        document_meta={"company": "Test Corp", "fiscal_year": "2024"}
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    return result


def test_llm_extraction():
    """Test LLM extraction with mock mode"""
    print("=" * 60)
    print("TEST 2: LLM-Only Extraction (Mock Mode)")
    print("=" * 60)

    # Use mock mode (no API calls)
    import os
    os.environ["LLM_MOCK"] = "1"

    extractor = HybridExtractor(use_transformer=False, use_llm=True)

    # Sample evidence
    evidence = [
        {
            "document_id": "test_doc_1",
            "page": 12,
            "text": "Emissões Escopo 1: 1.250 tCO2e. Escopo 2: 3.500 tCO2e."
        }
    ]

    # Mock schema
    schema = {
        "type": "object",
        "properties": {
            "kpis": {"type": "object"}
        }
    }

    # Mock template
    template = "Extract climate data: {{evidence_chunks}}"

    result = extractor.extract(
        evidence_chunks=evidence,
        document_meta={"company": "Test Corp", "fiscal_year": "2024"},
        template=template,
        schema=schema,
        method=ExtractionMethod.LLM
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    return result


def test_hybrid_extraction():
    """Test hybrid extraction combining both methods"""
    print("=" * 60)
    print("TEST 3: Hybrid Extraction (Transformer + LLM)")
    print("=" * 60)

    import os
    os.environ["LLM_MOCK"] = "1"

    extractor = HybridExtractor(use_transformer=True, use_llm=True)

    # Sample data
    test_text = """
    Relatório de Sustentabilidade 2024
    Emissões de GEE:
    - Escopo 1 (diretas): 1.250 tCO2e
    - Escopo 2 (indiretas): 3.500 tCO2e
    - Escopo 3 (cadeia): 12.000 tCO2e
    """

    evidence = [
        {
            "document_id": "test_doc_1",
            "page": 1,
            "text": test_text
        }
    ]

    schema = {
        "type": "object",
        "properties": {
            "kpis": {
                "type": "object",
                "properties": {
                    "emissions_scope1": {"type": "number"},
                    "emissions_scope2": {"type": "number"},
                    "emissions_scope3": {"type": "number"}
                }
            }
        }
    }

    template = "Extract IFRS S2 KPIs: {{evidence_chunks}}"

    result = extractor.extract(
        text=test_text,
        evidence_chunks=evidence,
        document_meta={"company": "Test Corp", "fiscal_year": "2024"},
        template=template,
        schema=schema,
        method=ExtractionMethod.HYBRID
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Print confidence voting summary
    if "kpis" in result:
        print("\n📊 Confidence Voting Summary:")
        print("-" * 60)
        for key, value in result["kpis"].items():
            if isinstance(value, dict):
                conf = value.get("confidence", 0)
                method = value.get("method", "unknown")
                agreement = value.get("agreement", False)
                print(f"{key}:")
                print(f"  Method: {method}")
                print(f"  Confidence: {conf:.2%}")
                print(f"  Agreement: {'✓' if agreement else '✗'}")

    return result


def main():
    """Run all tests"""
    print("\n🟣 PÚRPURA Hybrid Extraction Test Suite\n")

    try:
        # Test 1: Transformer
        test_transformer_extraction()

        # Test 2: LLM
        test_llm_extraction()

        # Test 3: Hybrid
        test_hybrid_extraction()

        print("\n✅ All tests completed!")
        print("\nNext steps:")
        print("1. Install actual OS-Climate tools: pip install -r requirements.txt")
        print("2. Integrate real osc-transformer-presteps in osc_adapter.py")
        print("3. Test with real PDF documents")
        print("4. Compare extraction quality: transformer vs LLM vs hybrid")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
