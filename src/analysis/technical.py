import pandas as pd
import numpy as np
import logging

class TechnicalAnalyzer:
    """
    Motor de Análise Quantitativa e Técnica.
    Responsável por calcular Tendências, Volatilidade, Força de Rompimento e Stop Loss.
    """
    def __init__(self):
        # Janelas de tempo configuráveis (em dias úteis)
        self.janela_curta = 20
        self.janela_media = 50
        self.janela_longa = 200
        self.janela_volatilidade = 30
        self.janela_atr = 14

    def calcular_sinais(self, df: pd.DataFrame) -> dict:
        """
        Recebe um DataFrame histórico (OHLCV) e calcula os indicadores para o dia mais recente.
        """
        if df is None or df.empty or len(df) < self.janela_longa:
            logging.warning("Dados insuficientes para calcular a MM200.")
            return {}

        # Criar uma cópia para não alterar o DataFrame original e garantir a ordem cronológica
        df = df.copy()
        df.sort_values('Date', inplace=True)

        # 1. Identificação de Tendências (Médias Móveis Simples)
        df['MMS_20'] = df['Close'].rolling(window=self.janela_curta).mean()
        df['MMS_50'] = df['Close'].rolling(window=self.janela_media).mean()
        df['MMS_200'] = df['Close'].rolling(window=self.janela_longa).mean()

        # 2. Análise de Volume (O combustível do mercado)
        df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
        # Se o volume atual for maior que a média, retorna 1, senão 0
        df['Volume_Acima_Media'] = np.where(df['Volume'] > df['Volume_MA_20'], 1, 0)

        # 3. Gerenciamento de Risco: Volatilidade (Desvio padrão de 30 dias)
        # Calcula a variação percentual dia após dia
        df['Retorno_Diario'] = df['Close'].pct_change()
        # Calcula o desvio padrão e multiplica por 100 para ficar em percentagem (ex: 2.5%)
        df['Volatilidade_30D'] = df['Retorno_Diario'].rolling(window=self.janela_volatilidade).std() * 100

        # 4. Gerenciamento de Risco: ATR (Average True Range) para Stop Loss
        # O TR (True Range) é o maior valor absoluto entre:
        # A oscilação de hoje (High - Low) ou a distância entre ontem e hoje (High - Prev_Close)
        df['Prev_Close'] = df['Close'].shift(1)
        df['TR'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Prev_Close']),
                abs(df['Low'] - df['Prev_Close'])
            )
        )
        # O ATR suaviza esse "ruído" numa média de 14 dias
        df['ATR_14D'] = df['TR'].rolling(window=self.janela_atr).mean()

        # -------------------------------------------------------------
        # EXTRACÃO DOS SINAIS PARA O DIA ATUAL (A última linha do DataFrame)
        # -------------------------------------------------------------
        ultimo_dia = df.iloc[-1]
        dia_anterior = df.iloc[-2]

        # Veredito 1: Tendência Macro (Preço está acima da média dos grandes institucionais?)
        tendencia_macro = "Alta" if ultimo_dia['Close'] > ultimo_dia['MMS_200'] else "Baixa"

        # Veredito 2: Cruzamento de Oportunidade (A Curta cruzou a Média hoje?)
        cruzamento = "Neutro"
        if (ultimo_dia['MMS_20'] > ultimo_dia['MMS_50']) and (dia_anterior['MMS_20'] <= dia_anterior['MMS_50']):
            cruzamento = "Compra"
        elif (ultimo_dia['MMS_20'] < ultimo_dia['MMS_50']) and (dia_anterior['MMS_20'] >= dia_anterior['MMS_50']):
            cruzamento = "Venda"

        # Veredito 3: Stop Loss Matemático (Proteção)
        # Se comprar agora, onde deve ficar a ordem de fuga para não perder o património?
        stop_loss = ultimo_dia['Close'] - (2 * ultimo_dia['ATR_14D'])

        # Empacotar tudo para o banco de dados
        return {
            "Tendencia_Macro": tendencia_macro,
            "Cruzamento_Medias": cruzamento,
            "Volume_Acima_Media": int(ultimo_dia['Volume_Acima_Media']),
            "Volatilidade_30D": round(ultimo_dia['Volatilidade_30D'], 2),
            "ATR_14D": round(ultimo_dia['ATR_14D'], 2),
            "Preco_Stop_Loss": round(stop_loss, 2)
        }