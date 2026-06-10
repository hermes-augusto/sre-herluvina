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

set_env_var() {
    local key="$1"
    local value="$2"
    local tmp_file
    tmp_file="$(mktemp)"

    if grep -q "^${key}=" .env; then
        awk -v key="$key" -v value="$value" '
            BEGIN { FS = OFS = "=" }
            $1 == key { $0 = key "=" value }
            { print }
        ' .env > "$tmp_file"
    else
        cp .env "$tmp_file"
        printf "%s=%s\n" "$key" "$value" >> "$tmp_file"
    fi

    mv "$tmp_file" .env
}

echo "[INFO] Ajustando UID/GID do .env para o usuário do runner..."
set_env_var "UID" "$(id -u)"
set_env_var "GID" "$(id -g)"

echo "[INFO] Garantindo diretórios locais graváveis antes dos bind mounts..."
mkdir -p logs data

if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    echo "[ERRO] Docker Compose não encontrado. Instale o plugin 'docker compose' ou o binário 'docker-compose'."
    exit 1
fi

echo "=== [INTEGRAÇÃO] Inicializando os containers Docker (Build)...=="
"${COMPOSE_CMD[@]}" down -v --remove-orphans || true
"${COMPOSE_CMD[@]}" up -d --build

# Função de limpeza automática ao sair do script
cleanup() {
    local exit_code=$?
    echo "=== [INTEGRAÇÃO] Limpando recursos do Docker Compose... ==="
    "${COMPOSE_CMD[@]}" down -v || true
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
