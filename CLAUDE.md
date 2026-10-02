# CLAUDE.md

Contexto para o Claude Code trabalhar neste repositório. Leia este arquivo inteiro antes de qualquer tarefa.

## Sobre o projeto

Projeto pessoal de Eduardo Silva dos Reis, originado do TCC de Engenharia da Computação
(Centro Universitário Jorge Amado, 2026), já entregue e aprovado. Agora evolui como projeto
pessoal e portfólio público. Pipeline ETL de dados do mercado financeiro brasileiro (B3) com uma camada de inteligência para
seleção de ativos e análise de carteira.

- **Regras de negócio, métricas e fórmulas de investimento:** `docs/Base_Conhecimento_Investimentos.md`.
  Consulte esse arquivo antes de implementar ou alterar qualquer lógica de análise
  (fundamentalista, técnica, FIIs, carteira, risco).
- Idioma do projeto: **português** (comentários, logs, mensagens de commit, documentação).
- Ambiente: **Windows**, PowerShell, Python 3.13 em `venv/`. O caminho do projeto tem espaços e
  acentos (`OneDrive\Área de Trabalho\...`), então sempre use aspas em caminhos.

## Arquitetura

```
src/
  extract.py              # MarketDataExtractor: yf.download de vários tickers (MultiIndex)
  transform.py            # DataTransformer: stack, renomeia colunas, mapeia Ticker -> Id_Ativo, remove nulos
  load.py                 # DataLoader: backup CSV + carga incremental no SQL Server
  main.py                 # Orquestrador do ETL (extract -> transform -> load)
  main_intelligence.py    # Orquestrador da análise (provider -> técnica + fundamentalista -> veredito)
  interfaces/data_provider.py  # DataProviderInterface (ABC, padrão Adapter)
  providers/yahoo_provider.py  # Implementação via yfinance
  providers/mt5_provider.py    # VAZIO - será implementado (MetaTrader 5)
  analysis/technical.py        # TechnicalAnalyzer: MMS 20/50/200, volume, volatilidade, ATR, stop loss
  analysis/fundamental.py      # FundamentalAnalyzer: filtros Graham (P/L, P/VP, liquidez) e Barsi (DY)
  alerts/email_sender.py       # VAZIO - será implementado (alertas por e-mail)
sql/create_tables.sql     # DDL do DW MercadoFinanceiroDW (Star Schema) + seed de Dim_Ativo
data/                     # Backup CSV da última carga (não versionar dados)
executar_etl.bat          # Execução agendada via Agendador de Tarefas do Windows
```

### Banco de dados (SQL Server, `MercadoFinanceiroDW`)

- `Dim_Ativo` (Id_Ativo, Ticker UNIQUE, Nome_Empresa, Setor_Atuacao, Data_Inclusao). Tickers no formato Yahoo (`PETR4.SA`).
- `Fato_Cotacao` (Id_Cotacao, Id_Ativo FK, Data_Pregao, Preco_Abertura/Maxima/Minima/Fechamento/Fechamento_Ajustado,
  Volume_Negociado, Data_Carga). UNIQUE (Id_Ativo, Data_Pregao) garante idempotência.
- Conexão: ODBC Driver 17, `Trusted_Connection=yes` (autenticação Windows).
- Qualquer mudança de esquema deve ser refletida em `sql/create_tables.sql`.

### Contratos entre módulos

- `transform.py` entrega as colunas: `Data, Asset_ID, Open, High, Low, Close, Adj_Close, Volume`.
- `load.py` renomeia para os nomes do banco (`Data -> Data_Pregao`, `Asset_ID -> Id_Ativo`, etc.).
- Providers devolvem DataFrame com `Date, Open, High, Low, Close, Volume` (sem fuso horário) e
  dicionário de fundamentos com `P_VP, P_L, ROE, Margem_Liquida, Liquidez_Corrente, Dividend_Yield`.
- Atenção: o ETL usa a coluna `Data`; a camada de análise usa `Date`. Não misture sem converter.

## Como executar

