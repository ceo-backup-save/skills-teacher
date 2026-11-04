# Dia de Sorte × Timemania — análise de padrões

Análise dos **últimos 100 concursos** de cada jogo (e da série completa como controle):
frequência de dezenas, repetição em relação ao concurso anterior, colunas do volante,
comportamento por concurso isolado e cruzamento entre os dois jogos.

## Arquivos

| Arquivo | O que é |
|---|---|
| `relatorio.html` | **relatório visual** (abre no navegador, gráficos embutidos) |
| `RELATORIO.md` | mesmo conteúdo em texto/tabelas, versionável |
| `analise.py` | calcula todas as estatísticas → `resultados.json` |
| `relatorio.py` | gera `RELATORIO.md`, `relatorio.html` e os CSVs a partir do JSON |
| `resultados.json` | saída bruta, para reuso |
| `dados/*.json` | histórico completo dos sorteios (fonte: eitchtee/loterias.json) |
| `ultimos-100-*.csv` | os dois recortes usados, em CSV |

## Como reproduzir

```bash
python3 analise.py     # ~25 s (Monte Carlo com semente fixa)
python3 relatorio.py
```

Sem dependências: só a biblioteca padrão do Python 3.11+.

## Método, em uma linha

Onde a distribuição nula tem forma fechada, usa-se a fórmula (hipergeométrica para as
repetições, estatísticas de ordem para as colunas, qui-quadrado para a uniformidade).
Onde não tem — máximo de frequência, correlação entre jogos, "dezenas quentes" —
usa-se Monte Carlo com semente fixa.

## Cuidados com os dados

- Timemania concurso 1307 (19/03/2019) vinha com 8 dezenas na fonte (uma `54` indevida);
  corrigido em `analise.py` (`CORRECOES`) após conferência com uma segunda fonte.
- A fonte registra alguns sorteios de sábado com data de domingo; o pareamento entre os
  dois jogos usa tolerância de 1 dia no calendário.
- O histórico público não inclui o "Mês da Sorte" do Dia de Sorte; a análise cobre as 7 dezenas.

## Conclusão

Os padrões que aparecem nos dois jogos são os do sorteio justo (repetição média k²/N,
colunas ordenadas, soma e paridade). Não há dezena fora do acaso, dezena quente que
continue quente, nem transferência de frequência de um jogo para o outro.
