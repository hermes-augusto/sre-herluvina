#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# app/entrypoint.py
#
# Riscos:
# 1. Falha de boot se o binário do 'openssl' não estiver instalado no container e o SSL estiver ativo.
# 2. Permissões de escrita na pasta de certificados (/app/certs) negadas para o usuário non-root.
# 3. Processos zumbis se o Streamlit não for executado via os.execvp (reaproveitando o PID 1).
#
# Ambiguidades:
# 1. Se a pasta de certificados (/app/certs) deve ser persistida via volume ou gerada em memória a cada boot.
# 2. Se a expiração de 365 dias para o certificado autoassinado é aceitável para homologação local.

import os
import sys
import subprocess  # nosec B404
import shutil


def main():
    print("=== [BOOT] Inicializando entrypoint do Streamlit ===")

    enable_ssl = os.getenv("STREAMLIT_ENABLE_SSL", "false").lower() == "true"
    cert_dir = "/app/certs"
    cert_file = os.path.join(cert_dir, "cert.pem")
    key_file = os.path.join(cert_dir, "key.pem")

    # Comando base do Streamlit
    cmd = [
        "streamlit",
        "run",
        "app/main.py",
        "--server.port",
        "8501",
        "--server.address",
        "0.0.0.0",
    ]  # nosec B104

    if enable_ssl:
        print("[BOOT] SSL/TLS ativado via STREAMLIT_ENABLE_SSL=true.")

        # Garante diretório de certificados
        os.makedirs(cert_dir, exist_ok=True)

        # Gera chaves caso não existam
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            print(
                "[BOOT] Certificados não localizados. Gerando chaves autoassinadas via OpenSSL..."
            )

            # Verifica se openssl está instalado
            if not shutil.which("openssl"):
                print(
                    "[ERRO] Binário 'openssl' não encontrado. Instale o openssl ou desative o SSL."
                )
                sys.exit(1)

            try:
                subprocess.run(
                    [  # nosec B603 B607
                        "openssl",
                        "req",
                        "-x509",
                        "-newkey",
                        "rsa:4096",
                        "-keyout",
                        key_file,
                        "-out",
                        cert_file,
                        "-sha256",
                        "-days",
                        "365",
                        "-nodes",
                        "-subj",
                        "/CN=localhost",
                    ],
                    check=True,
                )
                print("[BOOT] Certificados SSL gerados com sucesso!")
            except subprocess.CalledProcessError as e:
                print(f"[ERRO] Falha ao gerar certificados OpenSSL: {e}")
                sys.exit(1)
        else:
            print("[BOOT] Certificados SSL existentes localizados.")

        # Adiciona chaves ao comando do Streamlit
        cmd.extend(
            [f"--server.sslCertFile={cert_file}", f"--server.sslKeyFile={key_file}"]
        )
    else:
        print("[BOOT] SSL/TLS desativado. Rodando em modo HTTP padrão.")

    print(f"[BOOT] Executando comando: {' '.join(cmd)}")

    # Substitui o processo atual (PID 1) pelo Streamlit para tratamento correto de sinais do Docker
    os.execvp(cmd[0], cmd)  # nosec B606


if __name__ == "__main__":
    main()
