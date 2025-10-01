#!/usr/bin/env python3
"""Debug OS-Climate PDF extractor output format"""
from osc_transformer_presteps.content_extraction.extraction_factory import PDFExtractor
from pathlib import Path
import json

pdf_path = Path("data/pdfs/samples/ifrs_s2_demo.pdf")

print("🔍 Debugging OS-Climate PDF Extractor\n")

extractor = PDFExtractor()
print(f"✓ Extractor initialized: {type(extractor)}\n")

print(f"Extracting: {pdf_path}")
result = extractor.extract(pdf_path)

print(f"\nResult type: {type(result)}")
print(f"Result length (if list/dict): {len(result) if hasattr(result, '__len__') else 'N/A'}")

if isinstance(result, dict):
    print(f"\nDict keys: {list(result.keys())}")
    print(f"\nFull result:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str)[:2000])
elif isinstance(result, str):
    print(f"\nString result (first 500 chars):")
    print(result[:500])
elif isinstance(result, list):
    print(f"\nList with {len(result)} items")
    if result:
        print(f"First item type: {type(result[0])}")
        print(f"First item: {result[0][:500] if isinstance(result[0], str) else result[0]}")
else:
    print(f"\nUnexpected type: {result}")