```powershell
# Ativar o ambiente
.\venv\Scripts\Activate.ps1

# ETL (imports relativos à pasta src)
python src/main.py

# Inteligência (imports absolutos "from src. ..." -> rodar como módulo a partir da raiz)
python -m src.main_intelligence
```

- `.env` na raiz (nunca versionado): `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASS`.
  O README cita `DB_PASSWORD`, mas o código lê `DB_PASS`.
- Se o banco estiver indisponível, `main.py` entra em **Modo CSV** com `DEFAULT_TICKERS` e IDs fictícios.
- `requirements.txt` está em UTF-16. Ao editar, preserve o encoding ou converta conscientemente para UTF-8.

## Regras do projeto

### Segurança
- Credenciais **sempre** via `.env` + `os.getenv`, nunca no código, em logs ou em commits.
- Ao implementar `email_sender.py` e `mt5_provider.py`, criar variáveis no `.env`
  (`EMAIL_USER`, `EMAIL_PASSWORD`, `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`) e atualizar `.env.example`.
- O repositório é **público** (portfólio): tudo que for versionado, incluindo `docs/`, fica visível para qualquer pessoa.

### Princípios de análise (resumo da Base de Conhecimento)
- Pipeline de decisão: Macro -> Filtros de qualidade -> Valuation -> Margem de segurança ->
  Timing técnico -> Construção da carteira -> Monitoramento.
- **Análise técnica é só timing** (quando comprar), nunca critério de seleção (o que comprar).
- Separar **score de qualidade** e **score de preço**; preferir score multifatorial a um múltiplo isolado.
- Usar séries de 5 a 10 anos para métricas fundamentalistas, não só o último trimestre.
- Bancos, seguradoras e utilities têm critérios próprios (não usar liquidez corrente/EBITDA em bancos).
- FIIs: avaliar sem RMG, comparar com pares do mesmo segmento.
- Limites de Graham foram calibrados para os EUA dos anos 1970; adaptações para o Brasil são
  decisões de projeto e devem ser parametrizáveis e validadas por backtest.
- O sistema é educacional e **não emite recomendação de investimento**; mensagens e relatórios devem refletir isso.

### Estilo de código
- Classes com responsabilidade única; novos provedores implementam `DataProviderInterface`.
- `logging` em vez de `print`, mensagens em português.
- Funções de rede/banco tratam exceções e retornam estruturas vazias (`pd.DataFrame()`, `{}`) em vez de quebrar o pipeline.
- Parâmetros de estratégia (janelas, limites de P/L, DY etc.) ficam no `__init__` ou em configuração, nunca soltos no meio da lógica.
- Comentários didáticos são bem-vindos: o projeto também serve como portfólio.

## Pendências e pontos de atenção conhecidos

- `main_intelligence.py`: conexão ao banco comentada, ativos fixos de teste e INSERT em
  `fato_sinal_investimento` ainda não implementado (a tabela também não existe no DDL).
- `load.py`: a carga incremental usa o `MAX(Data_Pregao)` global da tabela, não por ativo.
  Ativos novos ou com atraso podem ter dados ignorados.
- `load.py` lê `DB_USER`/`DB_PASS`, mas a conexão usa autenticação Windows (credenciais não são usadas).
- `main.py` busca só `period="5d"` (modo de teste).
- Estilos de import diferentes entre `main.py` (relativo a `src/`) e `main_intelligence.py` (`from src. ...`).
- `fundamental.py`: verificar a escala do `dividendYield` retornado pelo yfinance (decimal x percentual)
  antes de comparar com `barsi_min_dy = 0.06`.
- `technical.py` exige pelo menos 200 pregões para calcular a MM200.
- Documentação desatualizada: o `README.md` ainda trata o projeto como TCC em andamento e traz os
  placeholders `SEU-USUARIO/NOME-DO-REPOSITORIO` no comando de clone. Atualizar para a fase de projeto pessoal.

## Fluxo de Git

```powershell
git status
git add .
git commit -m "mensagem em português, descritiva"
git pull origin main   # se o push for rejeitado
git push origin main
```

Nunca usar `git push --force` na `main`. Conferir com `git status` que `.env`, `venv/` e `__pycache__/` não estão sendo incluídos.