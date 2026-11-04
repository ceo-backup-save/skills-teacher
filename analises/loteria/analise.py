#!/usr/bin/env python3
"""
Análise de padrões de repetição e frequência: DIA DE SORTE x TIMEMANIA
=====================================================================

Somente biblioteca padrão (sem numpy/scipy). Onde a distribuição nula é
conhecida exatamente (hipergeométrica, qui-quadrado) usa-se a fórmula; onde
não é (máximo de frequência, correlação entre jogos, "dezenas quentes"),
usa-se SIMULAÇÃO DE MONTE CARLO.

Uso:
    python3 analise.py            # calcula tudo e grava resultados.json
"""

from __future__ import annotations

import datetime as dt
import json
import math
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados"
JANELA = 100          # "últimos 100 jogos"
SEMENTE = 20261104

JOGOS = {
    "dia-de-sorte": {
        "nome": "Dia de Sorte",
        "universo": 31,
        "dezenas": 7,
        "arquivo": "dia-de-sorte.json",
        "extra": None,
    },
    "timemania": {
        "nome": "Timemania",
        "universo": 80,
        "dezenas": 7,
        "arquivo": "timemania.json",
        "extra": "time_do_coracao",
    },
}

# Correção de dados: o concurso 1307 da Timemania (19/03/2019) veio da fonte
# com 8 dezenas ("54" indevida). Conferido contra uma segunda fonte
# independente (guilhermeasn/loteria.json), que traz exatamente as outras 7.
CORRECOES = {("timemania", 1307): {"remover": 54}}


# --------------------------------------------------------------------------
# distribuições
# --------------------------------------------------------------------------
def comb(n: int, k: int) -> float:
    return float(math.comb(n, k)) if 0 <= k <= n else 0.0


def hipergeometrica(n: int, K: int, k: int) -> float:
    """P(exatamente k repetidas) entre dois sorteios de K dezenas em n."""
    return comb(K, k) * comb(n - K, K - k) / comb(n, K)


def _gammq(a: float, x: float) -> float:
    """Gamma incompleta regularizada Q(a,x) (Numerical Recipes, sem scipy)."""
    if x <= 0:
        return 1.0
    if x < a + 1.0:  # série para P
        ap, soma, delta = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1.0
            delta *= x / ap
            soma += delta
            if abs(delta) < abs(soma) * 1e-12:
                break
        return 1.0 - soma * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # fração continuada para Q
    b = x + 1.0 - a
    c = 1e300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(x: float, gl: int) -> float:
    """P(Chi2_gl > x)."""
    return _gammq(gl / 2.0, x / 2.0)


def p_mc(observado: float, nulos: list[float], bicaudal: bool = True) -> float:
    if bicaudal:
        centro = sum(nulos) / len(nulos)
        alvo = abs(observado - centro)
        return (sum(abs(v - centro) >= alvo for v in nulos) + 1) / (len(nulos) + 1)
    return (sum(v >= observado for v in nulos) + 1) / (len(nulos) + 1)


# --------------------------------------------------------------------------
# estatística descritiva
# --------------------------------------------------------------------------
def media_dp(xs: list[float]) -> tuple[float, float]:
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(v)


def chi2_uniforme(contagens: list[int], esperado: float) -> float:
    return sum((c - esperado) ** 2 / esperado for c in contagens)


def fisher_pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


def ranking(xs: list[float]) -> list[float]:
    ordem = sorted(range(len(xs)), key=lambda i: xs[i])
    postos = [0.0] * len(xs)
    i = 0
    while i < len(ordem):
        j = i
        while j + 1 < len(ordem) and xs[ordem[j + 1]] == xs[ordem[i]]:
            j += 1
        posto = (i + j) / 2 + 1
        for t in range(i, j + 1):
            postos[ordem[t]] = posto
        i = j + 1
    return postos


def spearman(xs: list[float], ys: list[float]) -> float:
    return fisher_pearson(ranking(xs), ranking(ys))


