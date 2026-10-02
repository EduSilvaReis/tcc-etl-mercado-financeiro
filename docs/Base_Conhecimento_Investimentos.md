# Base de Conhecimento de Investimentos

**Projeto:** Software de pipeline, seleção de ativos e análise de carteira
**Autor do projeto:** Eduardo Reis · **Versão:** 1.0 · **Data:** 02/10/2026
**Fontes analisadas:** 10 documentos (livros clássicos, livro técnico CVM/APIMEC, relatório anual da Berkshire 2025, guias de FIIs e carteiras recomendadas Rico jun–jul/2026)

> **Como usar este documento.** Ele foi escrito para ficar anexado ao contexto do projeto. Cada seção traduz os ensinamentos das fontes em **regras, métricas e fórmulas implementáveis**. Marcadores usados: **[Fonte]** indica de onde vem o conceito; **[Implementação]** indica uma sugestão de como levar o conceito para o código (decisão de projeto, não citação do livro). Nada aqui é recomendação de investimento.

---

## 1. Mapa das fontes

| # | Documento | Tipo | O que aproveitar no software |
|---|---|---|---|
| 1 | *O Investidor Inteligente* — Benjamin Graham (com comentários de Jason Zweig) | Livro clássico | Critérios quantitativos de seleção (defensivo e empreendedor), margem de segurança, Sr. Mercado, alocação 25–75%, custo médio |
| 2 | *O Jeito Warren Buffett de Investir* — Robert Hagstrom | Livro | 12 princípios de Buffett, ROE, lucros do proprietário, regra do "um dólar", carteira concentrada, Kelly, finanças comportamentais |
| 3 | *Berkshire Hathaway — Relatório Anual 2025* (1ª carta de Greg Abel como CEO) | Relatório anual | Princípios de alocação de capital, balanço "fortaleza", recompra abaixo do valor intrínseco, histórico 1965–2025 |
| 4 | *Análise de Investimentos* — CVM / APIMEC Brasil (2ª ed., 2025) | Livro técnico | Análise técnica (tendência, suportes, médias, candles), análise fundamentalista (top-down, bottom-up, DRE, balanço, fluxo de caixa), FCD, Gordon, múltiplos, DuPont, SWOT, Markowitz/CAPM, ASG |
| 5 | *Pai Rico, Pai Pobre* — Robert Kiyosaki (ed. 20 anos) | Livro | Ativo × passivo, "pague-se primeiro", educação financeira, foco na coluna de ativos |
| 6 | *Introdução a Fundos de Investimento Imobiliário* (Network de Educação Financeira, ago/2023) | Apresentação | Estrutura, segmentos, IFIX, custos, tributação, riscos, glossário de FIIs |
| 7 | *Aprenda a Investir em Fundos Imobiliários* (e-book) | E-book | Métricas de FIIs (vacância, DY, P/VP, cap rate, m²), qualidade do ativo, gestão, RMG |
| 8 | *Smart Ações 5+* — Rico, 10/06/2026 | Carteira recomendada | Processo macro → fundamentos → técnico, carteira de 5–8 ações, rebalanceamento mensal |
| 9 | *Carteira Brasil ETFs — Seleção Moderada* — Rico, 03/07/2026 | Carteira recomendada | Alocação por classe via ETFs, duration-alvo, benchmark CDI |
| 10 | *Carteira Brasil ETFs — Seleção Conservadora* — Rico, 03/07/2026 | Carteira recomendada | Mesma metodologia, perfil conservador |

---

## 2. Filosofia central (o "núcleo" que o software deve respeitar)

1. **Investimento × especulação.** "Uma operação de investimento é aquela que, após análise profunda, promete segurança do principal e um retorno adequado. As operações que não atendem a essas exigências são especulativas." **[Graham]** → o software deve sempre exigir análise (dados) + proteção de capital + retorno adequado antes de sinalizar "compra".
2. **Ação é participação em um negócio.** Quem compra uma ação vira sócio. **[Graham, Buffett, CVM]** → a análise começa pelo negócio, não pelo gráfico.
3. **Margem de segurança.** Comprar bem abaixo do valor intrínseco torna desnecessária uma previsão precisa do futuro e protege contra erros de estimativa. **[Graham cap. 20; Buffett]** → todo preço justo calculado deve gerar um *desconto exigido* antes do sinal de compra.
4. **Sr. Mercado.** O mercado é um sócio bipolar que oferece preços todos os dias; seu trabalho é fornecer preços, o seu é decidir se eles são vantajosos. **[Graham cap. 8; Zweig; Hagstrom]** → quedas fortes de preço sem piora de fundamentos são oportunidades, não sinais de venda.
5. **Risco vem de não saber o que se está fazendo** (não da volatilidade). **[Buffett via Hagstrom]** → priorizar empresas previsíveis e compreensíveis; medir risco também por *drawdown* e qualidade do balanço, não só desvio-padrão.
6. **Longo prazo e juros compostos.** Buffett avalia resultados em médias de 5 anos; Berkshire "pensa em décadas". **[Hagstrom; Berkshire 2025]** → métricas devem usar séries de 5–10 anos, não o último trimestre.
7. **Qualidade + preço.** Um ótimo ativo comprado caro é um mau investimento ("banana orgânica a R$ 100/kg"). **[e-book FIIs; Buffett]** → separar sempre *score de qualidade* e *score de preço*.
8. **O maior inimigo do investidor costuma ser ele mesmo.** **[Graham/Zweig; Hagstrom cap. 6]** → regras automáticas e disciplinadas reduzem vieses comportamentais.

