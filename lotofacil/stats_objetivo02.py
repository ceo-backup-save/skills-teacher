#!/usr/bin/env python3
"""
Lotofácil — Objetivo 02: estatística dos 100 concursos (3720-3819).

Indicadores (conforme template da página Lotofacil-Objetivo2):
  Pares/ímpares, Baixas/altas, Borda/miolo, Duplas exatas, Trios exatos,
  Quadras exatas, Maior sequência, Repetidas do anterior, Total de grupos,
  Pares adjacentes, Soma das 15 dezenas.

Saída: out/estatistica_objetivo02.json + relatório markdown/TSV por indicador.
"""

import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "resultados")

BAIXAS = set(range(1, 14))
ALTAS = set(range(14, 26))
BORDA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
MIOLO = {7, 8, 9, 12, 13, 14, 17, 18, 19}


def blocos(dezenas):
    """Blocos máximos de dezenas consecutivas (>=2)."""
    out, atual = [], [dezenas[0]]
    for d in dezenas[1:]:
        if d == atual[-1] + 1:
            atual.append(d)
        else:
            out.append(atual)
            atual = [d]
    out.append(atual)
    return [b for b in out if len(b) >= 2]


def pares_adjacentes(dezenas):
    """Cada bloco de tamanho k contribui com k-1 pares adjacentes."""
    return sum(len(b) - 1 for b in blocos(dezenas))


def volante_grupos(dezenas):
    """Grupos = 5 linhas + 5 colunas do volante 5x5; conta os com >=2 dezenas."""
    s = set(dezenas)
    linhas = [set(range(i * 5 + 1, i * 5 + 6)) for i in range(5)]
    colunas = [{i + 1 + 5 * j for j in range(5)} for i in range(5)]
    return {
        "linhas": sum(1 for g in linhas if len(g & s) >= 2),
        "colunas": sum(1 for g in colunas if len(g & s) >= 2),
        "total": sum(1 for g in linhas + colunas if len(g & s) >= 2),
    }


def cluster_volante(dezenas):
    """Alternativa: agrupamentos conexos (8-vizinhos) contando só os de 2+ dezenas."""
    s = set(dezenas)
    vistos, clusters = set(), []
    for d in sorted(s):
        if d in vistos:
            continue
        pilha, comp = [d], []
        vistos.add(d)
        while pilha:
            x = pilha.pop()
            comp.append(x)
            r, c = divmod(x - 1, 5)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 5 and 0 <= cc < 5:
                        y = rr * 5 + cc + 1
                        if y in s and y not in vistos:
                            vistos.add(y)
                            pilha.append(y)
        clusters.append(comp)
    return sum(1 for c in clusters if len(c) >= 2)


def indicadores(concursos):
    """concursos: lista de dicts {concurso, dezenas, repetidas}."""
    rows = []
    for c in concursos:
        d = sorted(c["dezenas"])
        b = blocos(d)
        g = volante_grupos(d)
        rows.append({
            "concurso": c["concurso"],
            "pares": sum(1 for x in d if x % 2 == 0),
            "impares": sum(1 for x in d if x % 2 == 1),
            "baixas": sum(1 for x in d if x in BAIXAS),
            "altas": sum(1 for x in d if x in ALTAS),
            "borda": sum(1 for x in d if x in BORDA),
            "miolo": sum(1 for x in d if x in MIOLO),
            "duplas": sum(1 for x in b if len(x) == 2),
            "trios": sum(1 for x in b if len(x) == 3),
            "quadras": sum(1 for x in b if len(x) == 4),
            "quinas_mais": sum(1 for x in b if len(x) >= 5),
            "maior_sequencia": max((len(x) for x in b), default=1),
            "repetidas": len(c["repetidas"]),
            "grupos_linhas": g["linhas"],
            "grupos_colunas": g["colunas"],
            "grupos_total": g["total"],
            "clusters_2mais": cluster_volante(d),
            "pares_adjacentes": pares_adjacentes(d),
            "soma": sum(d),
        })
    return rows


def faixa_prevalente(freq, total, alvo=0.70):
    """Valores em ordem decrescente de frequência até acumular >= alvo.

    Retorna (valores_ordenados, casos, pct, pct_acum).
    """
    ordenado = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    sel, casos = [], 0
    for valor, n in ordenado:
        sel.append((valor, n))
        casos += n
        if casos / total >= alvo:
            break
    return sel, casos, casos / total


def faixa_nao_prevalente(freq, total, excluidos, limiar=0.30):
    """Valores com frequência individual < limiar e fora da faixa prevalente."""
    sel = [(v, n) for v, n in sorted(freq.items())
           if v not in excluidos and n / total < limiar]
    return sel, sum(n for _, n in sel), sum(n for _, n in sel) / total


