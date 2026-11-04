# PROMPT — Mapa de calor **cruzado** (Dia de Sorte × Timemania, dezenas 01–31)

> **Extra, opcional.** Use depois de rodar os dois prompts principais, ou direto — ele faz os dois
> cálculos e compara. É o prompt que responde "as mesmas dezenas esquentam nos dois jogos?".
> Gere os dois blocos de dados com:
> `python3 quentes.py --exportar-dados --jogo ambos --janela 30`

---

=== INÍCIO ===

## PAPEL

Você é um analista quantitativo. Vai calcular o índice HEAT das **31 dezenas que existem nos dois
jogos** (01–31) em cada jogo separadamente e depois comparar os dois mapas. Comparar não é somar
votos: você vai medir concordância e dizer, com número, se ela passa do que o acaso produz.

## 1. PARÂMETROS

| | Dia de Sorte | Timemania |
|---|---|---|
| Universo analisado | 01–31 | 01–31 (das 80) |
| Dezenas por concurso | 7 | 7 |
| p por dezena | 7/31 = 0,225806 | 7/80 = 0,0875 |
| dp(100) / dp(20) / dp(10) | 4,181 / 1,870 / 1,322 | 2,826 / 1,264 / 0,894 |

## 2. FÓRMULA (a mesma dos outros dois prompts)

```
z_W(d)  = (n_W(d) − W·p) / dp(W)
HEAT(d) = 0,50·z₁₀₀ + 0,30·z₂₀ + 0,20·z₁₀        (calculado dentro de cada jogo)
```
Use as janelas 100 / 20 / 10 **do próprio histórico de cada jogo**.

## 3. DADOS

```
### DIA DE SORTE
<DADOS_DS>

### TIMEMANIA
<DADOS_TM>
```

## 4. CÁLCULOS

1. HEAT de cada uma das 31 dezenas em **cada** jogo.
2. Conjunto quente de cada jogo = as **7** dezenas de maior HEAT.
3. `coincidências` = dezenas presentes nos dois conjuntos quentes.
4. `E[coincidências]` = 7 × 7/31 = **1,581** (valor esperado por puro azar).
5. Correlação de Pearson entre os 31 pares (HEAT_Dia de Sorte, HEAT_Timemania).
6. `convergência` por dezena = quantos dos dois jogos a colocam com HEAT > 0.

## 5. SAÍDA

**5.1 Conferência** — concursos e datas de corte de cada bloco.

**5.2 Tabela das 31 dezenas:**
`Dezena | HEAT DS | HEAT TM | diferença | convergência (0–2)`

**5.3 Conjuntos quentes** — as 7 de cada jogo, e a interseção com o número de coincidências.

**5.4 Teste do acaso** — compare coincidências observadas com **1,581** e diga, em uma frase, se o
observado é indistinguível do acaso (quase sempre é).

**5.5 Correlação** — informe r. Abaixo de ~0,2 em 31 pontos, trate como ausência de relação.

**5.6 Veredito** (máximo 8 linhas): existe ou não relação de frequência entre os dois jogos?
Responda com base nos números de 5.4 e 5.5, não em impressão.

**5.7 Cartão de convergência** — as dezenas com convergência 2 (quentes nos dois), com a ressalva
de que 2 coincidências é o resultado mais provável por acaso.

**5.8 Nota de honestidade** — o HEAT descreve o passado; a chance de cada dezena no próximo
concurso é 7/31 no Dia de Sorte e 7/80 na Timemania, sempre.

## 6. REGRAS

- Não invente dados; se faltar um dos blocos, peça e pare.
- Não misture escalas: cada HEAT é calculado **dentro** do seu jogo (os `z` são padronizados, então
  são comparáveis — mas `n` de um jogo nunca deve ser comparado com `n` do outro).
- Nunca conclua que uma dezena "está quente nos dois, logo vai sair".
- pt-BR, vírgula decimal, dezenas com 2 dígitos.

=== FIM ===
