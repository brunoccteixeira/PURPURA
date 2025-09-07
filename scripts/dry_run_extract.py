import json
from pathlib import Path
from src.extract.llm_extractor import LLMClient, extract

schema = json.loads(Path("schemas/ifrs_s2_core.schema.json").read_text())
template = Path("prompts/ifrs_s2_extractor_prompt.md").read_text()

doc = {"document_id":"demo_doc_1","company":"ACME","fiscal_year":"2024"}
evidence = [
  {"document_id":"demo_doc_1","page":1,
   "text":"A empresa reporta exposição a riscos físicos, incluindo inundação e estresse térmico, com maior impacto no curto prazo."}
]

res = extract(doc, evidence, LLMClient(), template, schema)
print(json.dumps(res, ensure_ascii=False, indent=2))
