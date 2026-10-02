from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class DataProviderInterface(ABC):
    """
    Interface abstrata (Adapter Pattern).
    Define o contrato obrigatório para qualquer provedor de dados financeiros.
    """

    @abstractmethod
    def obter_precos_historicos(self, ticker: str, dias: int) -> pd.DataFrame:
        """
        Deve retornar um DataFrame do Pandas com os preços históricos.
        Colunas obrigatórias esperadas: ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        """
        pass

    @abstractmethod
    def obter_dados_fundamentos(self, ticker: str) -> Dict[str, Any]:
        """
        Deve retornar um dicionário com os múltiplos fundamentalistas da empresa/FII.
        Chaves esperadas: P_VP, P_L, ROE, Margem_Liquida, Liquidez_Corrente, Dividend_Yield.
        """
        pass