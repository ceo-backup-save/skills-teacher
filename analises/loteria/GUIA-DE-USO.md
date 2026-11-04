# Guia de uso — Mapa de calor do Dia de Sorte e da Timemania

Você tem em mãos **duas coisas que se encaixam**: um cálculo (o script) e um prompt (o texto que
faz um assistente refazer o mesmo cálculo). O script existe para o prompt não virar opinião: quando
os dois usam a mesma fórmula, o ranking sai igual — e qualquer diferença é erro de conta, não
"leitura de mercado".

| Peça | Onde está | Para quê |
|---|---|---|
| Prompt do Dia de Sorte | `prompts/prompt-dia-de-sorte.md` | mapa das 31 dezenas |
| Prompt da Timemania | `prompts/prompt-timemania.md` | mapa das 80 dezenas |
| Prompt cruzado (extra) | `prompts/prompt-comparacao.md` | as 31 dezenas nos dois jogos |
| Calculadora | `quentes.py` | o resultado oficial, sem IA |
| Relatório de base | `relatorio.html` | por que os mapas não preveem nada |

---

## 0. O combinado antes de começar

O mapa de calor **ordena o passado com um critério explícito**. Ele não prevê o próximo sorteio.

Isso não é opinião, é resultado: nos últimos 100 concursos de cada jogo, a frequência das dezenas
passou no teste de uniformidade (p = 0,77 no Dia de Sorte e 0,94 na Timemania), e apostar sempre nas
7 mais quentes dos 20 concursos anteriores acertou **1,50** por concurso no Dia de Sorte (esperado
1,58) e **0,58** na Timemania (esperado 0,61) — abaixo do acaso. Detalhes em `relatorio.html`.

Então use o mapa como **critério de escolha pessoal, auditável e consistente**, não como previsão.
O prompt já vem com essa cláusula embutida — e vale conferir se o modelo a respeitou (checklist no
item 5).

---

## 1. A fórmula, em uma tela

```
z_W(d)  = (n_W(d) − W·p) / √(W·p·(1−p))        p = 7/N   (N = 31 ou 80)
HEAT(d) = 0,50·z₁₀₀ + 0,30·z₂₀ + 0,20·z₁₀
```

| Termo | O que mede | Peso |
|---|---|---|
| `z₁₀₀` | base: frequência contra o esperado do jogo | 0,50 |
| `z₂₀` | momento: quem esquentou nas últimas semanas | 0,30 |
| `z₁₀` | faísca: quem está saindo agora | 0,20 |

Os pesos são **arbitrários e fixos** — é essa fixidez que torna o ranking comparável entre uma
semana e outra. Se você mudar os pesos, mude nos três arquivos (prompt, versão curta, `quentes.py`).

Três complementos que **não** entram no HEAT:

- **atraso** — concursos sem sair. Informativo. Não é dívida.
- **consistência** — em quantas das três janelas a dezena está acima do esperado (0 a 3).
- **momentum** — `z₁₀ − z₁₀₀`: subiu agora ou está em queda.

---

## 2. Escolha o caminho

### Caminho A — rodar local (30 segundos, resultado oficial)

```bash
cd analises/loteria
python3 quentes.py --salvar                  # os dois jogos, janela 100
python3 quentes.py --jogo timemania          # só um
python3 quentes.py --janela 50               # base de 50 em vez de 100
```

Gera `quentes-dia-de-sorte.md` e `quentes-timemania.md` com top 10, frias, em alta, em queda e
atrasos. É o gabarito para conferir qualquer resposta de IA.

### Caminho B — prompt no assistente, com dados colados (recomendado)

1. Gere o bloco de dados:
   ```bash
   python3 quentes.py --exportar-dados --jogo dia-de-sorte --janela 30
   ```
   Sai no formato `concurso;data;d1;d2;d3;d4;d5;d6;d7`.
2. Abra `prompts/prompt-dia-de-sorte.md`, copie **tudo** entre `=== INÍCIO ===` e `=== FIM ===`.
3. Troque `<DADOS>` pelo bloco do passo 1.
4. Envie. Confira a resposta com o checklist do item 5.
5. Repita com `prompt-timemania.md`.

> **Quantos concursos colar?** O mínimo útil são **100** (a janela base). Para economizar contexto,
> 30 concursos funcionam — o prompt manda avisar quando a base é menor que 100. Abaixo de 20, o
> resultado fica dominado por ruído: não vale.

