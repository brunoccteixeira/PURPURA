# Observability Stack - PÚRPURA Climate OS

Sistema completo de monitoramento e observabilidade usando Prometheus + Grafana.

## 🎯 Visão Geral

O PÚRPURA implementa um stack de observabilidade completo para monitorar performance, saúde e comportamento da API em tempo real.

### Componentes

- **Prometheus**: Coleta e armazena métricas time-series
- **Grafana**: Visualização de métricas e dashboards
- **Prometheus Client (Python)**: Exporta métricas da aplicação

## 📊 Métricas Exportadas

### Métricas HTTP

- `purpura_http_requests_total` - Total de requests HTTP (por method, endpoint, status_code)
- `purpura_http_request_duration_seconds` - Duração das requests (histogram com percentis)
- `purpura_http_requests_in_progress` - Requests ativas sendo processadas (gauge)

### Métricas de Rate Limiting

- `purpura_rate_limit_hits_total` - Total de rate limits atingidos
- `purpura_rate_limit_remaining` - Requests restantes no limite

### Métricas de Erros

- `purpura_api_errors_total` - Erros da API (por tipo e endpoint)
- `purpura_api_exceptions_total` - Exceções não tratadas

### Métricas de Cache

- `purpura_cache_operations_total` - Operações de cache (hit/miss)
- `purpura_cache_hit_ratio` - Taxa de cache hit (0.0 a 1.0)

### Métricas de APIs Externas

- `purpura_external_api_calls_total` - Chamadas para APIs externas (INPE, ANA)
- `purpura_external_api_duration_seconds` - Duração das chamadas externas

### Métricas de Banco de Dados

- `purpura_trino_queries_total` - Queries Trino executadas
- `purpura_trino_query_duration_seconds` - Duração das queries

### Métricas de LLM

- `purpura_llm_extractions_total` - Extrações LLM realizadas
- `purpura_llm_extraction_duration_seconds` - Duração das extrações
- `purpura_llm_tokens_used_total` - Tokens consumidos (prompt + completion)

## 🚀 Quick Start

### 1. Iniciar Backend com Métricas

```bash
# Backend já exporta métricas automaticamente
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

### 2. Acessar Endpoint de Métricas

```bash
# Verificar métricas Prometheus
curl http://localhost:8000/metrics
```

### 3. Iniciar Prometheus e Grafana

```bash
# Iniciar stack completo
docker compose up -d prometheus grafana

# Verificar status
docker compose ps
```

### 4. Acessar Interfaces

- **Prometheus UI**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - User: `admin`
  - Password: `admin`

## 📈 Dashboards Grafana

### Dashboard: PÚRPURA API Overview

Localização: `grafana/dashboards/purpura-api-overview.json`

**Painéis incluídos:**

1. **Request Rate** - Taxa de requests por segundo
2. **Active Requests** - Número de requests ativas
3. **Success Rate** - Taxa de sucesso (non-5xx responses)
4. **Response Time (p95)** - Tempo de resposta no percentil 95
5. **Request Rate by Method** - Taxa de requests por método HTTP
6. **Response Status Codes** - Distribuição de códigos de status
7. **Response Time Percentiles by Endpoint** - Percentis (p50, p95, p99) por endpoint
8. **Rate Limit Hits** - Rate limits atingidos na última hora
9. **API Errors Rate** - Taxa de erros da API

O dashboard é auto-provisionado ao iniciar o Grafana.

## 🔧 Configuração

### Prometheus

Arquivo: `prometheus/prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'purpura-api'
    scrape_interval: 10s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

**Configurações importantes:**
- `scrape_interval`: 10s (coleta métricas a cada 10 segundos)
- `evaluation_interval`: 15s
- Retenção de dados: 15 dias (padrão)

### Grafana

**Datasource auto-provisionado:**
- Arquivo: `grafana/provisioning/datasources/prometheus.yml`
- URL: `http://prometheus:9090`
- Método HTTP: POST
- Intervalo de tempo: 15s

**Dashboards auto-provisionados:**
- Arquivo: `grafana/provisioning/dashboards/dashboards.yml`
- Diretório: `grafana/dashboards/`
- Update interval: 10s

## 📝 Exemplo de Uso

### Coletar Métricas Customizadas

