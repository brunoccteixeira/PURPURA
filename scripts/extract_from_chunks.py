#!/usr/bin/env python3
import argparse, json, importlib, inspect
from pathlib import Path

def dynamic_call(mod, text, schema_path=None):
    candidates = ["extract", "run_extractor", "run", "extract_text", "main"]
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            sig = inspect.signature(fn)
            kwargs = {}
            params = list(sig.parameters.keys())
            if "text" in params:
                kwargs["text"] = text
            elif len(params) >= 1:
                return fn(text)
            if "schema_path" in params:
                kwargs["schema_path"] = schema_path
            try:
                return fn(**kwargs)
            except TypeError:
                continue
    raise RuntimeError("No suitable extractor() found in module")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chunks_jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--schema", default="schemas/ifrs_s2_core.schema.json")
    ap.add_argument("--module", default="src.extract.llm_extractor")
    args = ap.parse_args()

    mod = importlib.import_module(args.module.replace("/", "."))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with open(args.chunks_jsonl, "r", encoding="utf-8") as f, open(args.out, "w", encoding="utf-8") as out:
        for line in f:
            rec = json.loads(line)
            text = rec["text"]
            try:
                res = dynamic_call(mod, text, args.schema)
            except Exception as e:
                res = {"error": str(e)}
            out.write(json.dumps({"doc_id": rec["doc_id"], "chunk_id": rec["chunk_id"], "result": res}, ensure_ascii=False)+"\n")
            n += 1
    print(f"Done. {n} chunk(s) processed. Wrote: {args.out}")

if __name__ == "__main__":
    main()