# --------------------------------------------------------------------------
# carga e validação
# --------------------------------------------------------------------------
def carregar(chave: str, cfg: dict) -> tuple[list[dict], list[str]]:
    bruto = json.loads((DADOS / cfg["arquivo"]).read_text(encoding="utf-8"))
    universo, k = cfg["universo"], cfg["dezenas"]
    avisos: list[str] = []
    jogos = []
    for r in bruto:
        dez = [int(x) for x in r["resultado"]]
        corr = CORRECOES.get((chave, r["concurso"]))
        if corr and corr.get("remover") in dez:
            alvo = corr["remover"]
            dez = [d for d in dez if d != alvo]
            avisos.append(f"concurso {r['concurso']}: dezena {alvo} removida (erro da fonte)")
        if len(set(dez)) != k:
            avisos.append(f"concurso {r['concurso']}: {len(set(dez))} dezenas, ignorado")
            continue
        if not all(1 <= d <= universo for d in dez):
            avisos.append(f"concurso {r['concurso']}: fora do universo, ignorado")
            continue
        jogos.append(
            {
                "concurso": r["concurso"],
                "data": r["data"],
                "dt": dt.datetime.strptime(r["data"], "%d/%m/%Y").date(),
                "dezenas": sorted(dez),
                "extra": r.get(cfg["extra"]) if cfg["extra"] else None,
            }
        )
    jogos.sort(key=lambda j: j["concurso"])
    return jogos, avisos


# --------------------------------------------------------------------------
# métricas
# --------------------------------------------------------------------------
def metricas(jogos: list[dict], universo: int, k: int) -> dict:
    contagens = [0] * universo
    for j in jogos:
        for d in j["dezenas"]:
            contagens[d - 1] += 1
    return {
        "n": len(jogos),
        "contagens": contagens,
        "somas": [sum(j["dezenas"]) for j in jogos],
        "impares": [sum(1 for d in j["dezenas"] if d % 2) for j in jogos],
        "consecutivos": [
            sum(1 for a, b in zip(j["dezenas"], j["dezenas"][1:]) if b - a == 1)
            for j in jogos
        ],
        "colunas": [[j["dezenas"][p] for j in jogos] for p in range(k)],
    }


def resumo(met: dict, universo: int, k: int) -> dict:
    med_soma, dp_soma = media_dp(met["somas"])
    med_imp, dp_imp = media_dp(met["impares"])
    cons = met["consecutivos"]
    return {
        "soma_media": med_soma,
        "soma_dp": dp_soma,
        "soma_min": min(met["somas"]),
        "soma_max": max(met["somas"]),
        "soma_teorica": k * (universo + 1) / 2,
        "impares_media": med_imp,
        "impares_dp": dp_imp,
        "impares_hist": [met["impares"].count(i) for i in range(k + 1)],
        "consecutivos_media": sum(cons) / len(cons),
        "consecutivos_hist": [cons.count(i) for i in range(5)],
    }


def teste_frequencias(contagens: list[int], n: int, universo: int, k: int,
                      rng: random.Random, nsim_max: int, nsim_chi: int = 0) -> dict:
    esperado = n * k / universo
    obs_chi2 = chi2_uniforme(contagens, esperado)
    usados = sum(1 for c in contagens if c > 0)
    p_chi2 = chi2_sf(obs_chi2, universo - 1)

    # nulo por Monte Carlo para o máximo observado (teste das "dezenas quentes")
    nulos_max = []
    for _ in range(nsim_max):
        c = [0] * universo
        for _ in range(n):
            for d in rng.sample(range(universo), k):
                c[d] += 1
        nulos_max.append(max(c))
    obs_max, obs_min = max(contagens), min(contagens)
    amplitude = obs_max - obs_min
    nulos_ampl = []
    for _ in range(nsim_max):
        c = [0] * universo
        for _ in range(n):
            for d in rng.sample(range(universo), k):
                c[d] += 1
        nulos_ampl.append(max(c) - min(c))

    ordem = sorted(range(universo), key=lambda i: -contagens[i])
    p_por_dezena = k / universo
    return {
        "esperado": esperado,
        "chi2": obs_chi2,
        "chi2_gl": universo - 1,
        "chi2_p": p_chi2,
        "dezenas_usadas": usados,
        "max": obs_max,
        "min": obs_min,
        "max_p": p_mc(obs_max, nulos_max, bicaudal=False),
        "max_nulo": sum(nulos_max) / len(nulos_max),
        "amplitude": amplitude,
        "amplitude_p": p_mc(amplitude, nulos_ampl, bicaudal=False),
        "quentes": [
            {
                "dezena": i + 1,
                "n": contagens[i],
                "desvio": (contagens[i] - esperado) / math.sqrt(esperado * (1 - p_por_dezena)),
            }
            for i in ordem[:10]
        ],
        "frias": [{"dezena": i + 1, "n": contagens[i]} for i in ordem[-10:][::-1]],
    }


