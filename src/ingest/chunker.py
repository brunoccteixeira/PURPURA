import re
from typing import List, Dict

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    _enc = None

def count_tokens(s: str) -> int:
    if _enc:
        return len(_enc.encode(s))
    return max(1, len(s)//4)

def chunk_text(text: str, max_tokens: int = 800, overlap: int = 120) -> List[Dict]:
    words = re.split(r"(\s+)", text)
    chunks = []
    buf = []
    tok = 0
    for w in words:
        w_tok = count_tokens(w)
        if tok + w_tok > max_tokens and buf:
            chunk = "".join(buf).strip()
            chunks.append({"text": chunk, "token_len": count_tokens(chunk)})
            back = []
            back_tok = 0
            j = len(buf) - 1
            while j >= 0 and back_tok < overlap:
                back.insert(0, buf[j])
                back_tok += count_tokens(buf[j])
                j -= 1
            buf = back + [w]
            tok = back_tok + w_tok
        else:
            buf.append(w)
            tok += w_tok
    if buf:
        chunk = "".join(buf).strip()
        chunks.append({"text": chunk, "token_len": count_tokens(chunk)})
    return chunks
