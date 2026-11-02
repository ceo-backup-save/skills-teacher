# Lotofácil — Objetivo 02: estatística dos 100 concursos

- Universo: **3720-3819** (100 concursos)
- Fonte: API Loterias Caixa (inacessível no ambiente) → espelho faelw/lotofacil-data; 3819 conferido em 2 fontes
- Regra A: acumular valores em ordem decrescente de frequência até ≥ 70%
- Regra B: valores com frequência individual < 30% fora da faixa A

## Tabela A — prevalentes (~70%)

| Indicador | Faixa principal | Casos | % |
|---|---|---|---|
| Pares / ímpares | 6–8 | 81 | 81.0% |
| Baixas / altas | 7–9 | 76 | 76.0% |
| Borda / miolo | 9–11 | 84 | 84.0% |
| Duplas exatas | 0–2 | 71 | 71.0% |
| Trios exatos | 0–1 | 71 | 71.0% |
| Quadras exatas | 0–1 | 88 | 88.0% |
| Maior sequência | 3–5 | 73 | 73.0% |
| Repetidas do anterior | 8–10 | 85 | 85.0% |
| Total de grupos (linhas+colunas) | 9–10 | 95 | 95.0% |
| Pares adjacentes | 7–9 | 81 | 81.0% |
| Soma das 15 dezenas | 173–207 | 70 | 70.0% |

## Tabela B — não prevalentes (<30%)

| Indicador | Valores (freq. individual) | Casos | % |
|---|---|---|---|
| Pares / ímpares | 5 (11.0%); 9 (6.0%); 10 (2.0%) | 19 | 19.0% |
| Baixas / altas | 4 (1.0%); 5 (1.0%); 6 (14.0%); 10 (5.0%); 11 (3.0%) | 24 | 24.0% |
| Borda / miolo | 6 (1.0%); 7 (1.0%); 8 (11.0%); 12 (2.0%); 13 (1.0%) | 16 | 16.0% |
| Duplas exatas | 3 (16.0%); 4 (12.0%); 5 (1.0%) | 29 | 29.0% |
| Trios exatos | 2 (17.0%); 3 (11.0%); 4 (1.0%) | 29 | 29.0% |
| Quadras exatas | 2 (10.0%); 3 (2.0%) | 12 | 12.0% |
| Maior sequência | 6 (17.0%); 7 (5.0%); 8 (2.0%); 9 (3.0%) | 27 | 27.0% |
| Repetidas do anterior | 6 (1.0%); 7 (7.0%); 11 (3.0%); 12 (4.0%) | 15 | 15.0% |
| Total de grupos (linhas+colunas) | 8 (5.0%) | 5 | 5.0% |
| Pares adjacentes | 6 (4.0%); 10 (14.0%); 11 (1.0%) | 19 | 19.0% |
| Soma das 15 dezenas | extremos (143–143 e 242–242) | 30 | 30.0% |

## Anexo — distribuição completa

```
Pares / ímpares              5:11 | 6:25 | 7:33 | 8:23 | 9:6 | 10:2
Baixas / altas               4:1 | 5:1 | 6:14 | 7:17 | 8:37 | 9:22 | 10:5 | 11:3
Borda / miolo                6:1 | 7:1 | 8:11 | 9:37 | 10:23 | 11:24 | 12:2 | 13:1
Duplas exatas                0:16 | 1:25 | 2:30 | 3:16 | 4:12 | 5:1
Trios exatos                 0:36 | 1:35 | 2:17 | 3:11 | 4:1
Quadras exatas               0:58 | 1:30 | 2:10 | 3:2
Maior sequência              3:19 | 4:29 | 5:25 | 6:17 | 7:5 | 8:2 | 9:3
Repetidas do anterior        6:1 | 7:7 | 8:25 | 9:29 | 10:31 | 11:3 | 12:4
Total de grupos (linhas+colunas) 8:5 | 9:43 | 10:52
Pares adjacentes             6:4 | 7:19 | 8:35 | 9:27 | 10:14 | 11:1
Soma das 15 dezenas          140–149:1 | 150–159:1 | 160–169:4 | 170–179:18 | 180–189:18 | 190–199:18 | 200–209:21 | 210–219:11 | 220–229:6 | 230–239:1 | 240–249:1
```