---

## 3. Arquitetura de decisão sugerida (pipeline)

A metodologia das carteiras Rico (Economia → Research Fundamentalista → Research Técnico) e do livro CVM (top-down + bottom-up) converge com Graham/Buffett no seguinte fluxo **[Implementação]**:

| Etapa | Pergunta | Fonte do conceito | Saída no software |
|---|---|---|---|
| 1. Macro (top-down) | Quais setores o cenário favorece? (juros, inflação, câmbio, PIB, política, fluxo estrangeiro) | CVM 4.2; Rico | Peso setorial / viés defensivo × cíclico |
| 2. Universo e filtros de qualidade | A empresa passa nos testes mínimos de solidez? | Graham cap. 14–15; Buffett | Lista elegível |
| 3. Valuation | Quanto vale? | CVM 4.4; Buffett; Graham cap. 11 | Preço justo (faixa) |
| 4. Margem de segurança | O preço está suficientemente abaixo do valor? | Graham cap. 20 | Upside / desconto |
| 5. Timing técnico | É um bom momento de entrada? | CVM cap. 2; Rico | Sinal de entrada/espera |
| 6. Construção da carteira | Quanto alocar em cada ativo/classe? | Graham; Hagstrom cap. 5; Markowitz; Rico ETFs | Pesos-alvo |
| 7. Monitoramento | O que mudou? Rebalancear? | Rico (revisão mensal); Graham | Alertas e rebalanceamento |

**Princípio de projeto:** a análise técnica entra **somente na etapa 5** (quando comprar), nunca como critério de seleção (o que comprar). Esse é exatamente o papel que a Rico dá a ela ("Research técnico: quando comprar").

---

## 4. Módulo Ações

### 4.1 Critérios do investidor defensivo (Graham, cap. 14)

| # | Critério original (EUA, 1972) | Regra sugerida para B3 **[Implementação]** | Dados necessários |
|---|---|---|---|
| 1 | Tamanho adequado (≥ US$ 100 mi de faturamento; ≥ US$ 50 mi de ativos em utilities) | Receita líquida anual mínima (ex.: ≥ R$ 1–2 bi) **e** liquidez média diária mínima (ex.: ≥ R$ 10 mi) | DFP, volume B3 |
| 2 | Condição financeira forte: ativo circulante ≥ 2× passivo circulante; dívida de LP ≤ capital de giro líquido. Utilities: dívida ≤ 2× patrimônio | Liquidez corrente ≥ 2,0 (industriais); Dív. LP ≤ AC − PC; utilities: Dívida/PL ≤ 2. Bancos/seguradoras: critério próprio (Basileia, solvência) | Balanço |
| 3 | Estabilidade de lucros: algum lucro em cada um dos últimos 10 anos | Lucro líquido > 0 nos últimos 10 anos | DFPs históricas |
| 4 | Histórico de dividendos: pagamentos ininterruptos por ≥ 20 anos | Proventos ininterruptos por ≥ 10 anos (mercado BR é mais jovem) | Histórico de proventos |
| 5 | Crescimento de lucros: +⅓ no LPA em 10 anos (médias trienais no início e no fim) | (média LPA últimos 3 anos) ÷ (média LPA de 10–8 anos atrás) ≥ 1,33 — corrigir pela inflação no Brasil | LPA histórico, IPCA |
| 6 | P/L moderado: preço ≤ 15× lucro médio dos últimos 3 anos | P/L(médio 3a) ≤ 15 — ajustar ao nível da Selic (ver 4.5) | Preço, LPA |
| 7 | P/VP moderado: ≤ 1,5; ou **P/L × P/VP ≤ 22,5** | Implementar a regra combinada: **Preço ≤ √(22,5 × LPA × VPA)** ("número de Graham") | LPA, VPA |

Outras regras de Graham para a parcela de ações do defensivo (cap. 5): **10 a 30 ações**; empresas grandes, conceituadas e financiadas de forma conservadora; histórico longo de dividendos; **preço ≤ 25× o lucro médio de 7 anos e ≤ 20× o lucro dos últimos 12 meses**.

### 4.2 Critérios do investidor empreendedor (Graham, cap. 15)

Ponto de partida de Graham: ações com **P/L < 10**, e então:

1. **Condição financeira:** ativo circulante ≥ 1,5× passivo circulante **e** dívida ≤ 110% do ativo circulante líquido (industriais).
2. **Estabilidade:** nenhum prejuízo nos últimos 5 anos.
3. **Dividendos:** algum dividendo atual.
4. **Crescimento:** lucro do último ano > lucro de ~5 anos atrás.
5. **Preço:** < 120% dos ativos tangíveis líquidos (P/VP tangível < 1,2).

Graham também testou "**net-nets**": comprar um grupo diversificado de ações negociadas **abaixo do ativo circulante líquido** (ativo circulante − passivo total, atribuindo valor zero aos ativos fixos), idealmente a **≤ ⅔ desse valor**. Funcionou de 1923 a 1957 em sua experiência. **[Implementação]** filtro raro, útil como "alerta de oportunidade profunda".

