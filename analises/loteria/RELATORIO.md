# Dia de Sorte × Timemania — padrões de repetição, colunas e frequência

**Recorte:** últimos 100 concursos de cada jogo  
- **Dia de Sorte:** concursos **1238 a 1337** (06/07/2026 a 01/11/2026) — 7 dezenas de 1 a 31  
- **Timemania:** concursos **2363 a 2462** (05/03/2026 a 01/11/2026) — 7 dezenas de 1 a 80  
**Método:** distribuições exatas (hipergeométrica, qui-quadrado) + Monte Carlo para o que não tem forma fechada. Script reprodutível em `analise.py`.

> **Resposta curta:** existe um padrão nos dois jogos — mas é o padrão do sorteio justo. Frequência de dezenas, repetição em relação ao concurso anterior, colunas e somas batem com o previsto por azar puro. E os dois jogos **não** têm relação entre si.


## 1. As dezenas que mais saem (últimos 100)


### 🟢 Dia de Sorte

- Esperado por dezena: **22,58** aparições em 100 concursos (cada dezena tem 22,58% de chance por concurso).

- Mais sorteadas: **02** (30×), **11** (29×), **04** (28×), **06** (28×), **28** (28×), **26** (27×).

- Menos sorteadas: 17 (13×), 05 (16×), 18 (17×), 13 (17×), 21 (18×), 30 (19×).

- Máxima: **30×** (p = 0,856 contra o máximo esperado por acaso); mínima: **13×**.

- Qui-quadrado de uniformidade: χ² = 24,0 com 30 graus de liberdade → **p = 0,773**.

- Uma dezena precisa de cerca de **37×** para destoar de verdade (limiar de Bonferroni com 31 dezenas). A campeã chegou a 30×.


### 🟣 Timemania

- Esperado por dezena: **8,75** aparições em 100 concursos (cada dezena tem 8,75% de chance por concurso).

- Mais sorteadas: **22** (15×), **52** (15×), **26** (14×), **80** (14×), **10** (13×), **64** (13×).

- Menos sorteadas: 69 (4×), 61 (4×), 55 (4×), 48 (4×), 39 (4×), 33 (4×).

- Máxima: **15×** (p = 0,915 contra o máximo esperado por acaso); mínima: **4×**.

- Qui-quadrado de uniformidade: χ² = 60,2 com 79 graus de liberdade → **p = 0,943**.

- Curiosidade fora das dezenas: 57 times do coração diferentes em 100 concursos; o mais repetido foi ATLETICO /MG (5×).

- Uma dezena precisa de cerca de **18×** para destoar de verdade (limiar de Bonferroni com 80 dezenas). A campeã chegou a 15×.


**Leitura:** a “tábua de quentes” é compatível com sorteio uniforme. Se você olhar 31 ou 80 dezenas, alguém sempre vai parecer quente — é o efeito do teste múltiplo, não sinal.


## 2. Padrão de repetição em relação ao concurso anterior

Quantas dezenas de um concurso reaparecem no seguinte (comparando sempre com o sorteio imediatamente anterior):


| Jogo | Média de repetidas | Esperado | Erro padrão | z | p (média) | p (distribuição) |
|---|---|---|---|---|---|---|
| Dia de Sorte | **1,64** | 1,58 | 0,099 | 0,56 | 0,575 | 0,805 |
| Timemania | **0,63** | 0,61 | 0,072 | 0,19 | 0,849 | 0,606 |

Distribuição completa (observado × esperado pela hipergeométrica):


**Dia de Sorte** — 99 pares de concursos consecutivos


| Dezenas repetidas | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Observado | 10 | 38 | 35 | 12 | 2 | 2 | 0 |
| Esperado | 13,0 | 35,5 | 33,6 | 14,0 | 2,7 | 0,2 | 0,0 |


- Concursos **sem nenhuma repetição**: 10 (esperado 13,0) → na prática, **89,9%** dos concursos repetem ao menos 1 dezena (teoria: 86,8%).