def teste_repeticoes(jogos: list[dict], universo: int, k: int,
                     rng: random.Random, nsim: int) -> dict:
    """Quantas dezenas repetem do concurso anterior e se isso foge do esperado."""
    reps = [len(set(a["dezenas"]) & set(b["dezenas"])) for a, b in zip(jogos, jogos[1:])]
    n = len(reps)
    hist = [reps.count(i) for i in range(k + 1)]
    teorico = [hipergeometrica(universo, k, i) * n for i in range(k + 1)]
    media, dp = media_dp(reps)
    esperado_media = k * k / universo
    p = k / universo
    var_teo = k * p * (1 - p) * (universo - k) / (universo - 1)
    ep = math.sqrt(var_teo / n)
    z = (media - esperado_media) / ep

    # agrupa as caudas para o qui-quadrado (todas as classes com esperado >= 5)
    def agrupar(h):
        bins, acc_o, acc_e = [], 0, 0.0
        for o, e in zip(h, teorico):
            acc_o += o
            acc_e += e
            if acc_e >= 5:
                bins.append([acc_o, acc_e])
                acc_o, acc_e = 0, 0.0
        if acc_e > 0:
            if bins:
                bins[-1][0] += acc_o
                bins[-1][1] += acc_e
            else:
                bins.append([acc_o, acc_e])
        return bins

    bins = agrupar(hist)
    chi2 = sum((o - e) ** 2 / e for o, e in bins)
    gl = len(bins) - 1
    p_chi2 = chi2_sf(chi2, gl)

    nulos = []
    for _ in range(nsim):
        h = [0] * (k + 1)
        ant = None
        for _ in range(n):
            atu = set(rng.sample(range(universo), k))
            if ant is not None:
                h[len(ant & atu)] += 1
            ant = atu
        b = agrupar(h)
        nulos.append(sum((o - e) ** 2 / e for o, e in b))

    destaque = [
        {
            "concurso": b["concurso"],
            "anterior": b["concurso"] - 1,
            "data": b["data"],
            "dezenas": b["dezenas"],
            "repetidas": sorted(set(a["dezenas"]) & set(b["dezenas"])),
        }
        for a, b in zip(jogos, jogos[1:])
        if len(set(a["dezenas"]) & set(b["dezenas"])) >= 4
    ]
    sequencia = [
        {"concurso": b["concurso"], "repetidas": r} for b, r in zip(jogos[1:], reps)
    ]

    return {
        "n_pares": n,
        "hist": hist,
        "hist_pct": [h / n for h in hist],
        "teorico": teorico,
        "media": media,
        "dp": dp,
        "ep": ep,
        "esperado_media": esperado_media,
        "z": z,
        "p_media": math.erfc(abs(z) / math.sqrt(2)),
        "bins": [[o, round(e, 2)] for o, e in bins],
        "chi2": chi2,
        "chi2_gl": gl,
        "chi2_p": p_chi2,
        "chi2_p_mc": p_mc(chi2, nulos, bicaudal=False),
        "p_zero": hist[0] / n,
        "p_zero_teorico": hipergeometrica(universo, k, 0),
        "p_um_ou_mais": 1 - hist[0] / n,
        "p_um_ou_mais_teorico": 1 - hipergeometrica(universo, k, 0),
        "max_rep": max(reps),
        "min_rep": min(reps),
        "destaque": destaque,
        "sequencia": sequencia,
    }


