import os, json, time
from src.utils.trino_client import connect, wait_ready

def sql_str(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"

def _exec_retry(cur, q, retries=10, delay=1.5):
    for i in range(retries):
        try:
            cur.execute(q); return
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(delay)

def publish_jsonl(path: str, batch_size: int = 50):
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline()
        if not first:
            print("Arquivo vazio:", path); return
        rec0 = json.loads(first)

    wait_ready(max_wait=240)
    conn = connect(); cur = conn.cursor()
    cat = os.getenv("TRINO_CATALOG","lake"); sch = os.getenv("TRINO_SCHEMA","ifrs")

    def insert_raw(rows):
        if not rows: return
        values = ",".join("(" + ",".join([
            sql_str(r["doc_id"]),
            sql_str(r["chunk_id"]),
            sql_str(r.get("source_path")),
            sql_str(int(r.get("created_at", int(time.time())))),
            sql_str(int(r.get("token_len", 0))),
            sql_str(int(r.get("char_len", 0))),
            sql_str(r.get("text_sha256")),
            sql_str(r.get("text","")),
        ]) + ")" for r in rows)
        q = f"INSERT INTO {cat}.{sch}.raw_chunks (doc_id, chunk_id, source_path, created_at, token_len, char_len, text_sha256, text) VALUES {values}"
        _exec_retry(cur, q)

    def insert_results(rows):
        if not rows: return
        values = ",".join("(" + ",".join([
            sql_str(r["doc_id"]),
            sql_str(r["chunk_id"]),
            sql_str(json.dumps(r.get("result"), ensure_ascii=False)),
            sql_str(int(time.time())),
        ]) + ")" for r in rows)
        q = f"INSERT INTO {cat}.{sch}.extract_results (doc_id, chunk_id, result_json, created_at) VALUES {values}"
        _exec_retry(cur, q)

    is_raw = set(["doc_id","chunk_id","source_path","text"]).issubset(rec0.keys())
    is_res = set(["doc_id","chunk_id","result"]).issubset(rec0.keys())
    if not (is_raw or is_res):
        raise SystemExit("Formato não reconhecido (esperado JSONL de raw_chunks ou extract_results).")

    batch, n = [], 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            rec = json.loads(line); batch.append(rec)
            if len(batch) >= batch_size:
                (insert_raw if is_raw else insert_results)(batch); n += len(batch); batch = []
        if batch:
            (insert_raw if is_raw else insert_results)(batch); n += len(batch)
    print("OK: publicado", n, "registro(s) em", f"{cat}.{sch}.raw_chunks" if is_raw else f"{cat}.{sch}.extract_results")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("jsonl_path")
    args = ap.parse_args(); publish_jsonl(args.jsonl_path)
