# Roadmap

Este documento registra as principais sugestões para evoluir o PÚRPURA e as organiza por prioridade.

## Alta Prioridade
- **Stack conteinerizada de dados e IA**: adicionar `docker-compose` com MinIO, Nessie, Trino, Qdrant, FastAPI e Superset para fornecer ambiente reprodutível e plataforma de dados completa.
- **Data lakehouse IFRS S2**: definir schemas Iceberg para emissões, riscos climáticos e métricas (ex.: `ghg_emissions`, `climate_risks`, `ifrs_s2_metrics`).
- **RAG para conformidade**: implementar vetor DB Qdrant e processamento LLM para análise de conformidade, substituindo stubs de recuperação e verificação.

## Média Prioridade
- **Pipeline de dados**: construir rotinas de validação, enriquecimento e inserção de dados de emissões e riscos usando Trino.
- **API FastAPI**: expor endpoints para análise de conformidade, cálculo de impacto financeiro e consulta a métricas.
- **Dashboards Superset**: criar visualizações para trajetória de emissões, matriz de riscos e métricas IFRS S2.

## Baixa Prioridade
- **Scripts de inicialização**: automatizar bootstrap do ambiente (criação de buckets, schemas, indexação de documentos e configuração do Superset).
- **Integração OS-Climate**: adicionar adaptadores para entity matching e acesso ao data commons do OS-Climate.