Dois métodos simples que, segundo Graham, deram resultados bons e consistentes: (a) ações de **P/L baixo entre empresas grandes** e (b) **cesta diversificada de net-nets**. Ele ressalta que testes com *um fator* isolado funcionam pior do que **combinações de critérios quantitativos** → o software deve usar um **score multifatorial**, não um único múltiplo.

### 4.3 Os 12 princípios de Buffett (Hagstrom) → métricas

| Grupo | Princípio | Como medir **[Implementação]** |
|---|---|---|
| Negócio | Simples e compreensível | Classificação setorial manual / lista de "círculo de competência" do usuário |
| | Histórico consistente de operações | Desvio-padrão baixo de receita, margem e ROE em 10 anos; sem prejuízos |
| | Perspectivas favoráveis a longo prazo | Margens e ROE estáveis/crescentes (sinal de vantagem competitiva — "fosso") |
| Gestão | Racionalidade (alocação de capital) | Teste do "um dólar" (abaixo); recompras abaixo do valor; payout coerente com o ROE |
| | Transparência | Qualidade de RI, ressalvas de auditoria, segmento de listagem (Novo Mercado) |
| | Resistência ao imperativo institucional | Evitar aquisições caras/diversificação sem lógica (histórico de M&A, goodwill crescente) |
| Financeiro | Foque no **ROE**, não no LPA | ROE = Lucro operacional ÷ PL (média 5 anos), excluindo ganhos/perdas não recorrentes |
| | ROE alto **sem alavancagem** | Comparar ROE com Dívida/PL; desconfiar de ROE alto sustentado só por dívida |
| | **Lucros do proprietário** | **LL + Depreciação/Amortização − Capex de manutenção − Δ capital de giro necessário** |
| | Margens de lucro altas | Margem líquida/operacional vs. pares do setor; tendência de custos |
| | **Premissa do "um dólar"** | Δ Valor de mercado (5 anos) ÷ Lucros retidos acumulados (5 anos) ≥ 1 |
| Mercado | Determine o valor | Fluxo de caixa descontado (John Burr Williams) |
| | Compre a preço atraente | Preço ≤ valor × (1 − margem de segurança) |

Observações de Buffett úteis para o código: avaliar em **médias de 5 anos**; o crescimento só cria valor quando o **retorno sobre o capital é acima da média** ("valor e crescimento se unem"); se o fluxo de caixa não for previsível, **não tente avaliar a empresa** (marcar como "não avaliável").

### 4.4 Valuation (CVM/APIMEC cap. 4; Buffett; Graham)

**Fluxo de Caixa Descontado (FCD)**

- Valor = Σ FC<sub>t</sub> / (1 + r)<sup>t</sup> + Valor na perpetuidade descontado.
- Perpetuidade (Gordon) = FC<sub>n+1</sub> / (r<sub>p</sub> − g<sub>p</sub>), com r<sub>p</sub> > g<sub>p</sub>. A perpetuidade costuma ser **parcela grande do valor total** — teste de sensibilidade obrigatório.
- Modelos em **2 estágios** (empresas em crescimento normal) e **3 estágios** (pequenas e médias longe da maturidade).
- Taxa de desconto: **WACC** = (E/V)·Ke + (D/V)·Kd·(1 − IR). Custo da dívida = juros pagos ÷ dívida (ex.: R$ 10 mi / R$ 100 mi = 10%).
- **CAPM:** Ke = Rf + β · [E(Rm) − Rf]. Exemplo do livro: Rf 10%, E(Rm) 15%, β 0,8 → Ke = 14%.
- Visão de Buffett: usar a taxa livre de risco de longo prazo e, em vez de prêmio por volatilidade, **exigir margem de segurança maior**; quando os juros estão anormalmente baixos, somar alguns pontos. **[Implementação]** No Brasil, usar NTN-B longa (juro real) + IPCA projetado como Rf.

**Modelo de Gordon (dividendos)**

- P<sub>justo</sub> = D<sub>1</sub> / (k − g). Só vale para empresas maduras, com crescimento constante e k > g. Útil para pagadoras de dividendos (bancos, utilities, seguradoras).

**Fórmula de crescimento de Graham (cap. 11)**

- **Valor = LPA normalizado × (8,5 + 2g)**, onde g = crescimento anual esperado (%) para 7–10 anos. Também serve ao inverso: descobrir o **crescimento implícito** no preço atual. **[Implementação]** Os parâmetros foram calibrados para juros dos EUA nos anos 1960–70; com a Selic brasileira muito mais alta, reduzir o múltiplo-base ou usar apenas como sinal relativo.

**Múltiplos** (sempre comparar com pares do setor e com o histórico da própria empresa — "nenhum indicador é suficiente isoladamente")

- **P/L** = Preço ÷ LPA. **Taxa de retorno (earnings yield)** = L/P × 100 (P/L 4 → 25% a.a.; payback de 4 anos).
- **EV/EBITDA**, com EV = valor de mercado + dívida líquida. Ex.: múltiplo histórico 5× e EBITDA projetado R$ 100 mi → EV justo R$ 500 mi → subtrair dívida líquida = valor de mercado justo.
- **P/VP**: cuidado — compara expectativa futura com patrimônio presente.
- **Análise DuPont**: ROE = Margem líquida × Giro do ativo × Alavancagem (Ativo/PL) → revela *de onde* vem o retorno.
- **SWOT/FOFA**: síntese qualitativa (forças/fraquezas = bottom-up; oportunidades/ameaças = top-down). Ex.: empresa muito alavancada (fraqueza) diante de alta de juros (ameaça).

