import os
from trino.dbapi import connect

CATALOG = os.getenv("TRINO_CATALOG", "lake")
SCHEMA  = os.getenv("TRINO_SCHEMA", "ifrs")
WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "s3a://purpura/lake/ifrs/")

def conn():
    host = os.environ["TRINO_HOST"]
    port = int(os.getenv("TRINO_PORT", "8080"))
    user = os.getenv("TRINO_USER", "purpura")
    password = os.getenv("TRINO_PASSWORD")  # opcional
    # Se precisar TLS/BasicAuth, ajuste conforme seu cluster
    return connect(host=host, port=port, user=user, catalog=CATALOG, schema="system")

def run():
    con = conn()
    cur = con.cursor()

    # 1) schema (no catálogo)
    ddl_schema = f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA} WITH (location = '{WAREHOUSE}')"
    print("DDL:", ddl_schema)
    cur.execute(ddl_schema)

    # 2) tabelas Iceberg
    ddl_kpis = f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.ifrs_s2_kpis (
      company VARCHAR,
      document_id VARCHAR,
      fiscal_year VARCHAR,
      kpi_key VARCHAR,
      value_json JSON,
      created_at TIMESTAMP
    ) WITH (format='ICEBERG')
    """
    ddl_ev = f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.ifrs_s2_evidence (
      document_id VARCHAR,
      page INTEGER,
      quote VARCHAR,
      kpi_key VARCHAR,
      created_at TIMESTAMP
    ) WITH (format='ICEBERG')
    """
    for ddl in (ddl_kpis, ddl_ev):
        print("DDL:", " ".join(ddl.split()))
        cur.execute(ddl)

    con.close()
    print("OK: schema e tabelas criados.")

if __name__ == "__main__":
    run()