### Caminho C — deixar o assistente buscar o histórico

Funciona se a ferramenta tiver acesso à web. Acrescente ao final do prompt:

> *"Busque o histórico oficial dos últimos 100 concursos do Dia de Sorte e monte o bloco no formato
> `concurso;data;d1..d7` antes de calcular. Mostre o bloco na resposta para eu conferir a fonte e a
> data de corte. Se não conseguir 100 concursos íntegros, diga quantos conseguiu."*

Sempre confira o bloco: modelo que "lembra" de resultado de loteria erra com frequência.

---

## 3. Onde estão os dados deste repositório

- `dados/dia-de-sorte.json` — 1.337 concursos (desde 19/05/2018)
- `dados/timemania.json` — 2.462 concursos (desde 01/03/2008)
- `ultimos-100-dia-de-sorte.csv` e `ultimos-100-timemania.csv` — os recortes prontos

Para atualizar, substitua os JSONs pela versão mais recente da fonte pública (o formato é o mesmo:
`{concurso, data, resultado[]}`) e rode `python3 quentes.py --salvar`.

---

## 4. Como ler a saída

| Coluna | Significa | Como interpretar |
|---|---|---|
| `n₁₀₀` | saídas em 100 concursos | No Dia de Sorte o esperado é 22,58; na Timemania, 8,75 |
| `z₁₀₀` | quantos desvios-padrão acima/abaixo | ±2 já é comum; ±3 em 80 dezenas também aparece por acaso |
| `n₂₀`, `n₁₀` | saídas recentes | base do "momento" e da "faísca" |
| `Atraso` | concursos sem sair | informativo — **não** aumenta a chance |
| `HEAT` | índice composto | positivo = acima do esperado no conjunto das três janelas |
| `Consist.` | `3/3` = acima do esperado nas três janelas | o mais próximo de "sinal estável" que este índice oferece |

**Leitura de conjunto:** HEAT alto + consistência `3/3` = dezena acima do esperado em todas as
janelas. HEAT alto com `1/3` = puxado por uma janela só (geralmente a de 10, a mais ruidosa).

---

## 5. Checklist de auditoria (7 itens)

Rode isto em toda resposta antes de acreditar:

1. **Data de corte** declarada e compatível com o último concurso do bloco colado?
2. **Nenhum número inventado** — confira 3 dezenas contra `quentes-*.md`.
3. **A conta aparece** para pelo menos 3 dezenas (senão é chute com tabela bonita).
4. **Desvio-padrão correto do jogo** (4,181/1,870/1,322 no Dia de Sorte; 2,826/1,264/0,894 na
   Timemania). Modelo que usa "raiz de n" simples está errado — o sorteio é sem reposição.
5. **Atraso não entrou no HEAT** e não foi tratado como "dívida".
6. **Nota de honestidade presente** e sem promessa de acerto.
7. **Somatório confere:** a soma de `n₁₀₀` de todas as dezenas deve ser `100 × 7 = 700`
   (ou `7 × nº de concursos`, se a base for menor).

O item 7 pega quase todo erro de contagem. Use sempre.

---

## 6. Exemplo real (corte: 01/11/2026)

**Dia de Sorte** — concurso 1337, base de 100 concursos:

| # | Dezena | n₁₀₀ | z₁₀₀ | n₂₀ | n₁₀ | Atraso | HEAT | Consist. |
|---|---|---|---|---|---|---|---|---|
| 1 | **02** | 30 | 1,77 | 9 | 2 | 3 | **1,57** | 2/3 |
| 2 | **11** | 29 | 1,54 | 8 | 3 | 0 | **1,44** | 3/3 |
| 3 | **28** | 28 | 1,30 | 6 | 4 | 5 | **1,15** | 3/3 |
| 4 | **23** | 23 | 0,10 | 8 | 5 | 0 | **1,02** | 3/3 |
| 5 | **25** | 26 | 0,82 | 6 | 4 | 1 | **0,91** | 3/3 |
| 6 | **26** | 27 | 1,06 | 6 | 3 | 4 | **0,88** | 3/3 |
| 7 | **09** | 23 | 0,10 | 7 | 5 | 1 | **0,86** | 3/3 |

Fria do dia: **17** (13 saídas, HEAT −1,74). Em queda: **02** e **20** (momentum −1,97 e −1,53) —
note que a dezena 02 é a mais quente da base de 100 e ainda assim está na lista de queda: é o índice
fazendo seu trabalho, não confundindo "muito saiu no passado" com "está saindo agora".

