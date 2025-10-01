import json
import sys
from pathlib import Path

# Resolve repo root based on this file's location (scripts/..)
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.extract.llm_extractor import LLMClient, extract

# Load resources relative to repo root so the script works from any CWD
schema_path = REPO_ROOT / "schemas/ifrs_s2_core.schema.json"
template_path = REPO_ROOT / "prompts/ifrs_s2_extractor_prompt.md"

schema = json.loads(schema_path.read_text(encoding="utf-8"))
template = template_path.read_text(encoding="utf-8")

doc = {"document_id": "demo_doc_1", "company": "ACME", "fiscal_year": "2024"}
evidence = [
    {
        "document_id": "demo_doc_1",
        "page": 1,
        "text": "A empresa reporta exposição a riscos físicos, incluindo inundação e estresse térmico, com maior impacto no curto prazo.",
    }
]

res = extract(doc, evidence, LLMClient(), template, schema)
print(json.dumps(res, ensure_ascii=False, indent=2))
