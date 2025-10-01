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
      extraction_method VARCHAR,  -- 'transformer', 'llm', 'hybrid'
      kpis_json VARCHAR,  -- Structured KPIs with confidence scores
      confidence_avg DOUBLE,  -- Average confidence across all KPIs
      agreement_count INTEGER,  -- Number of KPIs where both methods agreed
      total_kpis INTEGER,  -- Total number of KPIs extracted
      transformer_result VARCHAR,  -- Full transformer results (JSON)
      llm_result VARCHAR,  -- Full LLM results (JSON)
      schema_valid BOOLEAN,  -- Schema validation passed
      schema_errors VARCHAR,  -- Validation errors if any
      created_at BIGINT,
      extracted_at TIMESTAMP  -- Timestamp from extraction process
    ) WITH (format = 'PARQUET')""")

    # New table for extraction confidence metrics
    _exec_retry(cur, f"""CREATE TABLE IF NOT EXISTS {cat}.{sch}.extraction_confidence (
      doc_id VARCHAR,
      kpi_name VARCHAR,
      value VARCHAR,
      confidence DOUBLE,
      method VARCHAR,  -- Method that provided the final value
      agreement BOOLEAN,  -- Did both methods agree?
      transformer_value VARCHAR,
      transformer_confidence DOUBLE,
      llm_value VARCHAR,
      llm_confidence DOUBLE,
      created_at BIGINT
    ) WITH (format = 'PARQUET')""")

    print('OK: schemas/tabelas prontas (incluindo metadados de confiança).')

if __name__ == '__main__':
    main()