### 4.5 Adaptações ao Brasil **[Implementação]**

- **Comparar o earnings yield com os juros.** Graham compara o retorno do lucro da ação com o rendimento dos títulos (margem de segurança de ações). Regra prática: só considerar "barata" a ação cujo **L/P supere o juro real da NTN-B + um prêmio**, ou cujo L/P seja comparável à taxa da renda fixa pós-fixada.
- **Inflação**: corrigir séries de lucro/LPA pelo IPCA antes de medir crescimento.
- **Setores especiais**: bancos e seguradoras não usam liquidez corrente/EBITDA; usar ROE, índice de Basileia, índice combinado (seguros), P/VP. Utilities usam regra própria de dívida (Graham já as separa).
- **Câmbio**: empresas exportadoras/endividadas em dólar — a variação cambial distorce DRE e balanço (exemplo do livro: dívida de US$ 150 mil passa de R$ 300 mil para R$ 450 mil com o dólar de 2 para 3). Verificar hedge.

### 4.6 Saúde financeira e demonstrações (CVM/APIMEC)

- **Balanço**: comparar pelo menos **3 anos** (art. 176, Lei 6.404/76). Ativos de curto prazo devem ser financiados por passivos de curto prazo; ativos de longo prazo por passivo de LP + PL. **Risco de liquidez**: dívida de curto prazo > caixa + geração de caixa esperada.
- **Capital de giro positivo** é sinal de empresa saudável (bebidas e programas de fidelidade recebem antes de pagar).
- **Endividamento**: não é bom nem ruim por si; avaliar se o custo da dívida é menor que o retorno exigido e se há geração de caixa para pagá-la. Exemplo do livro (31/03/2024): **CSN Dívida Líquida/EBITDA 3,13×** vs. **Ferbasa com caixa líquido de R$ 781,4 mi**.
- **DRE**: Receita bruta → deduções → receita líquida → CPV → lucro bruto → despesas operacionais → EBIT/EBITDA → IR → minoritários → lucro líquido. **Giro do ativo** = receita líquida ÷ ativo total.
- **Fluxo de caixa** (operacional, investimento, financiamento): a empresa é geradora ou consumidora de caixa?
- **Berkshire 2025** reforça: o lucro contábil (GAAP) oscila com ganhos/perdas de investimentos; o **lucro operacional** e o **caixa operacional** são as melhores medidas de desempenho anual. **[Implementação]** separar itens não recorrentes do lucro.

### 4.7 Análise técnica — camada de *timing* (CVM/APIMEC cap. 2; Rico)

**Princípios (Teoria de Dow):** o preço desconta tudo; o preço tem tendência; a história se repete. O próprio livro alerta: *"a análise técnica não é uma ciência"* e as regras têm muitas exceções.

| Conceito | Regra objetiva implementável |
|---|---|
| Tendência de alta | Sequência de **fundos ascendentes**; linha de tendência confirmada no **3º toque** |
| Tendência de baixa | Sequência de **topos descendentes** |
| Rompimento | Exigir **fechamento** além da linha; rompimento encerra a tendência mas não garante reversão (pode virar lateral) |
| Lateralidade | Topos e fundos no mesmo nível → **desligar sinais seguidores de tendência** |
| Suporte/Resistência | Força ∝ nº de toques e duração do nível |
| Média móvel simples × exponencial | MMS para ativos pouco voláteis; MME para voláteis |
| Preço × média | Compra quando o preço cruza a média para cima; venda para baixo. Muitos falsos sinais quando a média está horizontal |
| Média curta × longa | Cruzamento (ex.: 10 × 50 períodos) reduz falsos sinais, com atraso |
| **MM200** | A Rico usa repetidamente a **média de 200 períodos** como região de suporte relevante para entrada (ITUB4, ISAE4, MDNE3 em jun/2026) |
| Figuras de continuidade | Retângulo, bandeira, flâmula (projeção = altura do mastro), triângulos ascendente/descendente/simétrico (projeção = altura) |
| Figuras de reversão | OCO e OCO invertido (projeção = cabeça→pescoço), topo duplo "M", fundo duplo "W" — exigir tendência prévia clara |
| Candles | Martelo, enforcado (sombra inferior 2–3× o corpo), martelo invertido, estrela cadente, engolfo, harami, nuvem negra ("tempestade à vista", fechamento ≤ 50% do corpo anterior) |

**[Implementação]** Usar o técnico apenas para (a) adiar compras de ativos aprovados quando em tendência de baixa clara e (b) priorizar entradas próximas de suportes/MM200. Validar qualquer regra técnica com **backtest** (conceito do glossário Rico: "retornos passados não garantem retornos futuros").

---

## 5. Módulo Fundos Imobiliários (FIIs)

### 5.1 Estrutura e segmentos
- Condomínio **fechado** (não há resgate; liquidez via bolsa). Ticker XXXX11. Administrador/gestor; gestão ativa/passiva; mono/multiativo; prazo determinado/indeterminado.
- **Segmentos:** Tijolo (logística, shoppings/varejo, lajes corporativas, agências, hotéis, hospitais, residencial, educacional), **Papel/recebíveis** (CRI, LCI), **Fundos de fundos (FoF)**, **Desenvolvimento**, **Híbridos**.
- **IFIX**: índice de retorno total (cota + rendimentos) dos FIIs mais líquidos; benchmark do módulo.
- Obrigatório distribuir **≥ 95% do lucro (regime de caixa) por semestre**.

