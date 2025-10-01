#!/usr/bin/env python3
"""
Test OS-Climate PDF extraction on real documents
"""
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from extraction.transformers.osc_adapter import OSCTransformerExtractor


def test_pdf_extraction(pdf_path: str):
    """Test PDF extraction with OS-Climate tools"""
    print("=" * 80)
    print(f"Testing PDF Extraction: {Path(pdf_path).name}")
    print("=" * 80)

    # Initialize extractor
    extractor = OSCTransformerExtractor()

    try:
        # Extract PDF
        result = extractor.extract_from_pdf(pdf_path)

        print(f"\n✓ Extraction successful!")
        print(f"Extractor: {result['raw_json']['metadata'].get('extractor', 'unknown')}")
        print(f"Total pages: {result['raw_json']['metadata']['total_pages']}")

        # Show first page preview
        if result['raw_json']['pages']:
            first_page = result['raw_json']['pages'][0]
            text_preview = first_page['text'][:500].replace('\n', ' ')
            print(f"\nFirst page preview (500 chars):")
            print(f"Page {first_page['page_number']}: {text_preview}...")

        # Save full results
        output_path = Path(pdf_path).with_suffix('.extraction.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Full extraction saved to: {output_path}")

        return result

    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run tests on available PDFs"""
    print("\n🟣 PÚRPURA PDF Extraction Test\n")

    # Find sample PDFs
    data_dir = Path(__file__).resolve().parents[2] / "data"
    pdf_files = list(data_dir.glob("**/*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found in data/ directory")
        print("\nTo test, add a PDF file to:")
        print(f"  {data_dir}/pdfs/samples/")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF file(s):\n")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"{i}. {pdf.relative_to(data_dir.parent)}")

    print("\n")

    # Test each PDF
    results = []
    for pdf_path in pdf_files[:3]:  # Limit to first 3
        result = test_pdf_extraction(str(pdf_path))
        if result:
            results.append({
                "file": pdf_path.name,
                "pages": result['raw_json']['metadata']['total_pages'],
                "extractor": result['raw_json']['metadata'].get('extractor')
            })
        print()

    # Summary
    if results:
        print("\n" + "=" * 80)
        print("EXTRACTION SUMMARY")
        print("=" * 80)
        for r in results:
            print(f"✓ {r['file']}: {r['pages']} pages ({r['extractor']})")

        print(f"\nTotal processed: {len(results)} / {len(pdf_files)}")
        print("\nNext: Run hybrid extraction (transformer + LLM) for KPI detection")
    else:
        print("\n❌ No successful extractions")


if __name__ == "__main__":
    main()
