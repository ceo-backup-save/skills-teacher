#!/usr/bin/env python3
"""
Lotofácil — extração determinística dos 100 concursos (Objetivo 01).

Uso:
    python3 lotofacil/extract_lotofacil.py --inicio 3719 --fim 3819

Fonte (ordem de tentativa):
  1. API oficial das Loterias da Caixa:
     https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{concurso}
  2. Espelho público em GitHub (mesmo schema da API oficial), usado quando a
     API oficial não está acessível a partir do ambiente de execução.

Saídas em lotofacil/out/:
  lotofacil_lista_100_concursos.txt  -> "concurso: dd, dd, ..."  (100 linhas)
  lotofacil_lista_repetidas.txt      -> "concurso: dd, dd, ..."  (100 linhas)
  extracao_objetivo01.md             -> as duas listas em bloco de código
  extracao_objetivo01.json           -> dados + atributos por concurso
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out")
CACHE = os.path.join(DATA_DIR, "lotofacil_cache.json")

CAIXA_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{concurso}"
MIRROR_URL = (
    "https://api.github.com/repos/faelw/lotofacil-data/contents/api/lotofacil.json"
)
UA = "Mozilla/5.0 (compatible; lotofacil-extract/1.0)"


def http_json(url, timeout=20, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def normalize(dezenas):
    out = sorted(int(d) for d in dezenas)
    assert len(out) == 15, f"esperado 15 dezenas, veio {len(out)}"
    assert len(set(out)) == 15, "dezenas duplicadas"
    assert all(1 <= d <= 25 for d in out), "dezena fora de 01-25"
    return out


def from_caixa(concurso):
    j = http_json(CAIXA_URL.format(concurso=concurso))
    dezenas = j.get("listaDezenas") or j.get("dezenasSorteadasOrdemSorteio")
    return {
        "concurso": int(j["numero"]),
        "data": j["dataApuracao"],
        "dezenas": normalize(dezenas),
        "fonte": "api-oficial-caixa",
    }


def load_mirror():
    print("[fonte] baixando espelho público (fallback)...", file=sys.stderr)
    dados = http_json(MIRROR_URL, timeout=90, accept="application/vnd.github.raw")
    index = {}
    for j in dados:
        index[int(j["concurso"])] = {
            "concurso": int(j["concurso"]),
            "data": j["data"],
            "dezenas": normalize(j["dezenas"]),
            "fonte": "espelho-github-faelw/lotofacil-data",
        }
    return index


def collect(inicio, fim):
    """Retorna lista de registros de `inicio` a `fim`, em ordem crescente."""
    cache = {}
    if os.path.exists(CACHE):
        cache = {int(k): v for k, v in json.load(open(CACHE)).items()}

    registros = {}
    oficial_ok = True
    for c in range(inicio, fim + 1):
        if c in cache and cache[c].get("fonte") == "api-oficial-caixa":
            registros[c] = cache[c]
            continue
        try:
            registros[c] = from_caixa(c)
            time.sleep(0.15)
        except Exception as exc:  # noqa: BLE001
            oficial_ok = False
            print(f"[aviso] API oficial indisponível no concurso {c}: {exc}", file=sys.stderr)
            break

    if not oficial_ok or len(registros) < (fim - inicio + 1):
        espelho = load_mirror()
        for c in range(inicio, fim + 1):
            if c not in registros:
                if c not in espelho:
                    raise SystemExit(f"[erro] concurso {c} ausente no espelho")
                registros[c] = espelho[c]

    for c, r in registros.items():
        cache.setdefault(str(c), r)
    os.makedirs(DATA_DIR, exist_ok=True)
    json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=0)

    return [registros[c] for c in sorted(registros)]


def fmt(dezenas):
    return ", ".join(f"{d:02d}" for d in dezenas)


def validar(registros, inicio, fim):
    esperado = list(range(inicio, fim + 1))
    obtido = [r["concurso"] for r in registros]
    assert obtido == esperado, "janela de concursos incompleta ou fora de ordem"
    for r in registros:
        normalize(r["dezenas"])
        assert isinstance(r["data"], str) and len(r["data"]) == 10, f"data inválida em {r['concurso']}"
    anos = {r["data"][-4:] for r in registros}
    assert anos == {"2026"}, f"ano fora da janela esperada: {anos}"
    print(f"[ok] {len(registros)} concursos validados ({inicio}-{fim})", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", type=int, default=3719,
                    help="primeiro concurso (inclui o anterior à janela, para as repetidas)")
    ap.add_argument("--fim", type=int, default=3819)
    args = ap.parse_args()

    registros = collect(args.inicio, args.fim)
    validar(registros, args.inicio, args.fim)

    janela = [r for r in registros if r["concurso"] > args.inicio]
    anterior = {r["concurso"]: set(r["dezenas"]) for r in registros}

    linhas_jogos, linhas_rep, detalhe = [], [], []
    for r in janela:
        c = r["concurso"]
        rep = [d for d in r["dezenas"] if d in anterior[c - 1]]
        linhas_jogos.append(f"{c}: {fmt(r['dezenas'])}")
        linhas_rep.append(f"{c}: {fmt(rep)}" if rep else f"{c}: (sem repetidas)")
        detalhe.append({
            "concurso": c,
            "data": r["data"],
            "dezenas": r["dezenas"],
            "repetidas": rep,
            "qtd_repetidas": len(rep),
            "fonte": r["fonte"],
        })

    os.makedirs(OUT_DIR, exist_ok=True)
    p1 = os.path.join(OUT_DIR, "lotofacil_lista_100_concursos.txt")
    p2 = os.path.join(OUT_DIR, "lotofacil_lista_repetidas.txt")
    open(p1, "w").write("\n".join(linhas_jogos) + "\n")
    open(p2, "w").write("\n".join(linhas_rep) + "\n")

    meta = {
        "universo": f"{janela[0]['concurso']}-{janela[-1]['concurso']}",
        "n": len(janela),
        "primeira_data": janela[0]["data"],
        "ultima_data": janela[-1]["data"],
        "concursos": detalhe,
    }
    json.dump(meta, open(os.path.join(OUT_DIR, "extracao_objetivo01.json"), "w"),
              ensure_ascii=False, indent=1)

    md = [
        "# Extração Objetivo 01 — 100 concursos da Lotofácil",
        "",
        f"- Universo: **{meta['universo']}** ({meta['n']} concursos)",
        f"- Janela: {meta['primeira_data']} a {meta['ultima_data']}",
        f"- Fontes: {sorted({r['fonte'] for r in janela})}",
        "",
        "## Lista 1 — concursos e dezenas",
        "",
        "```",
        *linhas_jogos,
        "```",
        "",
        "## Lista 2 — repetidas do concurso anterior",
        "",
        "```",
        *linhas_rep,
        "```",
        "",
        f"Total de linhas: {len(linhas_jogos)} | {len(linhas_rep)}",
        "",
    ]
    open(os.path.join(OUT_DIR, "extracao_objetivo01.md"), "w").write("\n".join(md))

    print(f"[ok] {len(linhas_jogos)} linhas -> {p1}")
    print(f"[ok] {len(linhas_rep)} linhas -> {p2}")


if __name__ == "__main__":
    main()