```python
from backend.utils.prometheus_metrics import MetricsCollector

# Registrar chamada de API externa
MetricsCollector.record_external_api_call(
    api_name="INPE",
    status="success",
    duration=1.25
)

# Registrar extração LLM
MetricsCollector.record_llm_extraction(
    model="gpt-4o-mini",
    status="success",
    duration=3.5,
    tokens_used={"prompt_tokens": 150, "completion_tokens": 80}
)

# Registrar query Trino
MetricsCollector.record_trino_query(
    query_type="select",
    status="success",
    duration=0.5
)
```

### Queries PromQL Úteis

**Taxa de requests por segundo:**
```promql
rate(purpura_http_requests_total[1m])
```

**Taxa de sucesso:**
```promql
sum(rate(purpura_http_requests_total{status_code!~"5.."}[5m]))
/
sum(rate(purpura_http_requests_total[5m]))
```

**Percentil 95 de latência:**
```promql
histogram_quantile(0.95,
  sum(rate(purpura_http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)
```

**Requests mais lentas (top 5 endpoints):**
```promql
topk(5,
  histogram_quantile(0.95,
    sum(rate(purpura_http_request_duration_seconds_bucket[5m])) by (le, endpoint)
  )
)
```

**Taxa de rate limit por tipo de identificador:**
```promql
sum by(identifier_type) (
  rate(purpura_rate_limit_hits_total[1h])
)
```

## 🔍 Troubleshooting

### Métricas não aparecem no Prometheus

1. Verificar se o backend está rodando:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Verificar targets no Prometheus:
   - Acessar http://localhost:9090/targets
   - Verificar se `purpura-api` está UP

3. Verificar logs do Prometheus:
   ```bash
   docker compose logs prometheus
   ```

### Grafana não mostra dados

1. Verificar datasource:
   - Configuration → Data Sources → Prometheus
   - Clicar em "Save & Test"

2. Verificar se há dados no Prometheus:
   - Acessar http://localhost:9090/graph
   - Executar query: `purpura_http_requests_total`

3. Ajustar time range no Grafana:
   - Usar "Last 15 minutes" ou "Last 1 hour"

### Dashboard não foi provisionado

1. Verificar volumes montados:
   ```bash
   docker compose config
   ```

2. Verificar permissões dos arquivos:
   ```bash
   ls -la grafana/dashboards/
   ```

3. Reiniciar Grafana:
   ```bash
   docker compose restart grafana
   ```

## 🎨 Personalizando Dashboards

### Adicionar Novo Painel

1. Editar `grafana/dashboards/purpura-api-overview.json`
2. Adicionar novo objeto no array `panels`
3. Reiniciar Grafana ou aguardar auto-reload (10s)

### Criar Novo Dashboard

1. Criar arquivo JSON em `grafana/dashboards/`
2. Seguir estrutura do dashboard existente
3. Grafana irá auto-provisionar na próxima inicialização

## 📦 Estrutura de Arquivos

```
├── backend/
│   ├── utils/
│   │   └── prometheus_metrics.py       # Definição de métricas
│   └── middleware/
│       └── prometheus_middleware.py     # Middleware de coleta
│   └── api/
│       └── routers/
│           └── prometheus.py            # Endpoint /metrics
├── prometheus/
│   └── prometheus.yml                   # Config do Prometheus
├── grafana/
│   ├── dashboards/
│   │   └── purpura-api-overview.json   # Dashboard principal
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml           # Datasource config
│       └── dashboards/
│           └── dashboards.yml           # Dashboard provisioning
└── docker-compose.yml                   # Prometheus + Grafana services
```

## 🔐 Segurança

### Considerações de Produção

1. **Autenticação Grafana**:
   - Alterar senha padrão `admin/admin`
   - Configurar OAuth ou LDAP
   - Desabilitar signup: `GF_USERS_ALLOW_SIGN_UP=false`

2. **Prometheus**:
   - Habilitar autenticação básica
   - Restringir acesso ao endpoint `/metrics` via firewall
   - Usar HTTPS com certificados válidos

3. **Rede**:
   - Isolar Prometheus/Grafana em rede interna
   - Expor apenas Grafana via reverse proxy (Nginx/Traefik)

### Variáveis de Ambiente

```bash
# Grafana
export GF_SECURITY_ADMIN_USER=admin
export GF_SECURITY_ADMIN_PASSWORD=strong_password
export GF_SERVER_ROOT_URL=https://grafana.purpura.com

# Prometheus (se usar autenticação)
export PROMETHEUS_AUTH_USER=metrics
export PROMETHEUS_AUTH_PASSWORD=secret
```

## 📚 Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Python Prometheus Client](https://github.com/prometheus/client_python)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