def resumo_contagem(rows, campo, total, rotulo):
    freq = Counter(r[campo] for r in rows)
    prevalentes, casos_a, pct_a = faixa_prevalente(freq, total)
    valores_a = {v for v, _ in prevalentes}
    cauda, casos_b, pct_b = faixa_nao_prevalente(freq, total, valores_a)
    det = {
        "indicador": rotulo,
        "campo": campo,
        "distribuicao": dict(sorted(freq.items())),
        "faixa_A_valores": sorted(valores_a),
        "faixa_A_texto": None,
        "faixa_A_casos": casos_a,
        "faixa_A_pct": round(pct_a * 100, 1),
        "faixa_B_valores": [v for v, _ in cauda],
        "faixa_B_casos": casos_b,
        "faixa_B_pct": round(pct_b * 100, 1),
        "faixa_B_detalhe": [{"valor": v, "casos": n, "pct": round(n / total * 100, 1)}
                            for v, n in cauda],
    }
    return det


def faixa_contigua(valores):
    return f"{min(valores)}–{max(valores)}"


def main():
    dados = json.load(open(os.path.join(OUT, "extracao_objetivo01.json")))
    concursos = dados["concursos"]
    total = len(concursos)
    rows = indicadores(concursos)

    contagens = [
        ("pares", "Pares / ímpares"),
        ("baixas", "Baixas / altas"),
        ("borda", "Borda / miolo"),
        ("duplas", "Duplas exatas"),
        ("trios", "Trios exatos"),
        ("quadras", "Quadras exatas"),
        ("maior_sequencia", "Maior sequência"),
        ("repetidas", "Repetidas do anterior"),
        ("grupos_total", "Total de grupos (linhas+colunas)"),
        ("pares_adjacentes", "Pares adjacentes"),
    ]
    saida = {"universo": dados["universo"], "n": total, "indicadores": []}
    for campo, rotulo in contagens:
        det = resumo_contagem(rows, campo, total, rotulo)
        det["faixa_A_texto"] = faixa_contigua(det["faixa_A_valores"])
        saida["indicadores"].append(det)

    # Soma: faixas por amplitude (largura 10) + faixa contígua acumulada
    somas = sorted(r["soma"] for r in rows)
    bins = Counter((s // 10) * 10 for r in rows for s in [r["soma"]])
    det_soma = {
        "indicador": "Soma das 15 dezenas",
        "campo": "soma",
        "min": somas[0],
        "max": somas[-1],
        "media": round(sum(somas) / total, 1),
        "distribuicao_bins_10": {f"{k}–{k+9}": bins[k] for k in sorted(bins)},
    }
    # faixa contígua de soma que cobre >=70%
    melhor = None
    for i, lo in enumerate(somas):
        casos = 0
        for hi in somas[i:]:
            casos = sum(1 for s in somas if lo <= s <= hi)
            if casos / total >= 0.70:
                if melhor is None or (hi - lo) < (melhor[1] - melhor[0]):
                    melhor = (lo, hi, casos)
                break
    det_soma["faixa_A_texto"] = faixa_contigua([melhor[0], melhor[1]])
    det_soma["faixa_A_casos"] = melhor[2]
    det_soma["faixa_A_pct"] = round(melhor[2] / total * 100, 1)
    cauda = [s for s in somas if not (melhor[0] <= s <= melhor[1])]
    det_soma["faixa_B_texto"] = "extremos fora da faixa A"
    det_soma["faixa_B_casos"] = len(cauda)
    det_soma["faixa_B_pct"] = round(len(cauda) / total * 100, 1)
    det_soma["faixa_B_extremos"] = (
        f"{cauda[0]}–{cauda[0]} e {cauda[-1]}–{cauda[-1]}" if cauda else "—")
    saida["indicadores"].append(det_soma)

    json.dump({"resumo": saida, "por_concurso": rows},
              open(os.path.join(OUT, "estatistica_objetivo02.json"), "w"),
              ensure_ascii=False, indent=1)

    for det in saida["indicadores"]:
        print(f"\n== {det['indicador']}")
        if "distribuicao" in det:
            print("  dist:", det["distribuicao"])
            print(f"  A: {det['faixa_A_texto']} -> {det['faixa_A_casos']} ({det['faixa_A_pct']}%)")
            print(f"  B: {det['faixa_B_valores']} -> {det['faixa_B_casos']} ({det['faixa_B_pct']}%)")
        else:
            print("  min/max/media:", det["min"], det["max"], det["media"])
            print("  bins10:", det["distribuicao_bins_10"])
            print(f"  A: {det['faixa_A_texto']} -> {det['faixa_A_casos']} ({det['faixa_A_pct']}%)")
            print(f"  B: {det['faixa_B_casos']} ({det['faixa_B_pct']}%) extremos {det['faixa_B_extremos']}")

    print("\n== grupos (definições alternativas)")
    print(" grupos_total dist:", dict(sorted(Counter(r["grupos_total"] for r in rows).items())))
    print(" clusters_2mais dist:", dict(sorted(Counter(r["clusters_2mais"] for r in rows).items())))
    print(" linhas dist:", dict(sorted(Counter(r["grupos_linhas"] for r in rows).items())))
    print(" quinas_mais dist:", dict(sorted(Counter(r["quinas_mais"] for r in rows).items())))
    print(" soma min/max:", somas[0], somas[-1])


if __name__ == "__main__":
    main()