def teste_colunas(jogos: list[dict], universo: int, k: int) -> dict:
    """Estatística de cada coluna (posição da dezena no resultado ordenado).

    A média esperada de cada coluna é a esperança exata da i-ésima estatística
    de ordem de k dezenas sorteadas em 1..universo:
        E[X(i)] = soma_x P(X(i) >= x),  P(X(i) >= x) = P(até i-1 dezenas < x)
    """
    colunas = [[j["dezenas"][p] for j in jogos] for p in range(k)]
    n = len(jogos)
    total = comb(universo, k)
    saida = []
    for pos in range(k):
        i = pos + 1
        e = e2 = 0.0
        for x in range(1, universo + 1):
            prob = sum(comb(x - 1, j) * comb(universo - x + 1, k - j)
                       for j in range(0, i)) / total
            e += prob
            e2 += (2 * x - 1) * prob
        var = e2 - e * e
        ep = math.sqrt(var / n)
        valores = colunas[pos]
        med, dp = media_dp(valores)
        cont: dict[int, int] = {}
        for v in valores:
            cont[v] = cont.get(v, 0) + 1
        top = sorted(cont.items(), key=lambda kv: (-kv[1], kv[0]))
        z = (med - e) / ep if ep else 0.0
        saida.append(
            {
                "coluna": i,
                "media": med,
                "dp": dp,
                "teo_media": e,
                "teo_dp": math.sqrt(var),
                "ep": ep,
                "z": z,
                "p": math.erfc(abs(z) / math.sqrt(2)),
                "min": min(valores),
                "max": max(valores),
                "moda": top[0][0],
                "moda_n": top[0][1],
                "top": [{"dezena": d, "n": c} for d, c in top[:5]],
                "distintas": len(cont),
            }
        )
    return {"colunas": saida}


def teste_quentes(jogos: list[dict], universo: int, k: int, rng: random.Random,
                  janela: int = 20, nsim: int = 60) -> dict:
    """As k dezenas mais frequentes nos 'janela' concursos anteriores acertam mais?"""
    hist_real = [[d - 1 for d in j["dezenas"]] for j in jogos]

    def rodada(hist: list[list[int]]) -> float:
        cont = [0] * universo
        total, n = 0, 0
        for i, dez in enumerate(hist):
            if i >= janela:
                quentes = sorted(range(universo), key=lambda d: -cont[d])[:k]
                total += len(set(quentes) & set(dez))
                n += 1
                for d in hist[i - janela]:
                    cont[d] -= 1
            for d in dez:
                cont[d] += 1
        return total / n if n else 0.0

    obs = rodada(hist_real)
    nulos = [rodada([rng.sample(range(universo), k) for _ in range(len(jogos))])
             for _ in range(nsim)]
    esperado = k * k / universo
    return {
        "janela": janela,
        "media_acertos": obs,
        "esperado": esperado,
        "nulo_media": sum(nulos) / len(nulos),
        "p": p_mc(abs(obs - esperado), [abs(v - esperado) for v in nulos]),
        "n_concursos": len(jogos) - janela,
    }


def teste_atraso(jogos: list[dict], universo: int, k: int) -> dict:
    ultimo = {d: None for d in range(1, universo + 1)}
    chaves = ["1", "2", "3", "4", "5-9", "10+"]
    baldes = {c: [0, 0] for c in chaves}
    for i, j in enumerate(jogos):
        presentes = set(j["dezenas"])
        for d in range(1, universo + 1):
            u = ultimo[d]
            if u is None:
                continue
            gap = i - u
            if gap <= 4:
                chave = str(gap)
            elif gap <= 9:
                chave = "5-9"
            else:
                chave = "10+"
            baldes[chave][1] += 1
            if d in presentes:
                baldes[chave][0] += 1
        for d in j["dezenas"]:
            ultimo[d] = i
    saida = []
    p_esp = k / universo
    for chave in chaves:
        acertos, total = baldes[chave]
        if total:
            p = acertos / total
            ep = math.sqrt(p * (1 - p) / total)
            z = (p - p_esp) / ep
            saida.append({"atraso": chave, "acertos": acertos, "total": total,
                          "p": p, "ep": ep, "z": z,
                          "p_valor": math.erfc(abs(z) / math.sqrt(2))})
        else:
            saida.append({"atraso": chave, "acertos": 0, "total": 0,
                          "p": None, "ep": None, "z": None, "p_valor": None})
    return {"baldes": saida, "esperado": p_esp}


