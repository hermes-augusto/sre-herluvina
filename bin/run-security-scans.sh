#!/bin/bash
# bin/run-security-scans.sh
#
# Riscos:
# 1. Falha de execução dos containers de scan se o serviço do Docker host não estiver ativo ou acessível.
# 2. Lentidão extrema ou falha por timeout ao baixar imagens Docker volumosas do Trivy/Gitleaks/Bandit em conexões lentas.
# 3. Permissões de escrita negadas ao gerar relatórios locais de vulnerabilidades no diretório do host.
#
# Ambiguidades:
# 1. Se o script deve falhar/abortar (exit 1) imediatamente na primeira vulnerabilidade encontrada por qualquer ferramenta ou apenas listar os relatórios ao final.
# 2. Se o scan do Trivy deve focar apenas nas dependências do requirements.txt via filesystem (fs) ou também varrer a imagem Docker compilada.

set -o pipefail

echo "============================================================"
echo "🛡️  Iniciando Varredura de Segurança Northwind Traders"
echo "============================================================"

# Verifica se o Docker está instalado e rodando
if ! command -v docker &> /dev/null; then
    echo "[ERRO] Docker não encontrado no host. Por favor, instale o Docker para rodar os scans locais."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "[ERRO] O serviço do Docker não está ativo ou não responde. Inicie o Docker e tente novamente."
    exit 1
fi

# 1. SAST com Bandit
echo -e "\n🔍 Passo 1/3: Executando Bandit (SAST para código Python)..."
docker run --rm -v "$(pwd):/app" -w /app python:3.11-slim bash -c "pip install --no-cache-dir bandit && bandit -r app/"
BANDIT_STATUS=$?

if [ $BANDIT_STATUS -eq 0 ]; then
    echo "✅ Bandit: Nenhum problema de segurança de alto risco encontrado."
else
    echo "❌ Bandit: Vulnerabilidades estáticas detectadas."
fi

# 2. SCA com Trivy
echo -e "\n🔍 Passo 2/3: Executando Trivy (SCA para dependências e arquivos)..."
# Executa scan de filesystem ignorando erros de download de DB se estiver offline (modo leve)
docker run --rm -v "$(pwd):/app" -w /app aquasec/trivy:latest fs --severity HIGH,CRITICAL --exit-code 1 /app
TRIVY_STATUS=$?

if [ $TRIVY_STATUS -eq 0 ]; then
    echo "✅ Trivy: Nenhuma vulnerabilidade de alta/crítica encontrada nas dependências."
else
    echo "❌ Trivy: Vulnerabilidades HIGH/CRITICAL detectadas."
fi

# 3. Secret Scanning com Gitleaks
echo -e "\n🔍 Passo 3/3: Executando Gitleaks (Varredura de Segredos)..."
docker run --rm -v "$(pwd):/path" zricethezav/gitleaks:latest detect --source="/path" --config="/path/gitleaks.toml" --verbose --redact
GITLEAKS_STATUS=$?

if [ $GITLEAKS_STATUS -eq 0 ]; then
    echo "✅ Gitleaks: Nenhum segredo ou chave privada detectada no histórico."
else
    echo "❌ Gitleaks: Possível vazamento de credenciais no repositório."
fi

echo "============================================================"
echo "📊 Resumo dos Resultados de Segurança:"
echo "============================================================"
if [ $BANDIT_STATUS -eq 0 ]; then echo "  - Bandit (SAST): PASS"; else echo "  - Bandit (SAST): FAIL"; fi
if [ $TRIVY_STATUS -eq 0 ]; then echo "  - Trivy (SCA): PASS"; else echo "  - Trivy (SCA): FAIL"; fi
if [ $GITLEAKS_STATUS -eq 0 ]; then echo "  - Gitleaks (Secrets): PASS"; else echo "  - Gitleaks (Secrets): FAIL"; fi
echo "============================================================"

# Se algum scan falhou, retorna erro global
if [ $BANDIT_STATUS -ne 0 ] || [ $TRIVY_STATUS -ne 0 ] || [ $GITLEAKS_STATUS -ne 0 ]; then
    echo "🚨 Falha detectada em um ou mais testes de segurança. Verifique os logs acima."
    exit 1
fi

echo "🎉 Todos os testes de segurança passaram com sucesso!"
exit 0
