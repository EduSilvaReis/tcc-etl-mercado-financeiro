import logging

class FundamentalAnalyzer:
    """
    Motor de Análise Fundamentalista.
    Responsável por aplicar as regras de Benjamin Graham e Luiz Barsi
    para encontrar ativos descontados e boas pagadoras de dividendos.
    """
    def __init__(self):
        # Parâmetros do Investidor Defensivo (Graham)
        self.graham_max_pl = 15.0
        self.graham_max_pvp = 1.5
        self.graham_min_liquidez = 2.0
        
        # Parâmetros de Renda Passiva (Barsi)
        self.barsi_min_dy = 0.06 # Mínimo de 6% de Dividend Yield ao ano

    def calcular_sinais(self, fundamentos: dict) -> dict:
        """
        Recebe o dicionário de fundamentos da API e retorna os vereditos.
        """
        if not fundamentos:
            logging.warning("Sem dados fundamentalistas para analisar.")
            return {"Sinal_Graham": "DADOS_INSUFICIENTES", "Sinal_Barsi": "DADOS_INSUFICIENTES"}

        p_vp = fundamentos.get("P_VP")
        p_l = fundamentos.get("P_L")
        liquidez = fundamentos.get("Liquidez_Corrente")
        dy = fundamentos.get("Dividend_Yield")

        # -------------------------------------------------------------
        # 1. O Robô de Benjamin Graham (Margem de Segurança)
        # -------------------------------------------------------------
        sinal_graham = "REPROVADO"
        
        # Cenário A: É uma Ação (Possui P/L e Liquidez Corrente)
        if p_vp is not None and p_l is not None and liquidez is not None:
            if (0 < p_l < self.graham_max_pl) and (0 < p_vp <= self.graham_max_pvp) and (liquidez >= self.graham_min_liquidez):
                sinal_graham = "COMPRA"
            elif p_vp > 2.0 or p_l > 25.0:
                sinal_graham = "ALERTA_CARO"
                
        # Cenário B: É um FII ou ETF (Não possui P/L, avaliamos apenas pelo P/VP)
        elif p_vp is not None and p_l is None:
            if 0 < p_vp <= 1.05: # FIIs raramente ficam abaixo de 1.0, 1.05 é o limite do aceitável
                sinal_graham = "COMPRA_FII"
            elif p_vp > 1.10:
                sinal_graham = "ALERTA_CARO"

        # -------------------------------------------------------------
        # 2. O Robô de Luiz Barsi (Foco em Renda Passiva / Preço Teto)
        # -------------------------------------------------------------
        sinal_barsi = "REPROVADO"
        
        if dy is not None:
            if dy >= self.barsi_min_dy:
                sinal_barsi = "COMPRA"
            elif dy < 0.02: # Paga menos de 2% ao ano
                sinal_barsi = "ALERTA_BAIXA_RENDA"

        # Empacotar e retornar para o banco de dados
        return {
            "Sinal_Graham": sinal_graham,
            "Sinal_Barsi": sinal_barsi
        }