# --------------------------------------------------------------------------
# análise cruzada
# --------------------------------------------------------------------------
def parear(ds: list[dict], tm: list[dict]) -> list[tuple[dict, dict]]:
    """Casa cada concurso da Timemania com o concurso do Dia de Sorte mais
    próximo no calendário (tolerância de 1 dia: a fonte às vezes registra o
    sorteio de sábado com a data de domingo). Cada sorteio é usado uma vez."""
    usados: set[int] = set()
    pares = []
    for t in tm:
        melhor, melhor_chave = None, None
        for i, d in enumerate(ds):
            if i in usados:
                continue
            delta = abs((d["dt"] - t["dt"]).days)
            if delta > 1:
                continue
            chave = (delta, abs(d["concurso"] - t["concurso"]))
            if melhor_chave is None or chave < melhor_chave:
                melhor, melhor_chave = i, chave
        if melhor is not None:
            usados.add(melhor)
            pares.append((ds[melhor], t))
    return pares


def analise_cruzada(pares: list[tuple[dict, dict]], universo_ds: int,
                    rng: random.Random, nsim: int) -> dict:
    """Alinha Dia de Sorte x Timemania por data e mede coincidências."""
    n = len(pares)
    sobre = []
    for a, b in pares:
        sobre.append(len(set(a["dezenas"]) & set(b["dezenas"])))
    media, dp = media_dp(sobre)
    # E[coincidências] = 7 * 7/80: cada dezena do Dia de Sorte (1..31) tem
    # chance 7/80 de estar entre as 7 da Timemania.
    esperado = 7 * 7 / 80
    ep = dp / math.sqrt(n)

    freq_ds = [0] * universo_ds
    freq_tm = [0] * universo_ds
    for a, b in pares:
        for d in a["dezenas"]:
            freq_ds[d - 1] += 1
        for d in b["dezenas"]:
            if d <= universo_ds:
                freq_tm[d - 1] += 1

    r_p = fisher_pearson(freq_ds, freq_tm)
    r_s = spearman(freq_ds, freq_tm)

    nulos_p, nulos_s, nulos_sobre = [], [], []
    for _ in range(nsim):
        f_ds = [0] * universo_ds
        f_tm = [0] * universo_ds
        s_sobre = 0
        for _ in pares:
            a = rng.sample(range(1, universo_ds + 1), 7)
            b = rng.sample(range(1, 81), 7)
            for d in a:
                f_ds[d - 1] += 1
            for d in b:
                if d <= universo_ds:
                    f_tm[d - 1] += 1
            s_sobre += len(set(a) & set(b))
        nulos_p.append(fisher_pearson(f_ds, f_tm))
        nulos_s.append(spearman(f_ds, f_tm))
        nulos_sobre.append(s_sobre / n)

    def top7(freq):
        return {d for d in sorted(range(1, universo_ds + 1), key=lambda d: -freq[d - 1])[:7]}

    q_ds, q_tm = top7(freq_ds), top7(freq_tm)
    p_nenhuma = 1.0
    for i in range(7):
        p_nenhuma *= (80 - 7 - i) / (80 - i)

    return {
        "n_pares": n,
        "primeira_data": pares[0][0]["data"] if n else None,
        "ultima_data": pares[-1][0]["data"] if n else None,
        "concurso_ds_ini": pares[0][0]["concurso"] if n else None,
        "concurso_ds_fim": pares[-1][0]["concurso"] if n else None,
        "concurso_tm_ini": pares[0][1]["concurso"] if n else None,
        "concurso_tm_fim": pares[-1][1]["concurso"] if n else None,
        "sobreposicao_hist": [sobre.count(i) for i in range(8)],
        "sobreposicao_media": media,
        "sobreposicao_dp": dp,
        "sobreposicao_ep": ep,
        "sobreposicao_esperada": esperado,
        "sobreposicao_z": (media - esperado) / ep if ep else 0.0,
        "sobreposicao_p": p_mc(media, nulos_sobre),
        "pelo_menos_uma": sum(1 for s in sobre if s >= 1) / n,
        "pelo_menos_uma_teorico": 1 - p_nenhuma,
        "freq_ds": freq_ds,
        "freq_tm": freq_tm,
        "pearson": r_p,
        "pearson_p": p_mc(r_p, nulos_p),
        "spearman": r_s,
        "spearman_p": p_mc(r_s, nulos_s),
        "quentes_ds": sorted(q_ds),
        "quentes_tm": sorted(q_tm),
        "quentes_interseccao": sorted(q_ds & q_tm),
        "quentes_chance": 7 * 7 / universo_ds,
    }


