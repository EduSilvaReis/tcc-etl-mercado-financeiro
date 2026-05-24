# 📈 Pipeline de ETL Automatizado - Mercado Financeiro

Este repositório contém o código-fonte desenvolvido para o Trabalho de Conclusão de Curso (TCC) em **Engenharia da Computação** pelo Centro Universitário Jorge Amado (UJ).

O projeto consiste em um pipeline de **Extração, Transformação e Carga (ETL)** totalmente automatizado, focado na coleta de dados de ativos do mercado financeiro, garantindo a integridade, resiliência e armazenamento em um banco de dados relacional.

## 🛠️ Arquitetura e Tecnologias

A solução adota uma arquitetura *code-first* e foi construída utilizando:
* **Linguagem:** Python 3.10+
* **Bibliotecas Principais:** `pandas` (Data Cleansing e manipulação em memória), `yfinance` (Consumo da API do Yahoo Finance) e conectores de banco de dados (ex: `pyodbc` / `sqlalchemy`).
* **Banco de Dados:** Microsoft SQL Server (Modelagem Dimensional: *Star Schema*).
* **Orquestração:** Agendador de Tarefas do Windows + scripts `.bat`.

## 📂 Estrutura do Projeto

A modularização foi baseada em princípios de Engenharia de Software (Separação de Preocupações):

```text
ETL_MERCADO_FINANCEIRO/
├── data/                  # Diretório para os dumps temporários de backup (.csv)
├── sql/                   # Scripts SQL (DDL) de criação das tabelas (Dim_Ativo, Fato_Cotacao)
├── src/                   # Código-fonte principal
│   ├── extract.py         # Módulo de extração via API
│   ├── transform.py       # Módulo de limpeza e Data Quality (expurgo de nulos)
│   ├── load.py            # Módulo de carga (Idempotência e Carga Incremental)
│   └── main.py            # Orquestrador do pipeline
├── .env                   # Variáveis de ambiente (credenciais do BD - não versionado)
├── .gitignore             # Arquivos e pastas ignorados pelo Git
├── executar_etl.bat       # Script executável para automação no Windows
└── requirements.txt       # Dependências do projeto
```

# ⚙️ Como Configurar e Executar
## 1. Pré-requisitos
Python instalado na máquina.

Microsoft SQL Server configurado e rodando localmente ou em nuvem.

Driver ODBC para SQL Server instalado.

⚠️ IMPORTANTE: O Microsoft SQL Server é um requisito estrito para o funcionamento do pipeline ponta a ponta (Extração, Transformação e Carga). No entanto, o código possui um mecanismo de resiliência (fallback): caso o banco de dados esteja inacessível, o sistema extrairá uma lista padrão de ativos e funcionará em "Modo CSV", gerando apenas o backup local na pasta data/ para garantir que os dados não sejam perdidos.

## 2. Configuração do Ambiente
Clone o repositório e instale as dependências:

Clone o repositório
git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)

Acesse a pasta do projeto
cd NOME-DO-REPOSITORIO

Crie e ative o ambiente virtual
python -m venv venv
source venv/Scripts/activate  # No Windows

Instale as bibliotecas necessárias
pip install -r requirements.txt

## 3. Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto (este arquivo é ignorado pelo Git por segurança) e adicione as credenciais do seu banco de dados:
DB_SERVER=localhost
DB_NAME=NomeDoSeuBanco
DB_USER=SeuUsuario
DB_PASSWORD=SuaSenha

## 4. Execução Manual
Para rodar o pipeline pelo terminal e visualizar os logs de execução:
```Text
python src/main.py
```

## 5. Execução Automatizada
O projeto conta com o script executar_etl.bat. Ele foi desenhado para ser acoplado ao Agendador de Tarefas do Windows (Task Scheduler), permitindo que o pipeline rode de forma autônoma (ex: diariamente após o fechamento do pregão), ativando o ambiente virtual automaticamente e registrando os resultados.

#🚀 O que o projeto gera?
Ao final da execução, o pipeline entrega os seguintes resultados:

Banco de Dados Relacional Atualizado: Insere os dados processados na tabela Fato_Cotacao do SQL Server. O processo utiliza Carga Incremental (Delta Load), consultando a última data inserida no banco e salvando apenas dados novos.

Idempotência Garantida: Tratamento de erros de Pattern Matching que evita duplicidade de chaves, garantindo que execuções repetidas não corrompam a base.

Backup Frio (Cold Backup): Um arquivo temporário .csv é gerado na pasta data/ criando uma trilha de auditoria local (Audit Trail) contra falhas de rede durante o insert.

Logs de Observabilidade: Feedback no terminal (ou arquivo de log) detalhando horários de extração, volume de linhas processadas e alertas de qualidade de dados.

Autor: Eduardo Silva dos Reis

Bacharelado em Engenharia da Computação - 2026
