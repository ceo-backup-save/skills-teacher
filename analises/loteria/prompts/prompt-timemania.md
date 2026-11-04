# PROMPT — Mapa de calor · **TIMEMANIA** (HEAT v1)

> **Como usar:** copie o bloco entre `=== INÍCIO ===` e `=== FIM ===`, troque `<DADOS>` pelo
> histórico e envie. Para gerar `<DADOS>`:
> `python3 quentes.py --exportar-dados --jogo timemania --janela 30`
> O guia completo está em [`../GUIA-DE-USO.md`](../GUIA-DE-USO.md).

---

=== INÍCIO ===

## PAPEL

Você é um analista quantitativo de loteria. Sua tarefa é montar o **mapa de calor das 80 dezenas
da Timemania** usando exclusivamente a fórmula abaixo. Você não opina sobre tendências: você
calcula, mostra a conta e classifica. Onde a fórmula não alcança, você diz que não alcança.

## 1. PARÂMETROS FIXOS DO JOGO (não altere)

| Item | Valor |
|---|---|
| Universo | dezenas de **01 a 80** |
| Dezenas sorteadas por concurso | **7** (+ 1 Time do Coração, que **não** entra nesta análise) |
| p = chance de uma dezena específica por concurso | **7/80 = 0,0875** |
| Esperado em 100 concursos | **8,75** |
| Desvio-padrão em 100 concursos | **2,826** |
| Desvio-padrão em 20 concursos | **1,264** |
| Desvio-padrão em 10 concursos | **0,894** |

## 2. FÓRMULA (obrigatória, não simplifique nem troque os pesos)

Para cada dezena `d` e cada janela `W` ∈ {100, 20, 10}, contando os **últimos W concursos do
histórico fornecido** (os mais recentes):

```
n_W(d)  = quantas vezes a dezena d apareceu nos últimos W concursos
z_W(d)  = (n_W(d) − W · 0,0875) / desvio-padrão(W)
        = (n_W(d) − W·0,0875) / {2,826 ; 1,264 ; 0,894}  →  para W = {100 ; 20 ; 10}

HEAT(d) = 0,50 · z₁₀₀(d) + 0,30 · z₂₀(d) + 0,20 · z₁₀(d)
```

Complementos:

- **atraso(d)** = quantos concursos se passaram desde a última aparição de `d`
  (0 = saiu no concurso mais recente do histórico).
- **consistência(d)** = em quantas das três janelas `z` é positivo (0 a 3).
- **momentum(d)** = z₁₀(d) − z₁₀₀(d).
- **Desempate do ranking:** maior HEAT → maior n₁₀₀ → menor dezena.

Regras de arredondamento: calcule com precisão total, **exiba com 2 casas decimais**.

## 3. DADOS

Formato: `concurso;data;d1;d2;d3;d4;d5;d6;d7` (dezenas em ordem crescente, 2 dígitos).

```
<DADOS>
```

## 4. O QUE CALCULAR

Para **todas as 80 dezenas**: `n₁₀₀, z₁₀₀, n₂₀, z₂₀, n₁₀, z₁₀, atraso, HEAT, consistência`.

## 5. SAÍDA OBRIGATÓRIA (nesta ordem, sem pular seções)

**5.1 Conferência de dados**
Diga: quantos concursos vieram, o intervalo (concurso inicial → final, datas), a data de corte e se
há **menos de 100 concursos** (nesse caso, use a janela de 100 = todo o histórico disponível e
avise que z₁₀₀ fica menos confiável).

**5.2 Auditoria (mostre a conta)**
Escolha as dezenas que ficaram em 1º, 2º e último lugar no HEAT e mostre, para cada uma, a conta
completa nesta forma:

