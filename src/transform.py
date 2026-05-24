import pandas as pd
import logging

class DataTransformer:
    def __init__(self, asset_mapping: dict):
        self.asset_mapping = asset_mapping

    def transform(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        try:
            logging.info("Iniciando a transformação dos dados...")

            # 1. 'Derreter' o dataframe
            df_stacked = df_raw.stack(level=1, future_stack=True).reset_index()

            # 2. Padronizar nomes de colunas dinamicamente
            # O Yahoo Finance pode chamar o index de 'Date' ou 'Datetime'
            if 'Date' in df_stacked.columns:
                df_stacked.rename(columns={'Date': 'Data'}, inplace=True)
            elif 'Datetime' in df_stacked.columns:
                df_stacked.rename(columns={'Datetime': 'Data'}, inplace=True)
            
            # Renomear a coluna de Tickers gerada pelo stack
            if 'level_1' in df_stacked.columns:
                df_stacked.rename(columns={'level_1': 'Ticker'}, inplace=True)

            # Limpar espaços nos nomes ('Adj Close' -> 'Adj_Close')
            df_stacked.columns = [c.replace(' ', '_') for c in df_stacked.columns]

            # 3. Mapear Ticker para ID do Banco
            df_stacked['Asset_ID'] = df_stacked['Ticker'].map(self.asset_mapping)

            # 4. LIMPEZA CRÍTICA (Evita os erros de NULL no SQL)
            # Removemos linhas onde o Ativo não foi mapeado OU o Preço veio vazio (Falhas da API)
            df_stacked.dropna(subset=['Asset_ID', 'Close'], inplace=True)
            
            # 5. Filtrar apenas as colunas que o load.py espera
            colunas_obrigatorias = ['Data', 'Asset_ID', 'Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume']
            colunas_finais = [c for c in colunas_obrigatorias if c in df_stacked.columns]

            df_final = df_stacked[colunas_finais]
            logging.info(f"Transformação concluída. {len(df_final)} linhas validadas geradas.")
            
            return df_final

        except Exception as e:
            logging.error(f"Erro na transformação: {e}")
            return pd.DataFrame()