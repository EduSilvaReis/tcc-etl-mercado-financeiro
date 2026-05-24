import os
import urllib
import logging
import pandas as pd
from datetime import datetime  # <-- Importação adicionada aqui
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

class DataLoader:
    def __init__(self):
        self.server = os.getenv("DB_SERVER")
        self.database = os.getenv("DB_NAME")
        self.username = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "Trusted_Connection=yes;"
        )
        
        params = urllib.parse.quote_plus(connection_string)
        self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
    def load_fato(self, df):
        try:
            mapping = {
                'Data': 'Data_Pregao',
                'Asset_ID': 'Id_Ativo',
                'Open': 'Preco_Abertura',
                'High': 'Preco_Maxima',
                'Low': 'Preco_Minima',
                'Close': 'Preco_Fechamento',
                'Adj_Close': 'Preco_Fechamento_Ajustado',
                'Volume': 'Volume_Negociado'
            }
            df_ready = df.rename(columns=mapping)
            
            
            # --- 1. BACKUP LOCAL EM CSV ---
            os.makedirs('data', exist_ok=True)
            
            # Criamos uma cópia exclusiva para o CSV para não afetar a tabela do SQL Server
            df_csv = df_ready.copy()
            
            # Cria a coluna com a data e hora exata da execução da automação
            df_csv['Data_Execucao_Automacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            csv_path = os.path.join('data', 'ultima_carga_cotacoes.csv')
            df_csv.to_csv(csv_path, index=False)
            logging.info(f"Backup local salvo com carimbo de data/hora em: {csv_path}")

            # --- 2. CARGA INCREMENTAL (O "Pulo do Gato") ---
            # Busca qual foi a última data registrada no banco
            max_date_query = "SELECT MAX(Data_Pregao) FROM Fato_Cotacao"
            max_date_db = pd.read_sql(max_date_query, self.engine).iloc[0, 0]

            # Se o banco não for vazio, filtra o DataFrame para manter SÓ dados novos
            if pd.notnull(max_date_db):
                df_ready = df_ready[df_ready['Data_Pregao'] > max_date_db]

            # Se não sobrou nenhum dado novo após o filtro, encerra a função
            if df_ready.empty:
                logging.warning("Todos os dados extraídos já constam no Banco de Dados. Nenhuma inserção necessária.")
                return

            # --- 3. INSERÇÃO NO BANCO ---
            logging.info(f"Enviando {len(df_ready)} registros NOVOS para Fato_Cotacao...")
            df_ready.to_sql('Fato_Cotacao', self.engine, if_exists='append', index=False)
            logging.info("Carga concluída com sucesso no SQL Server!")
            
        except Exception as e:
            error_msg = str(e)
            if any(term in error_msg for term in ["2627", "23000", "chave duplicada", "UNIQUE KEY"]):
                logging.warning("Aviso: Dados de hoje já existem no banco. Ignorando para evitar duplicidade.")
            else:
                logging.error(f"Erro crítico na carga SQL: {e}")


    def get_asset_mapping(self):
        try:
            query = "SELECT Ticker, Id_Ativo FROM Dim_Ativo"
            df = pd.read_sql(query, self.engine)
            return dict(zip(df['Ticker'], df['Id_Ativo']))
        except Exception as e:
            logging.error(f"Erro ao buscar ativos: {e}")
            return {}