# --------------------------------------------------------------------------
# orquestração
# --------------------------------------------------------------------------
def main() -> None:
    rng = random.Random(SEMENTE)
    saida = {"gerado_em": "2026-11-04", "janela": JANELA, "jogos": {}}
    cache = {}

    for chave, cfg in JOGOS.items():
        jogos, avisos = carregar(chave, cfg)
        cache[chave] = jogos
        universo, k = cfg["universo"], cfg["dezenas"]
        jan = jogos[-JANELA:]
        m_jan, m_full = metricas(jan, universo, k), metricas(jogos, universo, k)
        print(f"== {cfg['nome']}: {len(jogos)} concursos | janela {jan[0]['concurso']}"
              f"–{jan[-1]['concurso']} ({jan[0]['data']} a {jan[-1]['data']})")

        saida["jogos"][chave] = {
            "nome": cfg["nome"],
            "universo": universo,
            "dezenas_por_jogo": k,
            "total_concursos": len(jogos),
            "avisos": avisos,
            "janela": {
                "de": jan[0]["concurso"], "ate": jan[-1]["concurso"],
                "data_ini": jan[0]["data"], "data_fim": jan[-1]["data"], "n": len(jan),
                "contagens": m_jan["contagens"],
                "resumo": resumo(m_jan, universo, k),
                "frequencias": teste_frequencias(m_jan["contagens"], len(jan), universo, k,
                                                rng, nsim_max=2000),
                "repeticoes": teste_repeticoes(jan, universo, k, rng, nsim=2000),
                "colunas": teste_colunas(jan, universo, k),
                "ultimo_sorteio": jan[-1]["dezenas"],
                "ultimo_concurso": jan[-1]["concurso"],
                "ultima_data": jan[-1]["data"],
                "desenho_sorte": [j["dezenas"] for j in jan],
            },
            "serie_completa": {
                "contagens": m_full["contagens"],
                "resumo": resumo(m_full, universo, k),
                "frequencias": teste_frequencias(m_full["contagens"], len(jogos), universo,
                                                k, rng, nsim_max=400),
                "repeticoes": teste_repeticoes(jogos, universo, k, rng, nsim=400),
                "quentes": teste_quentes(jogos[-800:], universo, k, rng, janela=20, nsim=60),
                "atraso": teste_atraso(jogos, universo, k),
            },
        }

    ds_all, tm_all = cache["dia-de-sorte"], cache["timemania"]
    ds_jan, tm_jan = ds_all[-JANELA:], tm_all[-JANELA:]
    # janela: só o período coberto pelos dois últimos 100 (TM tem 3 sorteios/semana,
    # DS tem 6, então o período comum é o do Dia de Sorte)
    pares_jan = parear(ds_jan, tm_jan[-120:])
    pares_full = parear(ds_all, tm_all)
    saida["cruzada"] = {
        "janela": analise_cruzada(pares_jan, 31, rng, nsim=2000),
        "serie_completa": analise_cruzada(pares_full, 31, rng, nsim=400),
    }

    times = [j["extra"] for j in tm_jan]
    contagem = {t: times.count(t) for t in set(times)}
    saida["jogos"]["timemania"]["janela"]["times"] = {
        "distintos": len(contagem),
        "top": sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))[:5],
    }

    (RAIZ / "resultados.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("OK -> resultados.json")


if __name__ == "__main__":
    main()