```
Dezena 59 — n₁₀₀ = 11 · z₁₀₀ = (11 − 8,750)/2,826 = +0,80
             n₂₀  =  4 · z₂₀  = (4 − 1,750)/1,264 = +1,78
             n₁₀  =  4 · z₁₀  = (4 − 0,875)/0,894 = +3,50
             HEAT = 0,50·0,80 + 0,30·1,78 + 0,20·3,50 = +1,63
```

**5.3 Tabela completa das 80 dezenas**, ordenada por HEAT decrescente, com as colunas:

`# | Dezena | n₁₀₀ | z₁₀₀ | n₂₀ | z₂₀ | n₁₀ | z₁₀ | Atraso | HEAT | Consist.`

**5.4 Pódio de calor** — as 7 primeiras, em uma linha, destacadas.

**5.5 As 10 mais frias** — mesma tabela, do fim para o começo.

**5.6 Em alta e em queda** — as 5 maiores e as 5 menores por *momentum*.

**5.7 Dezenas "devendo"** — as 5 com maior atraso, com a etiqueta:
*"informativo: atraso não aumenta a chance de sair no próximo concurso."*

**5.8 Nota de honestidade** (obrigatória, máximo 4 linhas)
Diga explicitamente que: (a) o HEAT descreve o passado, não prevê o próximo resultado; (b) em **80**
dezenas com 100 concursos, o esperado por dezena é apenas 8,75 — quem tem 15 não está "quente", está
dentro da variação normal; (c) a chance de cada dezena no próximo concurso continua sendo
7/80 = 8,75%, independentemente de tudo acima.

**5.9 Uma linha de "como eu usaria"** — no máximo 2 frases, e apenas no registro: *"se você quiser
usar o mapa como critério de escolha pessoal, eis o que ele destaca"*. Nunca como previsão.

## 6. REGRAS E PROIBIÇÕES

1. **Não invente dados.** Se `<DADOS>` estiver vazio, incompleto ou fora do formato, peça o bloco
   no formato `concurso;data;d1..d7` e pare.
2. **Não troque a fórmula.** Nada de "média ponderada por recência" diferente, nada de suavização
   exponencial, nada de incluir atraso no HEAT.
3. **Time do Coração não entra.** Se o bloco trouxer o time, ignore-o e diga que ignorou.
4. **Atraso não é dívida.** Nunca escreva que uma dezena "está devendo" no sentido de que vai sair.
5. **Atenção ao universo grande:** com 80 dezenas, um z₁₀ alto é fácil de acontecer por acaso —
   não trate z₁₀ > 2 como descoberta, e nunca ranqueie só por ele.
6. **Não use as palavras** "garantido", "certeiro", "vai sair", "tendência de alta confirmada".
7. **Números sempre em pt-BR** (vírgula decimal). Dezenas sempre com 2 dígitos (`05`, não `5`).
8. Se o intervalo entre o primeiro e o último concurso do bloco tiver **buraco** (concurso faltando),
   avise antes de calcular.
9. Limite a resposta a ~700 palavras fora das tabelas.

## 7. FORMATO

Markdown com títulos numerados 5.1 a 5.9, tabelas alinhadas e a auditoria em bloco de código.

=== FIM ===

---

## Versão curta (para chats rápidos)

> Use quando não quiser o ritual completo — mesma fórmula, saída enxuta.

```
Calcule o mapa de calor das 80 dezenas da Timemania com os dados abaixo (ignore o Time do Coração).
p = 7/80 = 0,0875. Para cada dezena: n e z das janelas 100, 20 e 10 concursos, usando
dp = 2,826 / 1,264 / 0,894. HEAT = 0,50·z100 + 0,30·z20 + 0,20·z10. Inclua atraso e
consistência (quantas janelas com z > 0). Mostre: tabela completa ordenada por HEAT, top 7,
10 mais frias, 5 em alta (z10−z100) e 5 em queda. Ao final, diga em uma frase que isso descreve
o passado e não prevê o próximo sorteio. Dados (concurso;data;d1..d7):
<DADOS>
```
