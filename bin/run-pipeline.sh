#!/bin/bash
#
# bin/run-pipeline.sh
#
# Riscos:
# 1. Falha silenciosa de passos individuais do pipeline se as saídas dos comandos docker exec não forem verificadas (set -e).
# 2. Containers desligados no momento da execução automatizada via cron do host, quebrando o agendamento.
# 3. Armazenamento de logs locais crescendo indefinidamente sem rotação física, exaurindo o espaço em disco do host.
#
# Ambiguidades:
# 1. Se o script deve tentar subir os containers automaticamente (docker compose up -d) se detectá-los desligados.
# 2. Se a gravação de logs deve ser escrita em arquivo montado no host ou enviada direto para o stdout/stderr do syslog local.

set -e # Aborta o script em caso de falha em qualquer comando

# Configuração de caminhos e logs
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CWD="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$CWD/logs"
LOG_FILE="$LOG_DIR/pipeline_$(date +'%Y%m%d_%H%M%S').log"

# Garante existência do diretório de logs
mkdir -p "$LOG_DIR"

# Função para registrar logs estruturados com timestamps
log_msg() {
    local level="$1"
    local message="$2"
    local ts=$(date +'%Y-%m-%d %H:%M:%S')
    echo "[$ts] [$level] $message" | tee -a "$LOG_FILE"
}

log_msg "INFO" "Iniciando execução do pipeline analítico Northwind"

# 1. Verifica se os containers estão rodando
if ! docker ps | grep -q "northwind-pipeline"; then
    log_msg "WARNING" "Container 'northwind-pipeline' não está rodando. Tentando inicializar via docker compose..."
    cd "$CWD"
    docker compose up -d
    sleep 3
fi

# 2. Executa a ingestão de dados brutos no MinIO
log_msg "INFO" "Passo 1/4: Iniciando Ingestão de arquivos CSV locais no MinIO..."
if docker exec northwind-pipeline python3 app/ingest.py >> "$LOG_FILE" 2>&1; then
    log_msg "INFO" "Passo 1/4 concluído com sucesso."
else
    log_msg "ERROR" "Falha crítica no Passo 1/4 (Ingestão). Abortando pipeline."
    exit 1
fi

# 3. Executa as transformações analíticas do dbt
log_msg "INFO" "Passo 2/4: Executando transformações analíticas dbt (DuckDB)..."
if docker exec northwind-pipeline dbt run --profiles-dir transform --project-dir transform >> "$LOG_FILE" 2>&1; then
    log_msg "INFO" "Passo 2/4 concluído com sucesso."
else
    log_msg "ERROR" "Falha crítica no Passo 2/4 (dbt run). Abortando pipeline."
    exit 1
fi

# 4. Executa os testes de qualidade de dados do dbt
log_msg "INFO" "Passo 3/4: Executando suíte de testes do dbt (qualidade de dados)..."
if docker exec northwind-pipeline dbt test --profiles-dir transform --project-dir transform >> "$LOG_FILE" 2>&1; then
    log_msg "INFO" "Passo 3/4 concluído com sucesso."
else
    log_msg "ERROR" "Falha crítica no Passo 3/4 (dbt test). Abortando pipeline."
    exit 1
fi

# 5. Executa a auditoria quantitativa de reconciliação
log_msg "INFO" "Passo 4/4: Executando auditoria quantitativa e verificação de integridade..."
if docker exec northwind-pipeline python3 app/audit.py >> "$LOG_FILE" 2>&1; then
    log_msg "INFO" "Passo 4/4 concluído com sucesso."
else
    log_msg "ERROR" "Falha crítica no Passo 4/4 (Auditoria / Perda de Linhas). Abortando pipeline."
    exit 1
fi

log_msg "INFO" "=== PIPELINE EXECUTADO COM SUCESSO DE PONTA A PONTA ==="
exit 0
