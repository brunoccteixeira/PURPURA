import os, re, json
from typing import Any, Dict, Optional

def _bool(pat: str, text: str) -> bool:
    return re.search(pat, text, flags=re.IGNORECASE) is not None

def _first_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("página ") or line.startswith("[PAGE "):
            continue
        if len(line) >= 6:
            return line[:140]
    return "document"

def extract(text: str, schema_path: Optional[str] = None) -> Dict[str, Any]:
    is_mock = os.getenv("LLM_MOCK", "") != ""

    # Padrões robustos (com §/§§ e en dash)
    p_s2_29 = r"\bS2\s*[§]{0,2}\s*29\b"
    p_s1_77_81 = r"\bS1\s*[§]{0,2}\s*77\s*[–-]?\s*81\b"

    mentions_s2_29 = _bool(p_s2_29, text)
    mentions_s1_77_81 = _bool(p_s1_77_81, text)

    # Metas e base
    year_target = 2030 if re.search(r"\b2030\b", text) else None
    base_year = 2023 if re.search(r"base\s*:?\s*2023", text, flags=re.IGNORECASE) else None

    # Redução GEE em %
    ghg_red = None
    m = re.search(r"(\d{1,3})\s*%\s*(?:de\s*)?(?:redu[cç][aã]o|ghg|gee)", text, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"redu[cç][aã]o[^\n%]{0,40}?(\d{1,3})\s*%", text, flags=re.IGNORECASE)
    if m:
        try:
            v = int(m.group(1))
            if 0 <= v <= 100:
                ghg_red = v / 100.0
        except Exception:
            pass

    title = _first_title(text)

    return {
        "meta": {
            "adapter": "llm_extractor_adapter",
            "mock_mode": is_mock,
            "schema_path": schema_path or "",
        },
        "document": { "title_guess": title },
        "detections": {
            "mentions": {
                "ifrs_s2_29": mentions_s2_29,
                "ifrs_s1_77_81": mentions_s1_77_81,
            },
            "targets": ({
                "year": year_target,
                "base_year": base_year,
                "ghg_reduction_fraction": ghg_red
            } if (year_target or base_year or ghg_red is not None) else None),
        },
        "sample_excerpt": text[:600],
    }
