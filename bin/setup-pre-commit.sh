#!/bin/bash
# bin/setup-pre-commit.sh
#
# Riscos:
# 1. Falha de permissão ao tentar escrever ou tornar executável o arquivo .git/hooks/pre-commit no host.
# 2. Incompatibilidade com ganchos (hooks) pré-existentes de outras ferramentas (como husky ou python-pre-commit) sobrescrevendo o arquivo.
# 3. Desativação indevida do hook se o arquivo .gitleaks-disabled for criado acidentalmente no diretório de trabalho.
#
# Ambiguidades:
# 1. Se o script deve baixar automaticamente a imagem do docker gitleaks no momento do setup para otimizar o tempo do primeiro commit.
# 2. Se devemos registrar o arquivo .gitleaks-disabled no .gitignore para evitar que desenvolvedores o subam para o repositório principal.

set -e

HOOK_PATH=".git/hooks/pre-commit"

install_hook() {
    echo "=== [SETUP] Configurando Hook de Pré-Commit do Gitleaks ==="
    
    if [ ! -d ".git" ]; then
        echo "[ERRO] Diretório .git não encontrado. Certifique-se de executar este script na raiz do projeto."
        exit 1
    fi
    
    # Backup se o hook já existir e não for nosso
    if [ -f "$HOOK_PATH" ] && ! grep -q "Gitleaks" "$HOOK_PATH"; then
        echo "[INFO] Hook pré-existente encontrado. Fazendo backup para ${HOOK_PATH}.bak"
        cp "$HOOK_PATH" "${HOOK_PATH}.bak"
    fi
    
    # Escreve o hook
    cat << 'EOF' > "$HOOK_PATH"
#!/bin/bash
# .git/hooks/pre-commit
# Hook de pré-commit do Gitleaks (Gerenciado por setup-pre-commit.sh)

if [ -f .gitleaks-disabled ]; then
    echo "[Gitleaks] Hook desativado via arquivo .gitleaks-disabled. Pulando scan..."
    exit 0
fi

echo "[Gitleaks] Iniciando varredura de segredos pré-commit..."

# Tenta usar o binário local se estiver no PATH
if command -v gitleaks &> /dev/null; then
    gitleaks protect --verbose --redact --staged
    EXIT_CODE=$?
else
    # Se não houver gitleaks local, tenta executar via Docker container
    if command -v docker &> /dev/null; then
        echo "[Gitleaks] Binário local não encontrado. Executando via Docker container..."
        docker run --rm -v "$(pwd):/path" zricethezav/gitleaks:latest protect --source="/path" --config="/path/gitleaks.toml" --verbose --redact --staged
        EXIT_CODE=$?
    else
        echo "[Gitleaks] AVISO: Nem 'gitleaks' local nem 'docker' foram encontrados. Pulando varredura..."
        exit 0
    fi
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "[Gitleaks] ERRO: Vazamento de credencial ou segredo detectado!"
    echo "[Gitleaks] O commit foi cancelado. Remova as credenciais e tente novamente."
    exit 1
fi

echo "[Gitleaks] Sucesso: Nenhum segredo detectado."
exit 0
EOF

    chmod +x "$HOOK_PATH"
    echo "[SUCESSO] Hook do Gitleaks instalado com sucesso em $HOOK_PATH!"
}

uninstall_hook() {
    echo "=== [SETUP] Removendo Hook de Pré-Commit do Gitleaks ==="
    if [ -f "$HOOK_PATH" ]; then
        if grep -q "Gitleaks" "$HOOK_PATH"; then
            rm "$HOOK_PATH"
            echo "[SUCESSO] Hook do Gitleaks removido de $HOOK_PATH."
            
            # Restaura backup se existir
            if [ -f "${HOOK_PATH}.bak" ]; then
                mv "${HOOK_PATH}.bak" "$HOOK_PATH"
                echo "[INFO] Backup restaurado para $HOOK_PATH."
            fi
        else
            echo "[INFO] O hook atual em $HOOK_PATH não é o do Gitleaks. Nenhuma alteração feita."
        fi
    else
        echo "[INFO] Nenhum hook encontrado em $HOOK_PATH."
    fi
}

disable_hook() {
    touch .gitleaks-disabled
    echo "[SUCESSO] Hook desativado temporariamente. Arquivo .gitleaks-disabled criado."
}

enable_hook() {
    if [ -f .gitleaks-disabled ]; then
        rm .gitleaks-disabled
        echo "[SUCESSO] Hook reativado. Arquivo .gitleaks-disabled removido."
    else
        echo "[INFO] O hook já está ativo (arquivo .gitleaks-disabled não existe)."
    fi
}

# Tratamento dos argumentos da CLI
case "$1" in
    uninstall)
        uninstall_hook
        ;;
    disable)
        disable_hook
        ;;
    enable)
        enable_hook
        ;;
    install|*)
        install_hook
        ;;
esac