### 5.2 Métricas

| Métrica | Fórmula / definição | Leitura |
|---|---|---|
| **Dividend Yield 12m** | Σ rendimentos 12m ÷ cotação atual | Ex.: R$ 7,65/mês × 12 = R$ 91,80 ÷ R$ 1.275 = **7,2%**. Nunca analisar isolado |
| Yield on cost | Σ rendimentos 12m ÷ preço médio de compra | Acompanhar a renda da carteira do usuário |
| **P/VP** | Cotação ÷ (PL ÷ nº de cotas) | < 1 desconto (pode ser oportunidade **ou** problema estrutural); > 1 ágio |
| **Vacância física** | ABL vaga ÷ ABL total | Avaliar **histórico longo**, comparar com a região (ex.: HGJH11 ~12% vs. média SP > 25%; FMOF11 48%) |
| **Vacância financeira** | % da área que não gera renda (vaga ou em carência) | Mais fiel ao impacto no rendimento |
| **Cap rate** | Renda anual do imóvel ÷ valor do imóvel | Ex.: R$ 4,56 mi ÷ R$ 50 mi = **9,12%**. Cap rate alto costuma vir com mais risco/vacância |
| Valor do m² implícito | Valor de mercado do fundo ÷ ABL vs. laudo ÷ ABL | Ex.: laudo R$ 12.500/m² vs. bolsa R$ 7.500/m² = desconto |
| Aluguel/m² vs. região | Aluguel praticado ÷ m² | Muito acima do mercado = risco de revisional/saída |
| Taxas | Administração, gestão, performance (ex.: 0,8% a.a. adm; 0,2% gestão; 20% sobre o benchmark) | Taxas altas corroem rendimento |
| Liquidez | Volume médio diário | Filtro de entrada |
| Distribuição × resultado | Rendimento pago ÷ resultado recorrente | **> 1 de forma persistente = "queimando caixa" ou RMG** |

### 5.3 Qualidade e riscos
- **Qualidade do imóvel:** localização, padrão construtivo, demanda da região, diferenciais, vacância controlada.
- **Gestão:** histórico do gestor, alinhamento (ex.: redução de custos condominiais), prospecção de inquilinos.
- **Fundos de papel:** analisar cada CRI — devedor, indexador (CDI/IPCA/IGP-M), vencimento, garantias, **rating**, adimplência.
- **Contratos típicos** (≈5 anos, reajuste anual, revisional a cada 3 anos, multa de 3–6 aluguéis) × **atípicos** (≈10 anos, built-to-suit/sale-leaseback, multa = aluguéis restantes; maior previsibilidade, mas risco de reajuste negativo na renovação).
- **Riscos:** inadimplência/crédito, vacância, **mono-ativo/mono-inquilino**, oscilação de cotas, risco regulatório/tributário, gestão.
- **RMG (Renda Mínima Garantida):** rendimento pago pelo vendedor, temporário; ao acabar, o rendimento cai para o resultado real → **avaliar sempre pelo resultado real, sem RMG**.
- **Preço:** comparar com **pares do mesmo segmento** (ex.: dois fundos de shopping de mesmo padrão → escolher o de múltiplos mais baratos).
- A análise de risco **deve ser refeita periodicamente**.

### 5.4 Custos e tributação (conforme material de 2023 — **confirmar legislação vigente**)
- Rendimentos isentos de IR para pessoa física se: cotista < 10% das cotas, fundo com ≥ 50 cotistas (regra do material) e cotas negociadas exclusivamente em bolsa.
- Ganho de capital: **20%**, via DARF até o último dia útil do mês seguinte; prejuízos compensáveis; **sem isenção** por volume mensal de vendas.
- Emissões de cotas: direito de preferência proporcional; tickers de direitos terminam em 12, 13, 14, 15.

**[Implementação] Score de FII sugerido:** Qualidade (vacância histórica, diversificação de ativos/inquilinos, gestão, taxas, contratos) + Preço (P/VP vs. pares, DY real vs. pares e vs. NTN-B) + Sustentabilidade (distribuição ≤ resultado, sem RMG) + Liquidez.

---

## 6. Módulo Renda Fixa, ETFs e Alocação de Ativos

### 6.1 Metodologia das carteiras Rico de ETFs (jul/2026)
1. **Economia:** cenário macro gera premissas.
2. **Alocação:** retornos e volatilidades esperados por classe → alocação ótima por perfil.
3. **Research:** escolha dos ativos dentro de cada classe para maximizar retorno ajustado ao risco.

Características: somente ETFs da B3, **todos com proteção cambial (hedge)** (exceto o ouro GOLD11, escolhido para incluir exposição ao dólar), objetivo de **superar o CDI no longo prazo**, revisão no **3º dia útil de cada mês**, e pré-requisito de **reserva de emergência** antes de investir.

### 6.2 Composição por classe (03/07/2026)

