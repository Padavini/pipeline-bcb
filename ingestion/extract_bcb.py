import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

# definição das séries do BCB (nome + código SGS)
SERIES = {
    "SELIC": 11,
    "IPCA": 433,
    "DOLAR": 1,
    "CDI": 12
}

def fetch_bcb_data(codigo_serie, data_inicial, data_final):
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"
        f"?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consumir API para série {codigo_serie}: {e}")
        return None
    
def transform_to_dataframe(data_json, nome_serie, codigo_serie):
    if not data_json:
        return pd.DataFrame()

    df = pd.DataFrame(data_json)

    # padronização de tipos
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # adicionando colunas
    df["nome_serie"] = nome_serie
    df["codigo_serie"] = codigo_serie
    df["data_carga"] = datetime.now()

    return df

def get_connection():
    load_dotenv()

    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER")
    port = os.getenv("DB_PORT", "1433")

    connection_string = (
        f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}"
        f"?driver={driver.replace(' ', '+')}"
        f"&TrustServerCertificate=yes"
    )

    try:
        engine = create_engine(connection_string)
        conn = engine.connect()
        return conn

    except Exception as e:
        print(f"Erro ao conectar no SQL Server: {e}")
        return None
    

def load_to_bronze(df, conn):
    if df.empty:
        return 0

    inserted_count = 0

    insert_sql = """
        INSERT INTO bronze_bcb_series (
            data,
            valor,
            nome_serie,
            codigo_serie,
            data_carga
        )
        SELECT
            :data,
            :valor,
            :nome_serie,
            :codigo_serie,
            :data_carga
        WHERE NOT EXISTS (
            SELECT 1
            FROM bronze_bcb_series
            WHERE codigo_serie = :codigo_serie
              AND data = :data
        )
    """

    try:
        for _, row in df.iterrows():
            result = conn.execute(
                text(insert_sql),
                {
                    "data": row["data"],
                    "valor": row["valor"],
                    "nome_serie": row["nome_serie"],
                    "codigo_serie": row["codigo_serie"],
                    "data_carga": row["data_carga"],
                }
            )

            inserted_count += result.rowcount

        conn.commit()
        return inserted_count

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir dados na bronze: {e}")
        return 0
    
def main():
    data_inicial = "01/01/2020"
    data_final = "31/12/2025"

    conn = get_connection()

    if conn is None:
        print("Pipeline encerrado: falha na conexão com o banco.")
        return

    total_inserido = 0

    for nome_serie, codigo_serie in SERIES.items():
        print(f"Processando série: {nome_serie}")

        data_json = fetch_bcb_data(
            codigo_serie=codigo_serie,
            data_inicial=data_inicial,
            data_final=data_final
        )

        df = transform_to_dataframe(
            data_json=data_json,
            nome_serie=nome_serie,
            codigo_serie=codigo_serie
        )

        qtd_inserida = load_to_bronze(df, conn)

        total_inserido += qtd_inserida

        print(f"{nome_serie}: {qtd_inserida} registros inseridos")

    conn.close()

    print(f"Pipeline finalizado. Total inserido: {total_inserido} registros.")


if __name__ == "__main__":
    main()