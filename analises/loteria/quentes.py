#!/usr/bin/env python3
"""
MAPA DE CALOR — dezenas quentes do Dia de Sorte e da Timemania (ÍNDICE HEAT v1)
===============================================================================

Este script é a "calculadora oficial" dos prompts de `prompts/`. Se o modelo e o
script usarem a mesma fórmula, o ranking sai igual nos dois — é isso que torna o
prompt auditável em vez de opinativo.

Índice HEAT (por dezena, em uma data de corte):

    z(W)  = (saídas em W concursos - W·p) / raiz(W·p·(1-p))      com p = 7/N
    HEAT  = 0,50·z(100) + 0,30·z(20) + 0,20·z(10)

  · z(100) = "base" — frequência contra o esperado do jogo (k²/N)
  · z(20)  = "momento" — quem esquentou nas últimas semanas
  · z(10)  = "faísca"  — quem está saindo agora
  · desempate: HEAT, depois saídas em 100, depois dezena (crescente)
  · atraso (quantos concursos sem sair) NÃO entra no HEAT: é coluna informativa

Uso:
    python3 quentes.py                       # os dois jogos, janela 100
    python3 quentes.py --jogo timemania
    python3 quentes.py --janela 50
    python3 quentes.py --salvar              # grava quentes-<jogo>.md
    python3 quentes.py --exportar-dados --janela 30   # bloco p/ colar no prompt
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados"

PESOS = {"base": 0.50, "momento": 0.30, "faisca": 0.20}
JANELAS = {"base": 100, "momento": 20, "faisca": 10}

JOGOS = {
    "dia-de-sorte": {"nome": "Dia de Sorte", "N": 31, "arquivo": "dia-de-sorte.json"},
    "timemania": {"nome": "Timemania", "N": 80, "arquivo": "timemania.json"},
}


def carregar(chave: str) -> list[dict]:
    cfg = JOGOS[chave]
    bruto = json.loads((DADOS / cfg["arquivo"]).read_text(encoding="utf-8"))
    jogos = []
    for r in bruto:
        dez = [int(x) for x in r["resultado"]][:7]
        if len(set(dez)) != 7:
            continue
        jogos.append({"concurso": r["concurso"], "data": r["data"], "dezenas": sorted(dez)})
    jogos.sort(key=lambda j: j["concurso"])
    return jogos


def z_score(saidas: int, janela: int, p: float) -> float:
    esperado = janela * p
    dp = math.sqrt(janela * p * (1 - p))
    return (saidas - esperado) / dp if dp else 0.0


def calcular(jogos: list[dict], N: int, janela_base: int = 100) -> dict:
    """Devolve o ranking HEAT e os insumos de cada dezena na data de corte."""
    k = 7
    p = k / N
    janelas = {"base": janela_base, "momento": JANELAS["momento"], "faisca": JANELAS["faisca"]}

    # atraso: quantos concursos desde a última aparição (0 = saiu no último)
    ultimo = {d: None for d in range(1, N + 1)}
    for i, j in enumerate(jogos):
        for d in j["dezenas"]:
            ultimo[d] = i
    atraso = {d: (len(jogos) - 1 - i) if i is not None else None for d, i in ultimo.items()}

    linhas = []
    for d in range(1, N + 1):
        saidas = {}
        for nome, w in janelas.items():
            recorte = jogos[-w:]
            saidas[nome] = sum(1 for j in recorte if d in j["dezenas"])
        zs = {nome: z_score(saidas[nome], janelas[nome], p) for nome in janelas}
        heat = sum(PESOS[n] * zs[n] for n in PESOS)
        consistencia = sum(1 for n in janelas if zs[n] > 0)
        linhas.append(
            {
                "dezena": d,
                "saidas": saidas,
                "z": zs,
                "heat": heat,
                "consistencia": consistencia,
                "momentum": zs["faisca"] - zs["base"],
                "atraso": atraso[d],
            }
        )
    linhas.sort(key=lambda r: (-r["heat"], -r["saidas"]["base"], r["dezena"]))

    return {
        "janelas": janelas,
        "p": p,
        "esperado_base": janelas["base"] * p,
        "linhas": linhas,
        "ultimo_concurso": jogos[-1]["concurso"],
        "ultima_data": jogos[-1]["data"],
        "n_concursos": len(jogos),
    }


def num(x, casas=2):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def tabela(calc: dict, quantas: int = 10, invertido: bool = False) -> str:
    linhas = calc["linhas"]
    linhas = list(reversed(linhas))[:quantas] if invertido else linhas[:quantas]
    out = ["| # | Dezena | 100 | z₁₀₀ | 20 | z₂₀ | 10 | z₁₀ | Atraso | HEAT | Consist. |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(linhas, start=1):
        out.append(
            f"| {i} | **{r['dezena']:02d}** | {r['saidas']['base']} | {num(r['z']['base'])} | "
            f"{r['saidas']['momento']} | {num(r['z']['momento'])} | {r['saidas']['faisca']} | "
            f"{num(r['z']['faisca'])} | {r['atraso']} | **{num(r['heat'])}** | {r['consistencia']}/3 |"
        )
    return "\n".join(out)


def resumo_md(chave: str, calc: dict) -> str:
    cfg = JOGOS[chave]
    top = calc["linhas"][:10]
    frias = calc["linhas"][-10:][::-1]
    em_alta = sorted(calc["linhas"], key=lambda r: -r["momentum"])[:5]
    em_queda = sorted(calc["linhas"], key=lambda r: r["momentum"])[:5]
    devendo = sorted(
        [r for r in calc["linhas"] if r["atraso"] is not None], key=lambda r: -r["atraso"]
    )[:5]
    podium = ", ".join(f"**{r['dezena']:02d}**" for r in top[:7])

    return f"""# Dezenas quentes — {cfg['nome']} (HEAT v1)