| Classe | Conservadora | Moderada | ETFs usados |
|---|---|---|---|
| RF pós-fixada | **72,5%** | 35,5% | LFTX11 (30% só na cons.), LTBX11, NLFA11, GICP11 |
| RF inflação (IPCA+) | 12,5% | **34,0%** | XB3011 (NTN-B 2030), XB3511 (NTN-B 2035) |
| RF prefixada | 6,5% | 10,0% | PREX11 (IRF-M P2, ~2 anos) |
| RF global (hedge) | 2,5% | 2,5% | HGBR11 |
| Renda variável Brasil | — | 6,5% | DIVO11 (dividendos/IDIV) |
| Renda variável global (hedge) | 2,5% | 3,5% | SPXH11 (S&P 500) |
| Fundos listados (FIIs) | 3,5% | 4,0% | XFIX11 (IFIX-L) |
| Alternativos | — | 4,0% | GOLD11 (ouro), BCOM39 (commodities) |

**Regras de alocação extraídas (visão XP/Rico, jul/2026):** pós-fixado como pilar de carrego/liquidez, com **cautela em crédito privado** (sem concentração por setor ou emissor); prefixados com **duration curta**; inflação com **duration média ~6 anos**; RF global com **duration ≤ 2 anos**; ações Brasil com foco em **qualidade, geração de caixa, baixa alavancagem e lucros em alta**; FIIs construtivos, com **reinvestimento dos rendimentos**.

Durations dos ETFs: LTBX11 1,2 a · NLFA11 2,2 a · GICP11 3,5 a · XB3011 4 a · XB3511 7 a · PREX11 2 a. Vantagens tributárias citadas: IR de 15% fixo em alguns ETFs de RF, sem come-cotas, IR retido na fonte.

### 6.3 Alocação ações × renda fixa (Graham)
- Manter **entre 25% e 75% em ações** (e o inverso em títulos); padrão **50/50**, rebalanceando quando a proporção se desviar (ex.: banda de ±5 p.p.). Aumentar ações apenas quando o mercado estiver claramente barato; reduzir quando estiver caro.
- **Custo médio em dólares (DCA):** aportar valores fixos periodicamente, independentemente do preço.

**[Implementação]** Perfis no software: *Conservador*, *Moderado*, *Arrojado* com pesos-alvo por classe (as tabelas Rico servem de referência inicial) e bandas de rebalanceamento.

---

## 7. Construção e gestão de carteira

| Tema | Ensinamento | Fonte |
|---|---|---|
| Diversificação "defensiva" | **10 a 30 ações**, grandes e conservadoramente financiadas | Graham |
| Carteira concentrada | Buffett: carteira ideal com **até ~10 ações**, ≥ 10% cada; Fisher: < 10 empresas, 3–4 = 75%. Simulação de Hagstrom: dos 3.000 portfólios de **15 ações**, 808 bateram o mercado (≈ 1 em 4) — mais dispersão, mais chance de superar *e* de ficar abaixo | Hagstrom cap. 5 |
| Peso por convicção | **Kelly**: fração = 2p − 1 (p = probabilidade de acerto; 55% → 10%; 70% → 40%). Usar **Kelly fracionário (semi-Kelly)** para reduzir risco | Hagstrom |
| Giro | Rotatividade de **10–20% ao ano** (horizonte de 5–10 anos) | Hagstrom |
| Carteira-modelo Rico | **5 a 8 ações**, base em blue chips do Ibovespa + posições táticas; revisão todo **dia 10**; benchmark **Ibovespa** | Smart Ações |
| Teoria moderna | Markowitz: risco da carteira ≠ média dos riscos; **fronteira eficiente**; Tobin: carteira tangente + ativo livre de risco; Sharpe/CAPM: **beta**; APT: múltiplos fatores | CVM 1.2.3 |
| Medidas de risco | Desvio-padrão; **downside risk / Sortino** (só perdas); **VaR** (pior perda esperada para um nível de confiança) | CVM 1.2.4 |
| Concentração (Berkshire) | Investir no que se entende, vantagens duráveis, gestores íntegros; **concentrar em poucas ideias de alta convicção**; disciplina e deixar os juros compostos agirem. ~2/3 da carteira de US$ 297,8 bi em 9 posições, rendendo 10% a.a. em dividendos sobre o custo | Berkshire 2025 |
| Custos | Corretagem ≤ **0,7% do aporte**; acumular antes de aportar se o custo for maior | e-book FIIs |
| Benchmarks | Ações: Ibovespa · FIIs: IFIX · Renda fixa/carteira total: CDI · Inflação: IPCA | Rico, B3 |

**[Implementação] Limites de risco sugeridos:** peso máximo por ação (ex.: 20%, como Copel/Itaú na Smart Ações) e por setor; peso de posições "táticas/cíclicas" reduzido em cenário adverso (Rico manteve MDNE3 em 6% e PRIO3 em 4%); cálculo de beta, volatilidade, Sortino, VaR e *drawdown* máximo da carteira do usuário.

---

## 8. Gestão de risco e comportamento

**Vieses a serem neutralizados pelo software** (Hagstrom cap. 6): excesso de confiança, reação exagerada a notícias, **aversão a perdas**, contabilidade mental, **aversão míope a perdas** (olhar a carteira com frequência demais aumenta a dor das perdas), efeito manada ("lemingue").

**Lições do histórico da Berkshire (1965–2025):** retorno composto de **19,7% a.a. vs. 10,5% do S&P 500** — e mesmo assim quedas anuais de **−48,7% (1974)**, **−31,8% (2008)**, **−23,1% (1990)** e **−19,9% (1999, ano em que o S&P subiu 21%)**. Em 2025: +10,9% vs. +17,9%. → Até a melhor estratégia passa anos abaixo do índice; o software deve mostrar desempenho em janelas longas e comunicar *drawdowns* esperados.

