#!/usr/bin/env python3
import argparse, json, os, time, uuid
from pathlib import Path
from src.ingest.pdf_ingestor import read_pdf, sha256_text, concat_pages
from src.ingest.chunker import chunk_text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf_path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--doc-id", default=None)
    ap.add_argument("--max-tokens", type=int, default=800)
    ap.add_argument("--overlap", type=int, default=120)
    args = ap.parse_args()

    pdf_path = Path(args.pdf_path).expanduser()
    pages = read_pdf(str(pdf_path))
    full_text = concat_pages(pages)

    doc_id = args.doc_id or f"doc_{uuid.uuid4().hex[:8]}"
    chunks = chunk_text(full_text, args.max_tokens, args.overlap)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as f:
        for i, ch in enumerate(chunks, start=1):
            rec = {
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_c{i:04d}",
                "page_start": None,
                "page_end": None,
                "source_path": str(pdf_path),
                "created_at": int(time.time()),
                "text": ch["text"],
                "token_len": ch["token_len"],
                "char_len": len(ch["text"]),
                "text_sha256": sha256_text(ch["text"]),
            }
            f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    print(f"Wrote {len(chunks)} chunks to {args.out}")

if __name__ == "__main__":
    main()
