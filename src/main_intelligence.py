import logging
import pyodbc # Ou a biblioteca que você usa para conectar ao SQL Server
from sqlalchemy import create_engine
from dotenv import load_dotenv
from src.providers.yahoo_provider import YahooFinanceProvider
from src.analysis.technical import TechnicalAnalyzer
from src.analysis.fundamental import FundamentalAnalyzer

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Iniciando Ciclo de Inteligência Financeira...")

    # 1. Instanciar componentes
    provider = YahooFinanceProvider()
    tech_analyzer = TechnicalAnalyzer()
    fund_analyzer = FundamentalAnalyzer()

    # 2. Conectar ao Banco de Dados (usando a sua lógica atual)
    # conn = pyodbc.connect(...) 
    # def __init__(self):
    #     self.server = os.getenv("DB_SERVER")
    #     self.database = os.getenv("DB_NAME")
    #     self.username = os.getenv("DB_USER")
    #     self.password = os.getenv("DB_PASS")
        
    #     connection_string = (
    #         f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    #         f"SERVER={self.server};"
    #         f"DATABASE={self.database};"
    #         "Trusted_Connection=yes;"
    #     )
        
    #     params = urllib.parse.quote_plus(connection_string)
    #     self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    
    # 3. Buscar ativos cadastrados (Exemplo de consulta)
    # ativos = conn.execute("SELECT Id_Ativo, Ticker FROM dim_ativo").fetchall()
    
    # Lista de teste (para você rodar e ver o resultado no console)
    ativos = [("PETR4.SA", 1), ("XPML11.SA", 5)] 

    for ticker, id_ativo in ativos:
        logging.info(f"Analisando: {ticker}")

        # A. Obter dados brutos
        df = provider.obter_precos_historicos(ticker, dias=300)
        fundamentos = provider.obter_dados_fundamentos(ticker)

        if df.empty:
            continue

        # B. Executar Análise Técnica
        sinais_tecnicos = tech_analyzer.calcular_sinais(df)

        # C. Executar Análise Fundamentalista
        sinais_fundamentais = fund_analyzer.calcular_sinais(fundamentos)

        # D. Consolidar e Decidir (O Veredito Final)
        recomendacao = "AGUARDAR"
        if sinais_tecnicos.get("Cruzamento_Medias") == "Compra" and sinais_fundamentais.get("Sinal_Graham") == "COMPRA":
            recomendacao = "COMPRA_FORTE"
        
        logging.info(f"Veredito para {ticker}: {recomendacao}")

        # E. TODO: INSERT na tabela fato_sinal_investimento
        # Aqui entra o seu código de Load (INSERT INTO fato_sinal_investimento ...)
        # passando: id_ativo, tendencia_macro, sinal_graham, etc.

    logging.info("Ciclo de Inteligência Financeira Finalizado com Sucesso.")

if __name__ == "__main__":
    main()