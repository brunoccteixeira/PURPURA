# Test Fixtures

This directory contains test data and fixtures for the PURPURA test suite.

## Directory Structure

```
fixtures/
├── sample_pdfs/          # PDF files for testing
├── sample_schemas/       # JSON schemas for testing
├── mock_responses/       # Mock LLM responses
└── README.md            # This file
```

## Sample PDFs

The `sample_pdfs/` directory should contain small PDF files for testing PDF ingestion and extraction.

### Adding Test PDFs

To add a test PDF:

1. Create a minimal PDF (1-2 pages) with climate-related content
2. Save it in `sample_pdfs/` directory
3. Recommended naming: `test_<description>.pdf`

Example test PDFs needed:
- `test_climate_report.pdf` - Small climate disclosure report
- `test_single_page.pdf` - Single page document
- `test_unicode.pdf` - Document with unicode characters

### Creating Test PDFs

You can create test PDFs using:

**Python (reportlab):**
```python
from reportlab.pdfgen import canvas

c = canvas.Canvas("test_climate_report.pdf")
c.drawString(100, 750, "Climate Risk Report 2023")
c.drawString(100, 700, "Our organization faces physical risks from extreme weather.")
c.drawString(100, 650, "GHG Emissions: Scope 1: 125,000 tCO2e")
c.showPage()
c.save()
```

**Online Tools:**
- Google Docs → Export as PDF
- LibreOffice → Export as PDF
- Any text-to-PDF converter

## Sample Schemas

JSON schemas in `sample_schemas/` are used to validate extraction results.

Current schemas:
- `test_ifrs_s2.schema.json` - Simplified IFRS S2 schema for testing

## Mock Responses

Mock LLM responses in `mock_responses/` simulate OpenAI API responses.

Current mock responses:
- `llm_response_complete.json` - Full extraction with all fields
- `llm_response_partial.json` - Partial extraction with missing fields

### Using Mock Responses in Tests

```python
import json
from pathlib import Path

fixtures_dir = Path(__file__).parent / "fixtures"
mock_response_path = fixtures_dir / "mock_responses" / "llm_response_complete.json"

with open(mock_response_path) as f:
    mock_response = json.load(f)
```

## Notes

- Keep test files minimal (< 100KB for PDFs)
- Use realistic but simplified data
- Include edge cases (empty content, unicode, special chars)
- Document any special test cases in this README
