import logging
from extract import MarketDataExtractor
from transform import DataTransformer
from load import DataLoader

def run_pipeline():
    logging.info("--- INICIANDO PIPELINE DE ETL FINANCEIRO ---")
    
    # 1. Inicializa o Carregador e busca ativos cadastrados no SQL
    loader = DataLoader()
    ativos_map = loader.get_asset_mapping() # Puxa do banco: {'PETR4.SA': 1, ...}
    
    if not ativos_map:
        logging.error("Nenhum ativo encontrado na Dim_Ativo. Abortando.")
        return

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
    run_pipeline()