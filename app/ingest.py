#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# app/ingest.py
#
# Riscos:
# 1. Falha de conexão com o MinIO se o container de armazenamento não estiver ativo ou a rede estiver instável.
# 2. Ausência dos arquivos CSV originais no diretório de dados montado no container (/app/data).
# 3. Falha de escrita no MinIO por falta de espaço de armazenamento no volume local do Docker.
#
# Ambiguidades:
# 1. Se a política de ingestão deve ser sempre incremental ou se deve substituir os arquivos brutos atuais a cada carga diária.
# 2. Se o pipeline deve abortar completamente se apenas um dos arquivos de dados falhar no upload, ou se deve fazer upload parcial.

import os
import sys
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, EndpointConnectionError


def main():
    print("=== [INGESTÃO] Iniciando processo de ingestão local no MinIO ===")

    # Configurações de conexão
    endpoint_url = os.getenv("AWS_S3_ENDPOINT", "http://minio:9000")
    if not endpoint_url.startswith("http"):
        endpoint_url = f"http://{endpoint_url}"

    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not access_key or not secret_key:
        print(
            "[ERRO] Credenciais S3/MinIO (AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY) não estão configuradas no ambiente."
        )
        sys.exit(1)

    bucket_name = "northwind-raw"

    files_to_upload = {
        "northwind_orders.csv": "/app/data/northwind_orders.csv",
        "northwind_order_details.csv": "/app/data/northwind_order_details.csv",
    }

    # Inicializa cliente boto3
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar o cliente S3: {e}")
        sys.exit(1)

    # Garante existência do bucket
    try:
        print(
            f"[INGESTÃO] Verificando bucket '{bucket_name}' no endpoint {endpoint_url}..."
        )
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"[INGESTÃO] Bucket '{bucket_name}' já existe.")
        except Exception:
            s3.create_bucket(Bucket=bucket_name)
            print(f"[INGESTÃO] Bucket '{bucket_name}' criado com sucesso.")
    except EndpointConnectionError as e:
        print(f"[ERRO] Falha de conexão com o MinIO em {endpoint_url}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] Falha ao gerenciar o bucket no MinIO: {e}")
        sys.exit(1)

    # Upload dos arquivos CSV
    for s3_key, file_path in files_to_upload.items():
        if not os.path.exists(file_path):
            print(f"[ERRO] Arquivo de origem não encontrado: {file_path}")
            sys.exit(1)

        try:
            print(
                f"[INGESTÃO] Fazendo upload de {file_path} para s3://{bucket_name}/{s3_key}..."
            )
            s3.upload_file(file_path, bucket_name, s3_key)
            print(f"[INGESTÃO] Upload de '{s3_key}' concluído.")
        except Exception as e:
            print(f"[ERRO] Falha no upload de '{s3_key}': {e}")
            sys.exit(1)

    print("=== [INGESTÃO] Processo finalizado com sucesso! ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