**Princípios de risco da Berkshire 2025 (Greg Abel):**

- Balanço **"fortaleza"**: dívida usada com moderação; liquidez para cumprir obrigações no pior cenário e agir quando outros têm medo (caixa e Treasuries > US$ 370 bi).
- **Recomprar ações somente abaixo do valor intrínseco**, estimado de forma conservadora.
- **Política de dividendos:** reter lucros enquanto cada R$ 1 retido gerar mais de R$ 1 de valor de mercado (= regra do "um dólar").
- Precificar o risco corretamente e **"ir embora quando o preço está errado"**; disciplina acima de volume.
- Avaliar negócios pela capacidade de **manter e fortalecer a posição competitiva no longo prazo**, não por resultados de curto prazo.
- Erros admitidos: Kraft Heinz ("retorno bem aquém do adequado") → registrar e revisar teses que falharam.

**[Implementação]** Diário de decisões (tese, preço justo, margem, data de revisão), alertas de quebra de tese (ROE, dívida, vacância), e mensagens que lembram o usuário dos princípios quando houver quedas fortes.

---

## 9. Educação e finanças pessoais (Pai Rico, Pai Pobre)

- **Ativo coloca dinheiro no seu bolso; passivo tira.** (A casa própria, em geral, é passivo.) → classificar itens do patrimônio pelo **fluxo de caixa**, não pelo valor contábil.
- **Os ricos não trabalham por dinheiro** — fazem o dinheiro trabalhar para eles; objetivo é **renda passiva > despesas**.
- **Alfabetização financeira** (contabilidade, investimentos, mercados, leis) é pré-requisito.
- **Cuide do seu próprio negócio:** construir a **coluna de ativos** (ações, títulos, FIIs, imóveis que geram renda, negócios).
- **Pague-se primeiro** (autocontrole): poupar/investir antes de gastar.
- Impostos e estruturas legais importam; **invista primeiro em educação**; mentalidade de riqueza de longo prazo, não de enriquecimento rápido.

**[Implementação] Painel de independência financeira:** taxa de poupança mensal, renda passiva (dividendos + rendimentos de FIIs + juros) ÷ despesas mensais (% de independência), evolução da coluna de ativos.

---

## 10. Retrato do mercado nas fontes (jun–jul/2026) — **dados datados**

> Usar como exemplo de metodologia e referência histórica, não como recomendação atual (este documento é de out/2026).

**Carteira Smart Ações 5+ (10/06/2026)** — 8 ações, sem troca de nomes no mês:

| Ação | Setor | Peso | Mudança |
|---|---|---|---|
| Copel (CPLE3) | Energia e saneamento | 20% | — |
| Itaú (ITUB4) | Bancos | 20% | — |
| Caixa Seguridade (CXSE3) | Seguros | 16% | +6 p.p. |
| Isa Energia (ISAE4) | Energia (transmissão) | 16% | — |
| Vale (VALE3) | Mineração | 12% | — |
| Moura Dubeux (MDNE3) | Construção civil | 6% | +1 p.p. |
| Vibra (VBBR3) | Óleo, gás e petroquímicos | 6% | −6 p.p. |
| Prio (PRIO3) | Óleo, gás e petroquímicos | 4% | −1 p.p. |

Desempenho: mês (10/05–10/06) **−6,61% vs. Ibovespa −7,76%**; 2026 **+5,71% vs. +3,94%**; desde jan/2025 **+56,93% vs. +41,17%**.

**Teses típicas usadas** (úteis como "tags" de análise): setor regulado e previsível (transmissão, energia), **baixo beta**, receita recorrente, dividend yield elevado, liderança setorial, geração de caixa, preço em suporte / MM200, tendência primária de alta, realização parcial após forte alta.

**Cenário macro descrito:** maio/2026 com Ibovespa −7,22% e perda do suporte de 175 mil pontos; saída de capital estrangeiro para teses de IA (EUA, Coreia, Taiwan); expectativas de inflação em alta e Selic alta por mais tempo; ruído eleitoral e risco fiscal. Junho: MSCI ACWI −1,5%, Ibovespa −1,0%, Fed mais *hawkish* (Kevin Warsh), abertura da curva de juros. Recomendação: equilíbrio, qualidade como linha mestra, commodities relevantes, sem aumentar cíclicos de forma agressiva.

---

## 11. Especificação de métricas para o software **[Implementação]**

### 11.1 Fórmulas principais

| Métrica | Fórmula |
|---|---|
| P/L | Preço ÷ LPA |
| Earnings yield | LPA ÷ Preço |
| P/VP | Preço ÷ VPA |
| Número de Graham | √(22,5 × LPA × VPA) |
| Valor de Graham (crescimento) | LPA × (8,5 + 2g) |
| EV | Valor de mercado + Dívida líquida |
| EV/EBITDA | EV ÷ EBITDA |
| Dív. líquida/EBITDA | (Dívida bruta − Caixa) ÷ EBITDA 12m |
| Liquidez corrente | Ativo circulante ÷ Passivo circulante |
| Capital de giro líquido | Ativo circulante − Passivo circulante |
| Net-net (NCAV) | Ativo circulante − Passivo total |
| ROE | Lucro líquido (recorrente) ÷ PL médio |
| DuPont | ROE = (LL/Receita) × (Receita/Ativo) × (Ativo/PL) |
| Margens | Bruta, EBITDA, líquida = item ÷ Receita líquida |
| Lucros do proprietário | LL + D&A − Capex de manutenção − Δ Capital de giro |
| Teste do "um dólar" | Δ Valor de mercado (5a) ÷ Σ Lucros retidos (5a) |
| Payout / DY | Dividendos ÷ Lucro; Dividendos 12m ÷ Preço |
| CAPM | Ke = Rf + β (Rm − Rf) |
| WACC | E/V·Ke + D/V·Kd·(1 − t) |
| Gordon | D1 ÷ (k − g) |
| Margem de segurança | (Valor justo − Preço) ÷ Valor justo |
| FII: DY, P/VP, vacância, cap rate | ver seção 5.2 |
| Carteira: β, volatilidade, Sortino, VaR, drawdown | ver seção 7 |

