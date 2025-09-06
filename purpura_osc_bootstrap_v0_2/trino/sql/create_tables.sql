CREATE TABLE IF NOT EXISTS lake.ifrs_s2_kpis (document_id VARCHAR, kpi_key VARCHAR, value_json JSON) WITH (format='ICEBERG');
