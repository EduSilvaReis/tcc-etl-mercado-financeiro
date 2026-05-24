import logging
from extract import MarketDataExtractor
from transform import DataTransformer
from load import DataLoader

# Lista padrão de ativos caso o banco de dados esteja inacessível (Fallback)
DEFAULT_TICKERS = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA']

def run_pipeline():
    logging.info("--- INICIANDO PIPELINE DE ETL FINANCEIRO ---")
    
    # 1. Inicializa o Carregador e busca ativos cadastrados no SQL
    loader = DataLoader()
    ativos_map = loader.get_asset_mapping() 
    
    # --- TRAVA DE SEGURANÇA ---
    if not ativos_map:
        logging.warning("Aviso: Banco de dados indisponível ou vazio. Ativando Modo de Segurança (Apenas CSV).")
        # Cria um dicionário falso mapeando os ativos padrão para IDs sequenciais 
        ativos_map = {ticker: idx for idx, ticker in enumerate(DEFAULT_TICKERS, start=1)}
    else:
        logging.info(f"{len(ativos_map)} ativos carregados do banco de dados com sucesso.")

    # 2. Extração
    tickers = list(ativos_map.keys())
    extractor = MarketDataExtractor(tickers)
    dados_brutos = extractor.fetch_data(period="5d") # Pegando os últimos 5 dias para teste

    # 3. Transformação
    transformer = DataTransformer(ativos_map)
    dados_transformados = transformer.transform(dados_brutos)

    # 4. Carga Final
    if not dados_transformados.empty:
        loader.load_fato(dados_transformados)
        logging.info("ETL Finalizado com sucesso!")
    else:
        logging.warning("Sem dados novos para carregar.")

if __name__ == "__main__":
    # Configuração básica de log para exibir no terminal
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    run_pipeline()