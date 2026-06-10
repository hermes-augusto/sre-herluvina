#!/bin/bash
# bin/ci-integration-test.sh
#
# Riscos:
# 1. Loop infinito ou travamento do CI se o health check do MinIO nunca retornar status saudável devido a falha interna.
# 2. Conflito de portas se o runner do GitHub Actions já tiver algum processo escutando nas portas do MinIO (9000) ou Streamlit (8501).
# 3. Falha ao tentar limpar os recursos (docker compose down) se algum container travar em estado irrecuperável.
#
# Ambiguidades:
# 1. Se o script deve injetar automaticamente variáveis mockadas no arquivo .env se este não for gerado previamente no runner de CI.
# 2. Se a limpeza dos volumes (docker compose down -v) deve ser executada mesmo se o pipeline de teste dinâmico falhar, para evitar vazamento de memória em runners auto-hospedados.

set -e

# Garante que estamos na raiz do projeto
cd "$(dirname "$0")/.."

echo "=== [INTEGRAÇÃO] Configurando arquivo de ambiente local ==="
if [ ! -f .env ]; then
    echo "[INFO] Criando .env a partir de .env.example..."
    cp .env.example .env
fi

echo "=== [INTEGRAÇÃO] Inicializando os containers Docker (Build)...=="
docker compose down -v --remove-orphans || true
docker compose up -d --build

# Função de limpeza automática ao sair do script
cleanup() {
    local exit_code=$?
    echo "=== [INTEGRAÇÃO] Limpando recursos do Docker Compose... ==="
    docker compose down -v || true
    exit $exit_code
}
trap cleanup EXIT

echo "=== [INTEGRAÇÃO] Aguardando o MinIO ficar saudável (Health Check)... ==="
MAX_ATTEMPTS=30
ATTEMPT=1
MINIO_HEALTHY=false

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    STATUS=$(docker inspect --format='{{json .State.Health.Status}}' northwind-minio 2>/dev/null || echo "unhealthy")
    if [ "$STATUS" = "\"healthy\"" ]; then
        echo "[SUCESSO] MinIO está saudável após $ATTEMPT tentativa(s)."
        MINIO_HEALTHY=true
        break
    fi
    echo "[AGUARDANDO] Tentativa $ATTEMPT/$MAX_ATTEMPTS: Status atual do MinIO é $STATUS. Dormindo 2s..."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

if [ "$MINIO_HEALTHY" = "false" ]; then
    echo "[ERRO] MinIO falhou no Health Check após o tempo limite. Exibindo logs:"
    docker logs northwind-minio
    exit 1
fi

echo "=== [INTEGRAÇÃO] Disparando a execução ponta a ponta do pipeline local ==="
# Executa o pipeline e coleta saída
if ./bin/run-pipeline.sh; then
    echo "=== [INTEGRAÇÃO] SUCESSO: Pipeline executado com 100% de paridade e sucesso! ==="
    exit 0
else
    echo "=== [INTEGRAÇÃO] ERRO: Pipeline falhou durante a execução! Exibindo logs do container do pipeline... ==="
    docker logs northwind-pipeline
    exit 1
fi
