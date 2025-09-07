from typing import Dict, Any, List, Tuple
import json, os, datetime, re, hashlib

# OpenAI SDK v1
from openai import OpenAI

JSON_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

def _extract_json_str(text: str) -> str:
    """Fallback: captura JSON de ```json ... ``` ou do maior bloco {...}."""
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S | re.M)
    if m:
        return m.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()
    raise ValueError("Nenhum objeto JSON encontrado na resposta do LLM.")

def _validate_with_schema_if_possible(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str | None]:
    """Validação opcional via jsonschema (se instalado). Retorna (ok, erro)."""
    try:
        from jsonschema import validate
        validate(instance=data, schema=schema)
        return True, None
    except ModuleNotFoundError:
        return True, None   # sem jsonschema, não invalida
    except Exception as e:
        return False, str(e)

def _mock_response(evidence_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Resposta determinística para dev sem chamar a API."""
    # gera um pequeno hash do primeiro trecho para variar minimamente
    seed = ""
    if evidence_chunks:
        seed = hashlib.sha1(evidence_chunks[0].get("text","").encode("utf-8")).hexdigest()[:8]
    return {
        "kpis": {
            "s2_mock": {
                "note": "LLM_MOCK=1 — resposta simulada para desenvolvimento",
                "seed": seed
            }
        }
    }

class LLMClient:
    """
    OpenAI-only (JSON mode):
      export OPENAI_API_KEY=...
      export OPENAI_MODEL=gpt-4o-mini
      # se usar org/projeto:
      export OPENAI_ORG_ID=org_xxx
      export OPENAI_PROJECT_ID=proj_xxx

    Mock (sem API):
      export LLM_MOCK=1
    """
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.mock = os.getenv("LLM_MOCK") == "1"

        if not self.mock:
            self.client = OpenAI(
                api_key=os.environ["OPENAI_API_KEY"],
                organization=os.getenv("OPENAI_ORG_ID"),
                project=os.getenv("OPENAI_PROJECT_ID"),
            )

    def extract_json(self, prompt: str, evidence_chunks: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        if self.mock:
            return _mock_response(evidence_chunks or [])

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are a structured-extraction model. Output ONLY valid JSON conforming to the user's schema."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"},
            timeout=JSON_TIMEOUT
        )
        txt = resp.choices[0].message.content
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return json.loads(_extract_json_str(txt))

def render_prompt(json_schema: dict, evidence_chunks: List[Dict[str, Any]], task: str, template: str) -> str:
    ev = []
    for i, ch in enumerate(evidence_chunks, 1):
        ev.append(f"[{i}] doc={ch.get('document_id')} page={ch.get('page')} :: {ch.get('text','')[:800]}")
    return (template
            .replace("{{json_schema}}", json.dumps(json_schema, ensure_ascii=False, indent=2))
            .replace("{{evidence_chunks}}", "\n\n".join(ev))
            .replace("{{task_description}}", task))

def extract(document_meta: Dict[str, Any],
            evidence_chunks: List[Dict[str, Any]],
            llm: LLMClient,
            template: str,
            schema: dict) -> Dict[str, Any]:
    """Executa extração estruturada, anexa metadados e valida (se jsonschema disponível)."""
    task = "Extract IFRS S2 KPIs for exposure to physical and transition risks. Return STRICT JSON."
    prompt = render_prompt(schema, evidence_chunks, task, template)
    result = llm.extract_json(prompt, evidence_chunks=evidence_chunks)

    # metadados + timestamp
    result["document_meta"] = document_meta
    result["extracted_at"] = datetime.datetime.utcnow().isoformat()

    # validação opcional
    ok, err = _validate_with_schema_if_possible(result, schema)
    if not ok:
        result["_schema_error"] = err

    return result
