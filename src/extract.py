import yfinance as yf
import pandas as pd
import logging
from typing import List

# Configuração de Logs para monitorar a saúde da extração
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MarketDataExtractor:
    """
    Classe responsável por interagir com a API do Yahoo Finance.
    Encapsula a lógica de requisição e tratamento de erros de rede.
    """
    def __init__(self, tickers: List[str]):
        self.tickers = tickers

    def fetch_data(self, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Extrai dados históricos dos ativos selecionados.
        :param period: Tempo de histórico (ex: '1mo', '1y', 'max')
        :param interval: Granularidade (ex: '1d', '1h')
        """
        try:
            logging.info(f"Iniciando extração para os ativos: {self.tickers}")
            
            # Download dos dados
            data = yf.download(
                tickers=self.tickers,
                period=period,
                interval=interval,
                group_by='column'
            )
            
            if data.empty:
                logging.warning("Atenção: A API retornou um DataFrame vazio.")
                return pd.DataFrame()
            
            logging.info("Extração concluída com sucesso!")
            return data
            
        except Exception as e:
            logging.error(f"Erro crítico durante a extração: {e}")
            return pd.DataFrame()

# # Pequeno teste local (pode apagar depois se quiser)
# if __name__ == "__main__":
#     test_tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
#     extractor = MarketDataExtractor(test_tickers)
#     df = extractor.fetch_data()
#     print(df.head())