- Maiores repetições da janela: concurso 1254 repetiu 5 (02, 13, 20, 23, 28); concurso 1279 repetiu 4 (01, 03, 04, 30); concurso 1286 repetiu 4 (04, 10, 12, 17); concurso 1293 repetiu 5 (06, 11, 12, 22, 26).


**Timemania** — 99 pares de concursos consecutivos


| Dezenas repetidas | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Observado | 47 | 42 | 10 | 0 |
| Esperado | 50,8 | 37,1 | 9,8 | 1,2 |


- Concursos **sem nenhuma repetição**: 47 (esperado 50,8) → na prática, **52,5%** dos concursos repetem ao menos 1 dezena (teoria: 48,7%).


**Leitura:** o número de repetidas é exatamente o que a hipergeométrica prevê. A “média de repetição” de cada jogo é, na prática, uma constante do jogo (k²/N), não uma tendência que aparece e desaparece.


## 3. As colunas (1ª a 7ª dezena do volante)

Coluna = posição da dezena depois de ordenar o resultado. É aqui que aparece o padrão mais forte — e o mais mal interpretado: ele é **combinatório**, não sorteável.


### Dia de Sorte — universo 1 a 31


| Coluna | Moda (nº mais frequente) | Vezes | Média | Média esperada | z | Faixa |
|---|---|---|---|---|---|---|
| 1ª | **01** | 24 | 3,7 | 4,0 | -0,85 | 01–12 |
| 2ª | **06** | 11 | 7,5 | 8,0 | -1,17 | 02–17 |
| 3ª | **15** | 9 | 11,9 | 12,0 | -0,13 | 03–24 |
| 4ª | **11** | 10 | 16,4 | 16,0 | 0,95 | 06–27 |
| 5ª | **22** | 11 | 20,4 | 20,0 | 0,80 | 09–29 |
| 6ª | **27** | 13 | 24,6 | 24,0 | 1,55 | 14–30 |
| 7ª | **31** | 26 | 28,0 | 28,0 | -0,07 | 17–31 |


### Timemania — universo 1 a 80


| Coluna | Moda (nº mais frequente) | Vezes | Média | Média esperada | z | Faixa |
|---|---|---|---|---|---|---|
| 1ª | **01** | 10 | 10,3 | 10,1 | 0,22 | 01–47 |
| 2ª | **22** | 8 | 20,1 | 20,2 | -0,17 | 02–54 |
| 3ª | **26** | 6 | 29,1 | 30,4 | -1,00 | 06–60 |
| 4ª | **36** | 6 | 39,3 | 40,5 | -0,97 | 09–72 |
| 5ª | **64** | 7 | 49,9 | 50,6 | -0,56 | 17–76 |
| 6ª | **75** | 6 | 60,5 | 60,8 | -0,20 | 24–78 |
| 7ª | **80** | 14 | 71,0 | 70,9 | 0,12 | 30–80 |


**Leitura:** a 1ª coluna concentra valores baixos e a 7ª valores altos — em qualquer jogo de 7 dezenas. E note a coincidência com a teoria: a dezena **01** na 1ª coluna do Dia de Sorte aparece 24× em 100 e a **31** na 7ª aparece 26×; nos dois casos 7/31 = 22,6% prevê 22,6 vezes. Na Timemania, 80 na 7ª saiu 14× contra 7/80 = 8,8% esperado. A “coluna da dezena 80” parece quente; é só o extremo do universo.


## 4. Existe relação de frequência em cada concurso isolado?

Teste direto: em cada concurso, aposte nas 7 dezenas “mais quentes” dos 20 concursos anteriores. Se frequência significasse algo, essa aposta acertaria mais que o acaso.


| Jogo | Acertos médios por concurso | Esperado por acaso | Simulação (média) | p |
|---|---|---|---|---|
| Dia de Sorte | 1,501 | 1,581 | 1,582 | 0,098 |
| Timemania | 0,577 | 0,613 | 0,610 | 0,295 |

Teste do atraso (a chance muda conforme o tempo sem sair?):


| Jogo | 1 | 2 | 3 | 4 | 5-9 | 10+ |
|---|---|---|---|---|---|---|
| Dia de Sorte | 22,3% | 21,9% | 22,6% | 24,0% | 22,6% | 22,8% |
| Timemania | 8,9% | 8,6% | 8,8% | 9,0% | 8,9% | 8,6% |