**Timemania** — concurso 2462, base de 100 concursos:

| # | Dezena | n₁₀₀ | z₁₀₀ | n₂₀ | n₁₀ | Atraso | HEAT | Consist. |
|---|---|---|---|---|---|---|---|---|
| 1 | **59** | 11 | 0,80 | 4 | 4 | 0 | **1,63** | 3/3 |
| 2 | **64** | 13 | 1,50 | 4 | 2 | 1 | **1,54** | 3/3 |
| 3 | **22** | 15 | 2,21 | 2 | 2 | 0 | **1,42** | 3/3 |
| 4 | **31** | 11 | 0,80 | 4 | 3 | 0 | **1,41** | 3/3 |
| 5 | **76** | 13 | 1,50 | 4 | 1 | 7 | **1,31** | 3/3 |
| 6 | **52** | 15 | 2,21 | 2 | 1 | 4 | **1,19** | 3/3 |
| 7 | **18** | 11 | 0,80 | 4 | 2 | 2 | **1,18** | 3/3 |

Fria do dia: **48** (4 saídas, HEAT −1,45). Repare: a líder (59) saiu 11× em 100 — **menos** que a
sexta colocada (52, com 15×). É o peso 30% do momento puxando a 59 para cima. Se você discorda
disso, o problema é a fórmula (mude os pesos), não a leitura.

> Para conferir: `python3 quentes.py` reproduz exatamente essas duas tabelas.

---

## 7. Erros comuns (e como o guia resolve cada um)

| Erro | Por que acontece | Antídoto |
|---|---|---|
| Tratar atraso como "dívida" | intuição de que a dezena "precisa sair" | atraso é coluna informativa; o prompt proíbe |
| Achar que 15× em 80 dezenas é "muito quente" | não se compara com o esperado (8,75) | sempre dividir pelo esperado / olhar o z |
| Usar janela de 10 como decisão | é a mais ruidosa (dp 0,89 na Timemania) | peso 20%; decida pelo conjunto das três |
| Comparar `n` do Dia de Sorte com `n` da Timemania | universos diferentes | compare `z`, nunca `n` |
| Somar os dois jogos para "confirmar" | dois rankings concordando parecem prova | a interseção esperada dos top 7 é 1,58 — ver prompt cruzado |
| Pedir ao modelo "os números que vão sair" | o modelo obedece e inventa | o prompt pede ranking, não palpite |
| Rodar toda hora | DS sorteia 6×/semana, TM 3×/semana | atualize uma vez por semana, após o último sorteio |
| Trocar os pesos "só um pouco" | quebra a comparabilidade | pesos fixos; se mudar, mude nos três lugares |

---

## 8. Rotina sugerida

1. **Uma vez por semana** (domingo), atualize os dois JSONs e rode `python3 quentes.py --salvar`.
2. Se quiser a versão narrada, alimente os prompts com `--exportar-dados --janela 30`.
3. Compare com a semana anterior: quem entrou/saiu do top 7 mostra **mudança de ranking**, não
   mudança de probabilidade.
4. Se algum dia um `z₁₀₀` passar de 3,15 no Dia de Sorte ou 3,42 na Timemania (limiar de Bonferroni
   para 31 e 80 dezenas), aí vale investigar de verdade — até hoje, em 1.337 e 2.462 concursos,
   nunca passou.

---

## 9. Perguntas rápidas

**Qual janela usar?** A de 100 como base — é a que o estudo validou. `--janela 50` serve para ver
tendência de médio prazo; abaixo de 30, é ruído.

**E o "Mês da Sorte" do Dia de Sorte?** Fica de fora: o histórico público usado aqui não traz o mês.
Se você tiver esse dado, ele entra como uma 8ª coluna categórica (12 valores), com o mesmo tratamento
de z — mas não misture com as dezenas.

**E o Time do Coração da Timemania?** Não é dezena; os prompts mandam ignorar.

**Posso usar o mapa para montar um jogo?** Pode, como critério pessoal. Só não espere vantagem: a
chance de acertar 7 no Dia de Sorte é 1 em 2.629.575 (e 1 em 3.176.716.400 na Timemania), com ou sem mapa.

**O script e o prompt dão o mesmo resultado?** Devem. Se divergirem, o prompt (ou o modelo) errou —
o script tem prioridade.
