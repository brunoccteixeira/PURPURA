from dataclasses import dataclass
from typing import List
import hashlib
from pypdf import PdfReader

@dataclass
class Page:
    page: int
    text: str

def read_pdf(path: str) -> List[Page]:
    reader = PdfReader(path)
    pages = []
    for i, pg in enumerate(reader.pages):
        try:
            t = pg.extract_text() or ""
        except Exception:
            t = ""
        pages.append(Page(page=i+1, text=t))
    return pages

def concat_pages(pages: List[Page]) -> str:
    parts = []
    for pg in pages:
        parts.append(f"[PAGE {pg.page}]\n{pg.text.strip()}\n")
    return "\n".join(parts)

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()