(Chance de referência por concurso: 22,58% no Dia de Sorte e 8,75% na Timemania.)


**Leitura:** nenhuma das duas rotinas bate o acaso. Dezena quente não continua quente; dezena atrasada não fica “devendo”. Em ambos os jogos os acertos ficaram levemente **abaixo** do esperado — o oposto do que o mito prevê.


## 5. Dia de Sorte × Timemania: os dois jogos conversam entre si?

Os dois sorteiam em dias diferentes (Dia de Sorte de segunda a sábado; Timemania terça, quinta e sábado), então comparamos os concursos **pareados por data** (tolerância de 1 dia, por causa da grafia de datas na fonte).


- Pares na janela: **51** (07/07/2026 a 01/11/2026; Dia de Sorte 1239–1337, Timemania 2412–2462).

- Dezenas em comum por par: **0,69** (esperado por azar: 0,61; z = 0,67; p = 0,470).

- Pares com **pelo menos uma** dezena em comum: 51,0% (esperado: 48,7%).

- Correlação de frequência nas 31 dezenas que existem nos dois jogos: Pearson r = 0,065 (p = 0,693), Spearman ρ = 0,128 (p = 0,470).

- Top 7 “quentes” do Dia de Sorte: 01, 02, 06, 11, 25, 27, 29; da Timemania: 02, 07, 09, 18, 21, 25, 30. Coincidem em **2** dezenas (02, 25).

- Com toda a série (1278 pares, desde 19/05/2018): média 0,60 vs esperado 0,61 (p = 0,489); r = 0,092 (p = 0,666).


**Leitura:** nenhuma relação. Duas coincidências entre os rankings de quentes é exatamente o que 31 dezenas escolhidas ao acaso produzem com mais frequência.


## 6. Veredito: o padrão existe nos dois jogos?


| Teste | p — Dia de Sorte | p — Timemania | Conclusão |
|---|---|---|---|
| Frequência das dezenas (qui-quadrado) | 0,773 | 0,943 | compatível com sorteio justo |
| Dezena mais frequente (máximo por simulação) | 0,856 | 0,915 | compatível com sorteio justo |
| Repetição do concurso anterior (média) | 0,575 | 0,849 | compatível com sorteio justo |
| Repetição do concurso anterior (distribuição) | 0,805 | 0,606 | compatível com sorteio justo |
| Dezenas quentes acertam mais? (série completa) | 0,098 | 0,295 | compatível com sorteio justo |

**O que existe nos dois jogos:**

1. Repetição média de dezenas do concurso anterior — sim, e é a mesma lei nos dois: k²/N = 1,58 no Dia de Sorte e 0,61 na Timemania. Nada além disso.

2. Colunas ordenadas com médias e modas previsíveis — sim, nos dois, por pura combinatoriedade (1ª coluna baixa, 7ª alta).

3. Soma, paridade e pares consecutivos dentro do esperado — sim, nos dois.


**O que não existe em nenhum dos dois:**

1. Dezena com frequência fora do acaso (p = 0,773 e 0,943).

2. Dezena “quente” que continua saindo, ou “fria” que está devendo.

3. Repetição acima do previsto entre concursos consecutivos.

4. Qualquer transferência de frequência de um jogo para o outro.


**Nota metodológica.** Um p < 0,05 isolado apareceria por acaso em ~1 de cada 20 testes; rodamos dezenas. Por isso cada achado foi checado na série completa (1.337 concursos do Dia de Sorte e 2.462 da Timemania) e com correção para testes múltiplos. O resultado é estável: os sorteios se comportam como sorteios.


**Limitações.** (a) O conjunto de dados público não traz o “Mês da Sorte” do Dia de Sorte — a análise cobre as 7 dezenas (o Time do Coração da Timemania não é dezena e ficou de fora); (b) o concurso 1307 da Timemania vinha com 8 dezenas na fonte (uma duplicidade), corrigido e documentado em `analise.py`; (c) nada aqui é recomendação de aposta — as dezenas dos próximos concursos continuam independentes do passado.
