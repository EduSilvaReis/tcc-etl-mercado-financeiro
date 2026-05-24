CREATE DATABASE MercadoFinanceiroDW;
GO

USE MercadoFinanceiroDW;
GO

-- ==========================================
-- DIMENSÃO: ATIVOS (Tabela de Domínio)
-- Objetivo: Armazenar os metadados e características descritivas dos ativos financeiros.
-- ==========================================
CREATE TABLE Dim_Ativo (
    -- IDENTITY(1,1): O SQL Server gerencia a criação do ID automaticamente (Auto-incremento).
    Id_Ativo INT IDENTITY(1,1) PRIMARY KEY,
    
    -- VARCHAR(10): Ocupa apenas o espaço dos caracteres digitados, otimizando o armazenamento no disco.
    Ticker VARCHAR(10) NOT NULL,
    Nome_Empresa VARCHAR(100) NULL,
    Setor_Atuacao VARCHAR(50) NULL,
    
    -- GETDATE(): Preenche automaticamente a data e hora do servidor no exato momento do cadastro.
    Data_Inclusao DATETIME DEFAULT GETDATE(),
    
    -- CONSTRAINT UNIQUE: Regra de integridade que impede a inserção de dois ativos com o mesmo Ticker.
    CONSTRAINT UQ_DimAtivo_Ticker UNIQUE (Ticker)
);
GO

-- ==========================================
-- FATO: COTAÇÕES (Tabela de Eventos/Série Temporal)
-- Objetivo: Armazenar os dados históricos capturados pela automação.
-- ==========================================
CREATE TABLE Fato_Cotacao (
    -- BIGINT: Usado pois tabelas fato crescem exponencialmente e podem estourar o limite numérico do INT comum.
    Id_Cotacao BIGINT IDENTITY(1,1) PRIMARY KEY,
    
    -- Chave Estrangeira (Foreign Key) para garantir relacionamento com a dimensão.
    Id_Ativo INT NOT NULL,
    Data_Pregao DATETIME NOT NULL, 
    
    -- DECIMAL(18, 4): Padrão da indústria financeira. 18 dígitos no total, com 4 casas decimais para alta precisão.
    Preco_Abertura DECIMAL(18, 4) NULL,
    Preco_Maxima DECIMAL(18, 4) NULL,
    Preco_Minima DECIMAL(18, 4) NULL,
    Preco_Fechamento DECIMAL(18, 4) NULL,
    Preco_Fechamento_Ajustado DECIMAL(18, 4) NULL,
    
    -- BIGINT: O volume negociado na bolsa (em R$) atinge a casa dos bilhões facilmente.
    Volume_Negociado BIGINT NULL,
    
    Data_Carga DATETIME DEFAULT GETDATE(),
    
    -- Restrição de Integridade Referencial: Impede que o Python cadastre uma cotação para um ID_Ativo inexistente.
    CONSTRAINT FK_FatoCotacao_DimAtivo FOREIGN KEY (Id_Ativo) 
        REFERENCES Dim_Ativo(Id_Ativo),
        
    -- Restrição de Idempotência: Garante que um mesmo ativo não tenha dados duplicados no mesmo dia.
    CONSTRAINT UQ_FatoCotacao_AtivoData UNIQUE (Id_Ativo, Data_Pregao)
);
GO

-- Índice Não-Clusterizado: Acelera as consultas da equipe de análise quando filtrarem relatórios por data.
CREATE NONCLUSTERED INDEX IX_FatoCotacao_DataPregao ON Fato_Cotacao(Data_Pregao);
GO

-- ==========================================
-- CARGA INICIAL (SEED DATA)
-- Objetivo: Popular a dimensão com os ativos que o robô de ETL irá monitorar.
-- ==========================================
INSERT INTO Dim_Ativo (Ticker, Nome_Empresa, Setor_Atuacao)
VALUES 
    ('PETR4.SA', 'Petrobras PN', 'Energia/Petróleo'),
    ('VALE3.SA', 'Vale S.A. ON', 'Mineração'),
    ('ITUB4.SA', 'Itaú Unibanco PN', 'Financeiro/Bancos'),
    ('WEGE3.SA', 'Weg ON', 'Bens Industriais'),
    ('HGLG11.SA', 'CGHG Logística FII', 'Imobiliário/Logística'),
    ('XPLG11.SA', 'XP Logística FII', 'Imobiliário/Logística'),
    ('KNRI11.SA', 'Kinea Renda Imobiliária FII', 'Imobiliário/Híbrido'),
    ('BOVA11.SA', 'iShares Ibovespa Index Fundo', 'Índice/Bolsa Brasileira'),
    ('IVVB11.SA', 'iShares S&P 500 Fundo Índice', 'Índice/Bolsa Americana'),
    ('AAPL34.SA', 'Apple Inc. BDR', 'Tecnologia'),
    ('GOGL34.SA', 'Alphabet Inc. (Google) BDR', 'Tecnologia');
GO