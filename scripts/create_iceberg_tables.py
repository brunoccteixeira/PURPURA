import os, time
from src.utils.trino_client import connect, wait_ready

def _exec_retry(cur, q, retries=10, delay=1.5):
    import trino
    for i in range(retries):
        try:
            cur.execute(q); return
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(delay)

def main():
    wh = os.getenv('ICEBERG_WAREHOUSE', 's3a://purpura/lake/ifrs/')
    cat = os.getenv('TRINO_CATALOG', 'lake')
    sch = os.getenv('TRINO_SCHEMA', 'ifrs')

    wait_ready(max_wait=240)  # aguarda SELECT 1 OK
    conn = connect(); cur = conn.cursor()

    _exec_retry(cur, f"""CREATE SCHEMA IF NOT EXISTS {cat}.{sch} WITH (location = '{wh}')""")

    _exec_retry(cur, f"""CREATE TABLE IF NOT EXISTS {cat}.{sch}.raw_chunks (
      doc_id VARCHAR,
      chunk_id VARCHAR,
      source_path VARCHAR,
      created_at BIGINT,
      token_len INTEGER,
      char_len INTEGER,
      text_sha256 VARCHAR,
      text VARCHAR
    ) WITH (format = 'PARQUET')""")

    _exec_retry(cur, f"""CREATE TABLE IF NOT EXISTS {cat}.{sch}.extract_results (
      doc_id VARCHAR,
      chunk_id VARCHAR,
      result_json VARCHAR,
      created_at BIGINT
    ) WITH (format = 'PARQUET')""")

    print('OK: schemas/tabelas prontas.')

if __name__ == '__main__':
    main()
