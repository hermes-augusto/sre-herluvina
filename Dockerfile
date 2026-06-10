# Dockerfile
#
# Riscos:
# 1. Ausência de ca-certificates ou bibliotecas OpenSSL que impeçam a extensão httpfs do DuckDB de se conectar ao MinIO via HTTPS local se configurado.
# 2. Execução de processos como usuário ROOT que pode expor vulnerabilidades de segurança se arquivos montados forem compartilhados no host.
# 3. Cache persistente de pacotes pip inflando desnecessariamente o tamanho da imagem Docker em ambiente local de desenvolvimento.
#
# Ambiguidades:
# 1. Se a imagem slim de base possui git instalado, necessário para que o dbt instale pacotes externos (ex: dbt-utils).
# 2. Se o timezone do container deve ser explicitamente sincronizado com o host local para consistência de logs do cron.

FROM python:3.11-slim

# Instala dependências de compilação básicas e utilitários de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /app/certs && chmod 777 /app/certs

# Copia e instala dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expõe as portas padrão da aplicação (8501 para Streamlit)
EXPOSE 8501

# Por padrão, mantém o container rodando no aguardo de comandos CLI
CMD ["tail", "-f", "/dev/null"]