### 11.2 Exemplo de esqueleto de scoring (Python)

```python
import math

def numero_graham(lpa: float, vpa: float) -> float | None:
    if lpa <= 0 or vpa <= 0:
        return None
    return math.sqrt(22.5 * lpa * vpa)

def lucros_do_proprietario(ll, da, capex_manut, delta_capital_giro):
    return ll + da - capex_manut - delta_capital_giro

def margem_seguranca(valor_justo, preco):
    return (valor_justo - preco) / valor_justo

def filtro_graham_defensivo(e) -> dict:
    """e: dicionário com dados históricos da empresa (10 anos)."""
    return {
        "tamanho": e["receita_liq"] >= 1e9 and e["liquidez_diaria"] >= 1e7,
        "liquidez_corrente": e["ativo_circ"] / e["passivo_circ"] >= 2.0,
        "divida_lp_vs_giro": e["divida_lp"] <= e["ativo_circ"] - e["passivo_circ"],
        "lucro_10_anos": all(l > 0 for l in e["lucros_10a"]),
        "dividendos_10_anos": all(d > 0 for d in e["dividendos_10a"]),
        "crescimento_lpa": (sum(e["lpa_10a"][-3:]) / 3) >= 1.33 * (sum(e["lpa_10a"][:3]) / 3),
        "pl_x_pvp": (e["preco"] / (sum(e["lpa_10a"][-3:]) / 3)) * (e["preco"] / e["vpa"]) <= 22.5,
    }
```

Score final sugerido: **Qualidade** (Graham + Buffett: estabilidade, ROE sem alavancagem, margens, dívida) × **Preço** (margem de segurança sobre FCD/Gordon/Graham, múltiplos vs. pares e vs. juros) → ranking; **Timing técnico** apenas como desempate/gatilho de entrada; **Macro** ajusta pesos setoriais.

### 11.3 Dados e rotinas
- **Fontes de dados sugeridas:** CVM Dados Abertos (DFP, ITR, informes mensais de FIIs), B3 (cotações, proventos, composição de índices), páginas de RI das empresas, Banco Central (SGS: Selic, IPCA, câmbio, Focus), Tesouro Direto (curvas NTN-B, LTN).
- **Rotina diária:** cotações, indicadores técnicos, alertas de preço vs. valor justo, notícias/fatos relevantes.
- **Rotina mensal:** rebalanceamento (Rico: dia 10 para ações, 3º dia útil para ETFs), relatórios de FIIs, revisão de proventos.
- **Rotina trimestral/anual:** atualização de demonstrações, recálculo de valor justo, revisão de teses.

---

## 12. Glossário essencial

- **ABL:** área bruta locável.
- **Backtest:** simulação da estratégia em dados passados.
- **Beta:** sensibilidade do ativo ao mercado.
- **Cap rate:** renda anual ÷ valor do imóvel.
- **Carrego:** retorno de manter um ativo até o vencimento.
- **Duration:** prazo médio ponderado dos fluxos; maior duration = maior oscilação com juros.
- **EBITDA:** lucro antes de juros, impostos, depreciação e amortização.
- **EV:** valor da firma.
- **Float:** recursos de seguros mantidos para pagar sinistros futuros e investidos enquanto isso (Berkshire: US$ 176 bi).
- **Hedge:** proteção contra variações (ex.: cambial).
- **IFIX:** índice de FIIs.
- **Margem de segurança:** diferença entre valor intrínseco e preço.
- **Payout:** % do lucro distribuído.
- **P/VP:** preço ÷ valor patrimonial.
- **RMG:** renda mínima garantida.
- **Top-down / bottom-up:** do macro para a empresa / da empresa para o macro.
- **Upside:** potencial de valorização até o preço-alvo.
- **Vacância financeira:** área sem gerar renda (vaga ou em carência).
- **Valor intrínseco:** valor presente dos fluxos de caixa futuros.

---

## 13. Limitações e avisos

1. Os limites numéricos de Graham foram calibrados para os EUA dos anos 1970; os ajustes para o Brasil nas seções 4.1 e 4.5 são **sugestões de projeto** e devem ser validados por backtest.
2. As carteiras e o cenário Rico refletem **jun–jul/2026**; não são recomendação atual.
3. Regras tributárias de FIIs e ETFs vêm de materiais de 2023–2026 e **podem ter mudado** — confirmar antes de implementar cálculos de IR.
4. Análise técnica, segundo o próprio livro da CVM, **não é ciência**; usar com cautela e validar estatisticamente.
5. Este documento é material educacional para o desenvolvimento de software e **não constitui recomendação de investimento**.