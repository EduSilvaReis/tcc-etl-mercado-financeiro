import yfinance as yf
import pandas as pd
import logging
from typing import Dict, Any
from src.interfaces.data_provider import DataProviderInterface

# Configuração básica de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YahooFinanceProvider(DataProviderInterface):
    """
    Implementação concreta do provedor de dados utilizando a API do yfinance.
    """

    def obter_precos_historicos(self, ticker: str, dias: int) -> pd.DataFrame:
        logging.info(f"A obter histórico de {dias} dias para {ticker} via Yahoo Finance...")
        try:
            ativo = yf.Ticker(ticker)
            # O yfinance aceita períodos como '1mo', '1y', 'max'. 
            # Para sermos precisos com os dias, podemos usar 'max' e filtrar as últimas 'N' linhas
            df = ativo.history(period="max")
            
            if df.empty:
                logging.warning(f"Nenhum dado de preço encontrado para {ticker}.")
                return pd.DataFrame()

            # Limpar o DataFrame para manter apenas o necessário
            df = df.reset_index()
            # Garantir que o fuso horário da data é removido para não dar conflito com o SQL Server
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None) 
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Retornar apenas os últimos 'X' dias solicitados
            return df.tail(dias).copy()

        except Exception as e:
            logging.error(f"Erro ao buscar histórico de {ticker}: {e}")
            return pd.DataFrame()

    def obter_dados_fundamentos(self, ticker: str) -> Dict[str, Any]:
        logging.info(f"A obter fundamentos contábeis para {ticker} via Yahoo Finance...")
        try:
            ativo = yf.Ticker(ticker)
            info = ativo.info

            # Mapeamento inteligente usando .get() para evitar o erro 'KeyError' 
            # caso um FII não tenha Lucro ou uma ação não tenha Dividendos
            fundamentos = {
                "P_VP": info.get('priceToBook', None),
                "P_L": info.get('trailingPE', None),
                "ROE": info.get('returnOnEquity', None),
                "Margem_Liquida": info.get('profitMargins', None),
                "Liquidez_Corrente": info.get('currentRatio', None),
                "Dividend_Yield": info.get('dividendYield', None) # Retorna decimal (ex: 0.08 para 8%)
            }
            
            return fundamentos

        except Exception as e:
            logging.error(f"Erro ao buscar fundamentos de {ticker}: {e}")
            # Se falhar totalmente, retorna o dicionário com valores nulos para não quebrar a base de dados
            return {"P_VP": None, "P_L": None, "ROE": None, "Margem_Liquida": None, "Liquidez_Corrente": None, "Dividend_Yield": None}