**Corte:** concurso {calc['ultimo_concurso']} ({calc['ultima_data']}) · histórico de
{calc['n_concursos']} concursos · universo 1–{cfg['N']} · esperado por dezena na janela de 100:
{num(calc['esperado_base'])}.

**Pódio de calor (7 primeiras):** {podium}

## Top 10 quentes

{tabela(calc, 10)}

## Top 10 frias

{tabela(calc, 10, invertido=True)}

## Em alta (momentum = z₁₀ − z₁₀₀)

{", ".join(f"**{r['dezena']:02d}** ({num(r['momentum'])})" for r in em_alta)}

## Em queda

{", ".join(f"**{r['dezena']:02d}** ({num(r['momentum'])})" for r in em_queda)}

## Dezenas "devendo" (maior atraso) — informativo, não entra no HEAT

{", ".join(f"**{r['dezena']:02d}** ({r['atraso']} concursos)" for r in devendo)}

---

*Leitura honesta:* o HEAT ordena o passado, não prevê o futuro. Em {cfg['N']} dezenas,
diferenças de frequência dessa magnitude são compatíveis com sorteio justo — a chance de
cada dezena no próximo concurso continua sendo 7/{cfg['N']} = {num(calc['p'] * 100, 2)}%.
"""


def bloco_dados(chave: str, calc_jogos: list[dict], janela: int) -> str:
    """Bloco compacto para colar no prompt."""
    recorte = calc_jogos[-janela:]
    linhas = ["concurso;data;" + ";".join(f"d{i}" for i in range(1, 8))]
    for j in recorte:
        linhas.append(f"{j['concurso']};{j['data']};" + ";".join(f"{d:02d}" for d in j["dezenas"]))
    return "\n".join(linhas)


def main() -> None:
    ap = argparse.ArgumentParser(description="Mapa de calor (HEAT v1) das Loterias Caixa")
    ap.add_argument("--jogo", choices=list(JOGOS) + ["ambos"], default="ambos")
    ap.add_argument("--janela", type=int, default=100, help="janela base (padrão 100)")
    ap.add_argument("--salvar", action="store_true", help="grava quentes-<jogo>.md")
    ap.add_argument("--exportar-dados", action="store_true",
                    help="imprime o bloco de dados para colar no prompt e encerra")
    args = ap.parse_args()

    chaves = list(JOGOS) if args.jogo == "ambos" else [args.jogo]
    saida = []
    for chave in chaves:
        jogos = carregar(chave)
        if args.exportar_dados:
            print(f"### DADOS — {JOGOS[chave]['nome']} (últimos {args.janela} concursos)\n")
            print(bloco_dados(chave, jogos, args.janela))
            print()
            continue
        calc = calcular(jogos, JOGOS[chave]["N"], args.janela)
        md = resumo_md(chave, calc)
        saida.append(md)
        if args.salvar:
            (RAIZ / f"quentes-{chave}.md").write_text(md, encoding="utf-8")

    if not args.exportar_dados:
        texto = "\n\n---\n\n".join(saida)
        print(texto)
        if args.salvar:
            print("\nArquivos quentes-<jogo>.md gravados.")


if __name__ == "__main__":
    main()
