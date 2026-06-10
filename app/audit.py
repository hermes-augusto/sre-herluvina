#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# app/audit.py
#
# Riscos:
# 1. Falha ao acessar o banco DuckDB se ele estiver bloqueado em modo exclusivo por outro container durante a auditoria.
# 2. Contagem incorreta no CSV caso existam quebras de linha dentro de campos de texto quotados (contornado usando pandas).
# 3. Falsos positivos caso registros duplicados ou inconsistentes na origem transacional sejam intencionalmente filtrados na modelagem.
#
# Ambiguidades:
# 1. Se a falha na paridade quantitativa (ex: 1 registro a menos) deve resultar em falha dura do pipeline (código de saída 1) ou apenas em aviso.
# 2. Se a auditoria deve detalhar exatamente quais chaves de pedido (order_id) causaram a divergência na contagem de linhas.

import os
import sys
import pandas as pd
import duckdb


def main():
    print("=== [AUDITORIA] Iniciando reconciliação quantitativa de registros ===")

    csv_details_path = "/app/data/northwind_order_details.csv"
    db_path = os.getenv("DUCKDB_DATABASE_PATH", "/app/data/northwind.duckdb")

    # 1. Valida existência dos caminhos
    if not os.path.exists(csv_details_path):
        print(f"[ERRO] Arquivo CSV de detalhes não localizado: {csv_details_path}")
        sys.exit(1)
    if not os.path.exists(db_path):
        print(f"[ERRO] Arquivo do banco DuckDB não localizado: {db_path}")
        sys.exit(1)

    # 2. Conta linhas no CSV original usando pandas para garantir precisão
    try:
        df_csv = pd.read_csv(csv_details_path)
        csv_count = len(df_csv)
        print(f"[AUDITORIA] Registros lidos no CSV de origem: {csv_count}")
    except Exception as e:
        print(f"[ERRO] Falha ao ler o arquivo CSV para auditoria: {e}")
        sys.exit(1)

    # 3. Conta registros na tabela fato fct_order_items do DuckDB
    try:
        conn = duckdb.connect(db_path, read_only=True)
        db_res = conn.execute("select count(*) from fct_order_items").fetchone()
        db_count = db_res[0] if db_res else 0
        conn.close()
        print(
            f"[AUDITORIA] Registros persistidos na fato (fct_order_items): {db_count}"
        )
    except Exception as e:
        print(f"[ERRO] Falha ao consultar o banco DuckDB para auditoria: {e}")
        sys.exit(1)

    # 4. Compara e reconcilia os volumes
    if csv_count != db_count:
        print(
            f"[ALERT] DIVERGÊNCIA DETECTADA! Perda Silenciosa de Linhas! Origem: {csv_count} | Fato: {db_count}"
        )
        # Grava log de falha na auditoria (abre em modo leitura/escrita)
        try:
            conn = duckdb.connect(db_path, read_only=False)
            conn.execute("""
                create table if not exists audit_log (
                    timestamp timestamp default current_timestamp,
                    event_type varchar,
                    status varchar,
                    csv_rows integer,
                    db_rows integer,
                    description varchar
                )
            """)
            conn.execute(
                """
                insert into audit_log (event_type, status, csv_rows, db_rows, description)
                values ('PIPELINE_RUN', 'FAILURE', ?, ?, 'Reconciliação falhou devido a divergência quantitativa.')
            """,
                (csv_count, db_count),
            )
            conn.close()
        except Exception as write_err:
            print(f"[ERRO] Falha ao gravar falha na tabela audit_log: {write_err}")
        # Retorna erro conforme RNF-02 / TC-11
        sys.exit(1)

    # 5. Grava registro de auditoria com sucesso na base (abre em modo leitura/escrita)
    try:
        print("[AUDITORIA] Registrando auditoria com sucesso no DuckDB...")
        conn = duckdb.connect(db_path, read_only=False)
        conn.execute("""
            create table if not exists audit_log (
                timestamp timestamp default current_timestamp,
                event_type varchar,
                status varchar,
                csv_rows integer,
                db_rows integer,
                description varchar
            )
        """)
        conn.execute(
            """
            insert into audit_log (event_type, status, csv_rows, db_rows, description)
            values ('PIPELINE_RUN', 'SUCCESS', ?, ?, 'Reconciliação quantitativa realizada com 100% de paridade.')
        """,
            (csv_count, db_count),
        )
        conn.close()
        print("[AUDITORIA] Evento gravado na tabela 'audit_log'.")
    except Exception as e:
        print(f"[ERRO] Falha ao gravar log de auditoria no DuckDB: {e}")
        sys.exit(1)

    print("=== [AUDITORIA] Reconciliação concluída com sucesso (100% de paridade)! ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
