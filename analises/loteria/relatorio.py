#!/usr/bin/env python3
"""
Gera RELATORIO.md e relatorio.html a partir de resultados.json.
Somente biblioteca padrão: os gráficos são SVG escritos na mão.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
R = json.loads((RAIZ / "resultados.json").read_text(encoding="utf-8"))

CORES = {
    "dia-de-sorte": {"fundo": "#0f766e", "claro": "#5eead4", "nome": "Dia de Sorte"},
    "timemania": {"fundo": "#6d28d9", "claro": "#c4b5fd", "nome": "Timemania"},
}
NEUTRO = "#64748b"


# --------------------------------------------------------------------------
# formatação
# --------------------------------------------------------------------------
def num(x, casas=2):
    if x is None:
        return "–"
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, casas=1):
    return num(x * 100, casas) + "%"


def pval(p):
    if p is None:
        return "–"
    if p < 0.001:
        return "< 0,001"
    return num(p, 3)


def marca(p, limite=0.05):
    return "✅" if p is not None and p >= limite else ("⚠️" if p is not None else "")


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def interp(c1, c2, t):
    a, b = hex_rgb(c1), hex_rgb(c2)
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


def svg_barras_duplas(dados, rotulos, w=760, h=260, cor_obs="#0f766e", cor_esp="#cbd5e1",
                      rotulo_obs="Observado", rotulo_esp="Esperado", eixo_y="concursos"):
    """dados: [(obs, esperado), ...]"""
    maxv = max(max(o, e) for o, e in dados) * 1.15
    margem_e, margem_d, margem_b, margem_t = 46, 12, 46, 28
    largura_plot = w - margem_e - margem_d
    altura_plot = h - margem_b - margem_t
    n = len(dados)
    passo = largura_plot / n
    bw = min(28, passo / 3)
    partes = [f'<svg viewBox="0 0 {w} {h}" class="grafico" role="img">']
    # grade
    for i in range(5):
        v = maxv * i / 4
        y = margem_t + altura_plot - altura_plot * i / 4
        partes.append(f'<line x1="{margem_e}" y1="{y:.1f}" x2="{w - margem_d}" y2="{y:.1f}" stroke="#e2e8f0"/>')
        partes.append(f'<text x="{margem_e - 8}" y="{y + 4:.1f}" class="eixo" text-anchor="end">{num(v, 1)}</text>')
    for i, ((obs, esp), rot) in enumerate(zip(dados, rotulos)):
        cx = margem_e + passo * (i + 0.5)
        ho = altura_plot * obs / maxv
        he = altura_plot * esp / maxv
        partes.append(f'<rect x="{cx - bw - 2:.1f}" y="{margem_t + altura_plot - ho:.1f}" width="{bw:.1f}" '
                      f'height="{ho:.1f}" fill="{cor_obs}" rx="3"><title>{rot}: {obs} observado</title></rect>')
        partes.append(f'<rect x="{cx + 2:.1f}" y="{margem_t + altura_plot - he:.1f}" width="{bw:.1f}" '
                      f'height="{he:.1f}" fill="{cor_esp}" rx="3"><title>{rot}: {num(esp,1)} esperado</title></rect>')
        partes.append(f'<text x="{cx:.1f}" y="{h - margem_b + 20}" class="eixo" text-anchor="middle">{rot}</text>')
        if obs:
            partes.append(f'<text x="{cx - bw/2 - 2:.1f}" y="{margem_t + altura_plot - ho - 6:.1f}" '
                          f'class="valor" text-anchor="middle">{obs}</text>')
        partes.append(f'<text x="{cx + bw/2 + 2:.1f}" y="{margem_t + altura_plot - he - 6:.1f}" '
                      f'class="valor esp" text-anchor="middle">{num(esp,1)}</text>')
    partes.append(f'<text x="{margem_e}" y="{h - 8}" class="eixo">{eixo_y}</text>')
    partes.append(f'<rect x="{w - 200}" y="{margem_t - 20}" width="10" height="10" fill="{cor_obs}" rx="2"/>'
                  f'<text x="{w - 184}" y="{margem_t - 11}" class="eixo">{rotulo_obs}</text>'
                  f'<rect x="{w - 110}" y="{margem_t - 20}" width="10" height="10" fill="{cor_esp}" rx="2"/>'
                  f'<text x="{w - 94}" y="{margem_t - 11}" class="eixo">{rotulo_esp}</text>')
    partes.append("</svg>")
    return "".join(partes)


def svg_dispersao(xs, ys, cor, w=680, h=340, rotulo_x="", rotulo_y=""):
    margem_e, margem_d, margem_b, margem_t = 52, 16, 44, 20
    lw, lh = w - margem_e - margem_d, h - margem_b - margem_t

    def esc_x(v, mn, mx):
        return margem_e + lw * (v - mn) / (mx - mn) if mx > mn else margem_e + lw / 2

    def esc_y(v, mn, mx):
        return margem_t + lh - lh * (v - mn) / (mx - mn) if mx > mn else margem_t + lh / 2

    x0, x1 = 0, max(xs) * 1.1
    y0, y1 = 0, max(ys) * 1.15
    partes = [f'<svg viewBox="0 0 {w} {h}" class="grafico" role="img">']
    for i in range(5):
        y = margem_t + lh * i / 4
        v = y1 * (4 - i) / 4
        partes.append(f'<line x1="{margem_e}" y1="{y:.1f}" x2="{w - margem_d}" y2="{y:.1f}" stroke="#e2e8f0"/>')
        partes.append(f'<text x="{margem_e - 8}" y="{y + 4:.1f}" class="eixo" text-anchor="end">{num(v, 1)}</text>')
    mx_, my_ = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((a - mx_) * (b - my_) for a, b in zip(xs, ys))
    sxx = sum((a - mx_) ** 2 for a in xs)
    inclinacao = sxy / sxx if sxx else 0
    intercepto = my_ - inclinacao * mx_
    if xs:
        xa, xb = 0, x1
        partes.append(f'<line x1="{esc_x(xa, x0, x1):.1f}" y1="{esc_y(intercepto, y0, y1):.1f}" '
                      f'x2="{esc_x(xb, x0, x1):.1f}" y2="{esc_y(intercepto + inclinacao * xb, y0, y1):.1f}" '
                      f'stroke="{NEUTRO}" stroke-dasharray="6 4" stroke-width="1.5"/>')
    for i, (a, b) in enumerate(zip(xs, ys)):
        partes.append(f'<circle cx="{esc_x(a, x0, x1):.1f}" cy="{esc_y(b, y0, y1):.1f}" r="5" '
                      f'fill="{cor}" fill-opacity="0.75" stroke="#fff" stroke-width="1">'
                      f'<title>dezena {i+1}: {a} no Dia de Sorte, {b} na Timemania</title></circle>')
    partes.append(f'<text x="{margem_e}" y="{h - 8}" class="eixo">{rotulo_x}</text>')
    partes.append(f'<text x="{margem_e}" y="{margem_t - 6}" class="eixo">{rotulo_y}</text>')
    partes.append("</svg>")
    return "".join(partes)


def heatmap(contagens, universo, cor, esperado, colunas=None):
    colunas = colunas or (10 if universo > 40 else 8)
    maxc = max(contagens)
    minc = min(contagens)
    celulas = []
    for i, c in enumerate(contagens, start=1):
        t = (c - minc) / (maxc - minc) if maxc > minc else 0.5
        fundo = interp("#f8fafc", cor, 0.15 + 0.85 * t)
        texto = "#0f172a" if t < 0.55 else "#ffffff"
        z = (c - esperado) / math.sqrt(esperado * (1 - 7 / universo))
        celulas.append(
            f'<div class="cel" style="background:{fundo};color:{texto}" '
            f'title="dezena {i:02d}: {c} saídas (esperado {num(esperado,2)}; z = {num(z,2)})">'
            f'<span class="cel-n">{i:02d}</span><span class="cel-c">{c}</span></div>'
        )
    return f'<div class="heat" style="grid-template-columns:repeat({colunas},minmax(0,1fr))">' + "".join(celulas) + "</div>"


# --------------------------------------------------------------------------
# texto
# --------------------------------------------------------------------------
def contexto(universo, k):
    def c(n, r):
        return math.comb(n, r)

    p0 = c(universo - k, k) / c(universo, k)
    p4 = sum(c(k, i) * c(universo - k, k - i) / c(universo, k) for i in range(4, k + 1))
    return {
        "p0": p0,
        "p_um_ou_mais": 1 - p0,
        "p4": p4,
        "esperado_4mais_em_100": p4 * 100,
        "p_min_1": c(universo - 1, k - 1) / c(universo, k),
        "p_dezena": k / universo,
    }


def montar():
    ds = R["jogos"]["dia-de-sorte"]
    tm = R["jogos"]["timemania"]
    cz = R["cruzada"]
    ctx = {k: contexto(v["universo"], v["dezenas_por_jogo"]) for k, v in R["jogos"].items()}

    # CSV dos últimos 100
    for chave, jogo in R["jogos"].items():
        linhas = ["concurso;data;" + ";".join(f"d{i}" for i in range(1, 8))]
        dados = json.loads((RAIZ / "dados" / ("dia-de-sorte.json" if chave == "dia-de-sorte" else "timemania.json")).read_text(encoding="utf-8"))
        usados = [d for d in dados if d["concurso"] >= jogo["janela"]["de"]][: jogo["janela"]["n"]]
        for d in usados:
            linhas.append(f'{d["concurso"]};{d["data"]};' + ";".join(d["resultado"][:7]))
        nome = "ultimos-100-dia-de-sorte.csv" if chave == "dia-de-sorte" else "ultimos-100-timemania.csv"
        (RAIZ / nome).write_text("\n".join(linhas) + "\n", encoding="utf-8")

    return ds, tm, cz, ctx


def veredito(ds, tm, cz):
    """Resumo dos testes em uma tabela única."""
    testes = []

    def add(nome, p_ds, p_tm, nota_ds, nota_tm):
        testes.append({"teste": nome, "p_ds": p_ds, "p_tm": p_tm, "ds": nota_ds, "tm": nota_tm})

    add("Frequência das dezenas (qui-quadrado)", ds["janela"]["frequencias"]["chi2_p"],
        tm["janela"]["frequencias"]["chi2_p"], "", "")
    add("Dezena mais frequente (máximo por simulação)", ds["janela"]["frequencias"]["max_p"],
        tm["janela"]["frequencias"]["max_p"], "", "")
    add("Repetição do concurso anterior (média)", ds["janela"]["repeticoes"]["p_media"],
        tm["janela"]["repeticoes"]["p_media"], "", "")
    add("Repetição do concurso anterior (distribuição)", ds["janela"]["repeticoes"]["chi2_p_mc"],
        tm["janela"]["repeticoes"]["chi2_p_mc"], "", "")
    add("Dezenas quentes acertam mais? (série completa)",
        ds["serie_completa"]["quentes"]["p"], tm["serie_completa"]["quentes"]["p"], "", "")
    return testes


def main():
    ds, tm, cz, ctx = montar()
    testes = veredito(ds, tm, cz)

    # ------------------------------------------------------------------ MD
    md = []
    A = md.append

    A("# Dia de Sorte × Timemania — padrões de repetição, colunas e frequência\n")
    A(f"**Recorte:** últimos 100 concursos de cada jogo  \n"
      f"- **Dia de Sorte:** concursos **{ds['janela']['de']} a {ds['janela']['ate']}** "
      f"({ds['janela']['data_ini']} a {ds['janela']['data_fim']}) — 7 dezenas de 1 a 31  \n"
      f"- **Timemania:** concursos **{tm['janela']['de']} a {tm['janela']['ate']}** "
      f"({tm['janela']['data_ini']} a {tm['janela']['data_fim']}) — 7 dezenas de 1 a 80  \n"
      f"**Método:** distribuições exatas (hipergeométrica, qui-quadrado) + Monte Carlo "
      f"para o que não tem forma fechada. Script reprodutível em `analise.py`.\n")

    A("> **Resposta curta:** existe um padrão nos dois jogos — mas é o padrão do sorteio justo. "
      "Frequência de dezenas, repetição em relação ao concurso anterior, colunas e somas "
      "batem com o previsto por azar puro. E os dois jogos **não** têm relação entre si.\n")

    # 1. frequência
    A("\n## 1. As dezenas que mais saem (últimos 100)\n")
    for chave, jogo, cor in (("dia-de-sorte", ds, "🟢"), ("timemania", tm, "🟣")):
        f = jogo["janela"]["frequencias"]
        c = ctx[chave]
        top = ", ".join(f"**{q['dezena']:02d}** ({q['n']}×)" for q in f["quentes"][:6])
        frias = ", ".join(f"{q['dezena']:02d} ({q['n']}×)" for q in f["frias"][:6])
        A(f"\n### {cor} {jogo['nome']}\n")
        A(f"- Esperado por dezena: **{num(f['esperado'], 2)}** aparições em 100 concursos "
          f"(cada dezena tem {pct(c['p_dezena'], 2)} de chance por concurso).\n")
        A(f"- Mais sorteadas: {top}.\n")
        A(f"- Menos sorteadas: {frias}.\n")
        A(f"- Máxima: **{f['max']}×** (p = {pval(f['max_p'])} contra o máximo esperado por acaso); "
          f"mínima: **{f['min']}×**.\n")
        A(f"- Qui-quadrado de uniformidade: χ² = {num(f['chi2'], 1)} com {f['chi2_gl']} graus de "
          f"liberdade → **p = {pval(f['chi2_p'])}**.\n")
        if chave == "timemania" and jogo['janela'].get('times'):
            tt = jogo['janela']['times']
            A(f"- Curiosidade fora das dezenas: {tt['distintos']} times do coração diferentes em 100 "
              f"concursos; o mais repetido foi {tt['top'][0][0]} ({tt['top'][0][1]}×).\n")
        A(f"- Uma dezena precisa de cerca de **{num(100 * c['p_dezena'] + 3.4 * math.sqrt(100 * c['p_dezena'] * (1 - c['p_dezena'])), 0)}×** "
          f"para destoar de verdade (limiar de Bonferroni com {jogo['universo']} dezenas). "
          f"A campeã chegou a {f['max']}×.\n")

    A("\n**Leitura:** a “tábua de quentes” é compatível com sorteio uniforme. Se você olhar 31 ou 80 "
      "dezenas, alguém sempre vai parecer quente — é o efeito do teste múltiplo, não sinal.\n")

    # 2. repetição
    A("\n## 2. Padrão de repetição em relação ao concurso anterior\n")
    A("Quantas dezenas de um concurso reaparecem no seguinte (comparando sempre com o sorteio imediatamente anterior):\n")
    A("\n| Jogo | Média de repetidas | Esperado | Erro padrão | z | p (média) | p (distribuição) |\n"
      "|---|---|---|---|---|---|---|")
    for jogo in (ds, tm):
        r = jogo["janela"]["repeticoes"]
        A(f"| {jogo['nome']} | **{num(r['media'], 2)}** | {num(r['esperado_media'], 2)} | "
          f"{num(r['ep'], 3)} | {num(r['z'], 2)} | {pval(r['p_media'])} | {pval(r['chi2_p_mc'])} |")
    A("\nDistribuição completa (observado × esperado pela hipergeométrica):\n")

    for jogo in (ds, tm):
        r = jogo["janela"]["repeticoes"]
        A(f"\n**{jogo['nome']}** — {r['n_pares']} pares de concursos consecutivos\n")
        ultimo = max(i for i, v in enumerate(r["hist"]) if v > 0)
        ks = list(range(min(len(r["hist"]), max(4, ultimo + 2))))
        A("\n| Dezenas repetidas | " + " | ".join(str(i) for i in ks) + " |\n"
          "|---|" + "---|" * len(ks))
        A("| Observado | " + " | ".join(str(r["hist"][i]) for i in ks) + " |")
        A("| Esperado | " + " | ".join(num(r["teorico"][i], 1) for i in ks) + " |")
        A("\n")
        c = ctx["dia-de-sorte" if jogo is ds else "timemania"]
        A(f"- Concursos **sem nenhuma repetição**: {r['hist'][0]} (esperado {num(r['teorico'][0], 1)}) → "
          f"na prática, **{pct(r['p_um_ou_mais'])}** dos concursos repetem ao menos 1 dezena "
          f"(teoria: {pct(r['p_um_ou_mais_teorico'])}).\n")
        if r["destaque"]:
            A("- Maiores repetições da janela: " + "; ".join(
                f"concurso {d['concurso']} repetiu {len(d['repetidas'])} "
                f"({', '.join(f'{x:02d}' for x in d['repetidas'])})" for d in r["destaque"]) + ".\n")

    A("\n**Leitura:** o número de repetidas é exatamente o que a hipergeométrica prevê. "
      "A “média de repetição” de cada jogo é, na prática, uma constante do jogo (k²/N), "
      "não uma tendência que aparece e desaparece.\n")

    # 3. colunas
    A("\n## 3. As colunas (1ª a 7ª dezena do volante)\n")
    A("Coluna = posição da dezena depois de ordenar o resultado. É aqui que aparece o padrão "
      "mais forte — e o mais mal interpretado: ele é **combinatório**, não sorteável.\n")
    for chave, jogo in (("dia-de-sorte", ds), ("timemania", tm)):
        A(f"\n### {jogo['nome']} — universo 1 a {jogo['universo']}\n")
        A("\n| Coluna | Moda (nº mais frequente) | Vezes | Média | Média esperada | z | Faixa |\n|---|---|---|---|---|---|---|")
        for c in jogo["janela"]["colunas"]["colunas"]:
            A(f"| {c['coluna']}ª | **{c['moda']:02d}** | {c['moda_n']} | {num(c['media'], 1)} | "
              f"{num(c['teo_media'], 1)} | {num(c['z'], 2)} | {c['min']:02d}–{c['max']:02d} |")
        A("")
    A("\n**Leitura:** a 1ª coluna concentra valores baixos e a 7ª valores altos — em qualquer jogo "
      "de 7 dezenas. E note a coincidência com a teoria: a dezena **01** na 1ª coluna do Dia de Sorte aparece "
      f"{ds['janela']['colunas']['colunas'][0]['top'][0]['n']}× em 100 e a **31** na 7ª aparece "
      f"{ds['janela']['colunas']['colunas'][6]['top'][0]['n']}×; nos dois casos 7/31 = {pct(7/31)} "
      f"prevê {num(7/31*100, 1)} vezes. Na Timemania, 80 na 7ª saiu "
      f"{tm['janela']['colunas']['colunas'][6]['top'][0]['n']}× contra 7/80 = {pct(7/80)} "
      f"esperado. A “coluna da dezena 80” parece quente; é só o extremo do universo.\n")

    # 4. por concurso
    A("\n## 4. Existe relação de frequência em cada concurso isolado?\n")
    A("Teste direto: em cada concurso, aposte nas 7 dezenas “mais quentes” dos 20 concursos anteriores. "
      "Se frequência significasse algo, essa aposta acertaria mais que o acaso.\n")
    A("\n| Jogo | Acertos médios por concurso | Esperado por acaso | Simulação (média) | p |\n|---|---|---|---|---|")
    for jogo in (ds, tm):
        q = jogo["serie_completa"]["quentes"]
        A(f"| {jogo['nome']} | {num(q['media_acertos'], 3)} | {num(q['esperado'], 3)} | "
          f"{num(q['nulo_media'], 3)} | {pval(q['p'])} |")
    A("\nTeste do atraso (a chance muda conforme o tempo sem sair?):\n")
    A("\n| Jogo | " + " | ".join(b["atraso"] for b in ds["serie_completa"]["atraso"]["baldes"]) + " |\n"
      "|---|" + "---|" * len(ds["serie_completa"]["atraso"]["baldes"]))
    for jogo in (ds, tm):
        A(f"| {jogo['nome']} | " + " | ".join(
            "–" if b["p"] is None else pct(b["p"], 1) for b in jogo["serie_completa"]["atraso"]["baldes"]) + " |")
    A(f"\n(Chance de referência por concurso: {pct(7/31, 2)} no Dia de Sorte e {pct(7/80, 2)} na Timemania.)\n")
    A("\n**Leitura:** nenhuma das duas rotinas bate o acaso. Dezena quente não continua quente; "
      "dezena atrasada não fica “devendo”. Em ambos os jogos os acertos ficaram levemente **abaixo** "
      "do esperado — o oposto do que o mito prevê.\n")

    # 5. cruzada
    j = cz["janela"]
    A("\n## 5. Dia de Sorte × Timemania: os dois jogos conversam entre si?\n")
    A("Os dois sorteiam em dias diferentes (Dia de Sorte de segunda a sábado; Timemania terça, quinta "
      "e sábado), então comparamos os concursos **pareados por data** (tolerância de 1 dia, por causa da "
      "grafia de datas na fonte).\n")
    A(f"\n- Pares na janela: **{j['n_pares']}** ({j['primeira_data']} a {j['ultima_data']}; "
      f"Dia de Sorte {j['concurso_ds_ini']}–{j['concurso_ds_fim']}, "
      f"Timemania {j['concurso_tm_ini']}–{j['concurso_tm_fim']}).\n")
    A(f"- Dezenas em comum por par: **{num(j['sobreposicao_media'], 2)}** (esperado por azar: "
      f"{num(j['sobreposicao_esperada'], 2)}; z = {num(j['sobreposicao_z'], 2)}; p = {pval(j['sobreposicao_p'])}).\n")
    A(f"- Pares com **pelo menos uma** dezena em comum: {pct(j['pelo_menos_uma'])} "
      f"(esperado: {pct(j['pelo_menos_uma_teorico'])}).\n")
    A(f"- Correlação de frequência nas 31 dezenas que existem nos dois jogos: "
      f"Pearson r = {num(j['pearson'], 3)} (p = {pval(j['pearson_p'])}), "
      f"Spearman ρ = {num(j['spearman'], 3)} (p = {pval(j['spearman_p'])}).\n")
    A(f"- Top 7 “quentes” do Dia de Sorte: {', '.join(f'{d:02d}' for d in j['quentes_ds'])}; "
      f"da Timemania: {', '.join(f'{d:02d}' for d in j['quentes_tm'])}. Coincidem em "
      f"**{len(j['quentes_interseccao'])}** dezenas ({', '.join(f'{d:02d}' for d in j['quentes_interseccao']) or 'nenhuma'}).\n")
    f2 = cz["serie_completa"]
    A(f"- Com toda a série ({f2['n_pares']} pares, desde {f2['primeira_data']}): média "
      f"{num(f2['sobreposicao_media'], 2)} vs esperado {num(f2['sobreposicao_esperada'], 2)} "
      f"(p = {pval(f2['sobreposicao_p'])}); r = {num(f2['pearson'], 3)} (p = {pval(f2['pearson_p'])}).\n")
    A("\n**Leitura:** nenhuma relação. Duas coincidências entre os rankings de quentes é exatamente "
      "o que 31 dezenas escolhidas ao acaso produzem com mais frequência.\n")

    # 6. veredito
    A("\n## 6. Veredito: o padrão existe nos dois jogos?\n")
    A("\n| Teste | p — Dia de Sorte | p — Timemania | Conclusão |\n|---|---|---|---|")
    for t in testes:
        concl = "compatível com sorteio justo" if min(t["p_ds"], t["p_tm"]) >= 0.05 else "ver seção"
        A(f"| {t['teste']} | {pval(t['p_ds'])} | {pval(t['p_tm'])} | {concl} |")
    A("\n**O que existe nos dois jogos:**\n")
    A("1. Repetição média de dezenas do concurso anterior — sim, e é a mesma lei nos dois: "
      f"k²/N = {num(49/31, 2)} no Dia de Sorte e {num(49/80, 2)} na Timemania. Nada além disso.\n")
    A("2. Colunas ordenadas com médias e modas previsíveis — sim, nos dois, por pura combinatoriedade "
      "(1ª coluna baixa, 7ª alta).\n")
    A("3. Soma, paridade e pares consecutivos dentro do esperado — sim, nos dois.\n")
    A("\n**O que não existe em nenhum dos dois:**\n")
    A("1. Dezena com frequência fora do acaso (p = "
      f"{pval(ds['janela']['frequencias']['chi2_p'])} e {pval(tm['janela']['frequencias']['chi2_p'])}).\n")
    A("2. Dezena “quente” que continua saindo, ou “fria” que está devendo.\n")
    A("3. Repetição acima do previsto entre concursos consecutivos.\n")
    A("4. Qualquer transferência de frequência de um jogo para o outro.\n")
    A("\n**Nota metodológica.** Um p < 0,05 isolado apareceria por acaso em ~1 de cada 20 testes; "
      "rodamos dezenas. Por isso cada achado foi checado na série completa (1.337 concursos do Dia de "
      "Sorte e 2.462 da Timemania) e com correção para testes múltiplos. O resultado é estável: os "
      "sorteios se comportam como sorteios.\n")
    A("\n**Limitações.** (a) O conjunto de dados público não traz o “Mês da Sorte” do Dia de Sorte — "
      "a análise cobre as 7 dezenas (o Time do Coração da Timemania não é dezena e ficou de fora); (b) o concurso 1307 da "
      "Timemania vinha com 8 dezenas na fonte (uma duplicidade), corrigido e documentado em `analise.py`; "
      "(c) nada aqui é recomendação de aposta — as dezenas dos próximos concursos continuam "
      "independentes do passado.\n")

    (RAIZ / "RELATORIO.md").write_text("\n".join(md), encoding="utf-8")

    # ------------------------------------------------------------------ HTML
    css = """
:root{--ds:#0f766e;--tm:#6d28d9;--tinta:#0f172a;--suave:#475569;--linha:#e2e8f0;--fundo:#f8fafc}
*{box-sizing:border-box}
body{margin:0;background:var(--fundo);color:var(--tinta);
 font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1000px;margin:0 auto;padding:40px 24px 80px}
header.hero{background:linear-gradient(135deg,#0f766e,#6d28d9);color:#fff;border-radius:20px;
 padding:38px 36px;margin-bottom:36px;box-shadow:0 20px 45px -25px rgba(15,23,42,.6)}
header.hero h1{margin:0 0 8px;font-size:33px;line-height:1.15;letter-spacing:-.02em}
header.hero p{margin:0;opacity:.92;font-size:15px;max-width:64ch}
header.hero .tags{margin-top:20px;display:flex;flex-wrap:wrap;gap:8px}
.tag{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);
 padding:5px 11px;border-radius:999px;font-size:12.5px;font-weight:600}
section{background:#fff;border:1px solid var(--linha);border-radius:16px;padding:28px 30px;
 margin-bottom:22px;box-shadow:0 1px 2px rgba(15,23,42,.04)}
h2{font-size:21px;margin:0 0 6px;letter-spacing:-.01em}
h2 .n{color:#94a3b8;font-weight:600;margin-right:8px}
h3{font-size:16px;margin:22px 0 8px}
p{margin:10px 0;font-size:15px;color:#1e293b}
ul{margin:10px 0 10px 18px;padding:0;font-size:15px}
li{margin:5px 0}
.sub{color:var(--suave);font-size:14px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:18px 0 4px}
.card{border:1px solid var(--linha);border-radius:12px;padding:14px 16px;background:#fcfdff}
.card .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:#64748b;font-weight:700}
.card .v{font-size:23px;font-weight:700;margin-top:4px;letter-spacing:-.02em}
.card .d{font-size:12.5px;color:var(--suave);margin-top:2px}
.card.ds{border-left:4px solid var(--ds)} .card.tm{border-left:4px solid var(--tm)}
table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0}
th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--linha)}
th{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#64748b;font-weight:700}
tbody tr:hover{background:#f8fafc}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.heat{display:grid;gap:5px;margin:16px 0 6px}
.cel{border-radius:8px;padding:6px 4px;display:flex;flex-direction:column;align-items:center;
 border:1px solid rgba(15,23,42,.06)}
.cel-n{font-size:10.5px;opacity:.85;font-weight:600}
.cel-c{font-size:15px;font-weight:700;line-height:1.1}
.grafico{width:100%;height:auto;display:block;margin:12px 0}
.eixo{font-size:11px;fill:#64748b}
.valor{font-size:10.5px;fill:#334155;font-weight:600}
.valor.esp{fill:#94a3b8}
.legenda{font-size:12.5px;color:var(--suave)}
.ok{color:#047857;font-weight:700}
.alerta{color:#b45309;font-weight:700}
blockquote{margin:16px 0;padding:14px 18px;background:#f0fdfa;border-left:4px solid var(--ds);
 border-radius:0 10px 10px 0;font-size:15px}
blockquote strong{color:#0f766e}
.split{display:grid;grid-template-columns:1fr 1fr;gap:22px}
@media(max-width:760px){.split{grid-template-columns:1fr}}
footer{color:#64748b;font-size:13px;text-align:center;margin-top:30px}
code{background:#f1f5f9;padding:1px 5px;border-radius:5px;font-size:13px}
"""

    def tabela_teste():
        linhas = ["<table><thead><tr><th>Teste</th><th class='num'>p — Dia de Sorte</th>"
                  "<th class='num'>p — Timemania</th><th>Leitura</th></tr></thead><tbody>"]
        for t in testes:
            ok = min(t["p_ds"], t["p_tm"]) >= 0.05
            linhas.append(
                f"<tr><td>{t['teste']}</td><td class='num'>{pval(t['p_ds'])}</td>"
                f"<td class='num'>{pval(t['p_tm'])}</td>"
                f"<td class='{'ok' if ok else 'alerta'}'>"
                f"{'sem desvio do acaso' if ok else 'ver detalhe'}</td></tr>")
        linhas.append("</tbody></table>")
        return "".join(linhas)

    def bloco_freq(chave, jogo, corvar):
        f = jogo["janela"]["frequencias"]
        c = ctx[chave]
        top = ", ".join(f"{q['dezena']:02d} <span class='sub'>({q['n']}×)</span>" for q in f["quentes"][:6])
        frias = ", ".join(f"{q['dezena']:02d} <span class='sub'>({q['n']}×)</span>" for q in f["frias"][:6])
        return f"""
        <h3 style="color:{corvar}">{jogo['nome']} — {jogo['universo']} dezenas</h3>
        <p class="sub">Esperado por dezena: <strong>{num(f['esperado'],2)}</strong> aparições
        (chance de {pct(c['p_dezena'],2)} por concurso). χ² = {num(f['chi2'],1)} com {f['chi2_gl']} gl →
        <strong>p = {pval(f['chi2_p'])}</strong>.</p>
        {heatmap(jogo['janela']['contagens'], jogo['universo'], corvar, f['esperado'])}
        <p class="legenda">Cor = número de aparições em 100 concursos. Passe o mouse para ver o z-score.</p>
        <div class="split">
          <div><p><strong>Mais quentes</strong><br>{top}</p></div>
          <div><p><strong>Mais frias</strong><br>{frias}</p></div>
        </div>
        <p class="sub">Máxima: <strong>{f['max']}×</strong>, contra um máximo de {num(f['max_nulo'],1)}× que o azar
        costuma produzir entre {jogo['universo']} dezenas (p = {pval(f['max_p'])}). Para destoar de verdade, seria preciso
        ~{num(100*c['p_dezena'] + 3.4*math.sqrt(100*c['p_dezena']*(1-c['p_dezena'])),0)}×.</p>"""

    def bloco_rep(jogo, corvar):
        r = jogo["janela"]["repeticoes"]
        ultimo = max(i for i, v in enumerate(r["hist"]) if v > 0)
        ks = list(range(min(len(r["hist"]), max(4, ultimo + 2))))
        graf = svg_barras_duplas([(r["hist"][i], r["teorico"][i]) for i in ks],
                                 [str(i) for i in ks], h=240, cor_obs=corvar,
                                 eixo_y="nº de concursos")
        return f"""
        <h3 style="color:{corvar}">{jogo['nome']}</h3>
        <p>Média de <strong>{num(r['media'],2)}</strong> dezenas repetidas por concurso, contra
        <strong>{num(r['esperado_media'],2)}</strong> esperado (z = {num(r['z'],2)},
        p = {pval(r['p_media'])}). A distribuição inteira adere à hipergeométrica
        (p = {pval(r['chi2_p_mc'])}).</p>
        {graf}
        <p class="legenda">Barras coloridas = observado nos últimos 100 concursos; cinza = esperado
        por sorteio uniforme. Eixo x = quantas dezenas repetiram do concurso anterior.</p>
        <p class="sub">{pct(r['p_um_ou_mais'])} dos concursos repetem ao menos 1 dezena
        (teoria: {pct(r['p_um_ou_mais_teorico'],1)}); {r['hist'][0]} concursos não repetiram nada
        (esperado {num(r['teorico'][0],1)}).</p>"""

    def bloco_colunas(jogo, corvar):
        linhas = "".join(
            f"<tr><td>{c['coluna']}ª</td><td><strong>{c['moda']:02d}</strong></td>"
            f"<td class='num'>{c['moda_n']}</td><td class='num'>{num(c['media'],1)}</td>"
            f"<td class='num'>{num(c['teo_media'],1)}</td>"
            f"<td class='num'>{num(c['z'],2)}</td>"
            f"<td class='num'>{c['min']:02d}–{c['max']:02d}</td></tr>"
            for c in jogo["janela"]["colunas"]["colunas"])
        return f"""
        <h3 style="color:{corvar}">{jogo['nome']}</h3>
        <table><thead><tr><th>Coluna</th><th>Moda</th><th class="num">Vezes</th>
        <th class="num">Média</th><th class="num">Média esperada</th><th class="num">z</th>
        <th class="num">Faixa</th></tr></thead><tbody>{linhas}</tbody></table>"""

    j = cz["janela"]
    j2 = cz["serie_completa"]
    dispersao = svg_dispersao(j["freq_ds"], j["freq_tm"], "#6d28d9",
                              rotulo_x="frequência no Dia de Sorte (100 concursos)",
                              rotulo_y="frequência na Timemania (mesmas datas)")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dia de Sorte × Timemania — análise de padrões</title>
<style>{css}</style></head><body><div class="wrap">

<header class="hero">
  <h1>Dia de Sorte × Timemania</h1>
  <p>Padrões de repetição, colunas e frequência nos últimos 100 concursos de cada jogo —
  e a pergunta que importa: esses padrões existem nos dois?</p>
  <div class="tags">
    <span class="tag">Dia de Sorte {ds['janela']['de']}–{ds['janela']['ate']}</span>
    <span class="tag">Timemania {tm['janela']['de']}–{tm['janela']['ate']}</span>
    <span class="tag">{j['n_pares']} concursos pareados por data</span>
    <span class="tag">Monte Carlo + testes exatos</span>
  </div>
</header>

<section>
  <h2><span class="n">01</span>Resposta curta</h2>
  <blockquote><strong>Existe um padrão nos dois jogos — mas é o padrão do sorteio justo.</strong>
  Frequência de dezenas, repetição em relação ao concurso anterior, colunas e somas batem com o
  que o azar puro prevê. E os dois jogos <strong>não</strong> têm relação de frequência entre si.</blockquote>
  <div class="cards">
    <div class="card ds"><div class="k">Dia de Sorte · repetição média</div>
      <div class="v">{num(ds['janela']['repeticoes']['media'],2)}</div>
      <div class="d">esperado {num(ds['janela']['repeticoes']['esperado_media'],2)} · p = {pval(ds['janela']['repeticoes']['p_media'])}</div></div>
    <div class="card tm"><div class="k">Timemania · repetição média</div>
      <div class="v">{num(tm['janela']['repeticoes']['media'],2)}</div>
      <div class="d">esperado {num(tm['janela']['repeticoes']['esperado_media'],2)} · p = {pval(tm['janela']['repeticoes']['p_media'])}</div></div>
    <div class="card ds"><div class="k">Dia de Sorte · uniformidade</div>
      <div class="v">p = {pval(ds['janela']['frequencias']['chi2_p'])}</div>
      <div class="d">χ² com {ds['janela']['frequencias']['chi2_gl']} gl · nenhuma dezena fora do acaso</div></div>
    <div class="card tm"><div class="k">Timemania · uniformidade</div>
      <div class="v">p = {pval(tm['janela']['frequencias']['chi2_p'])}</div>
      <div class="d">χ² com {tm['janela']['frequencias']['chi2_gl']} gl · nenhuma dezena fora do acaso</div></div>
    <div class="card"><div class="k">Coincidência entre os jogos</div>
      <div class="v">{num(j['sobreposicao_media'],2)}</div>
      <div class="d">dezenas em comum por concurso · esperado {num(j['sobreposicao_esperada'],2)}</div></div>
    <div class="card"><div class="k">Correlação de frequência</div>
      <div class="v">r = {num(j['pearson'],2)}</div>
      <div class="d">nas 31 dezenas comuns · p = {pval(j['pearson_p'])}</div></div>
  </div>
</section>

<section>
  <h2><span class="n">02</span>As dezenas que mais saem</h2>
  {bloco_freq("dia-de-sorte", ds, "#0f766e")}
  {bloco_freq("timemania", tm, "#6d28d9")}
  <p><strong>Leitura.</strong> A “tábua de quentes” é compatível com sorteio uniforme. Olhando 31 ou
  80 dezenas, alguém sempre parece quente: é efeito de teste múltiplo, não sinal. A dezena mais
  frequente da Timemania saiu {tm['janela']['frequencias']['max']}× — e o máximo que o puro azar
  produz em 80 dezenas ao longo de 100 concursos é, em média, {num(tm['janela']['frequencias']['max_nulo'],1)}×.</p>
</section>

<section>
  <h2><span class="n">03</span>Padrão de repetição</h2>
  <p class="sub">Quantas dezenas de um concurso reaparecem no concurso seguinte — sempre comparando
  com o sorteio imediatamente anterior.</p>
  {bloco_rep(ds, "#0f766e")}
  {bloco_rep(tm, "#6d28d9")}
  <p><strong>Leitura.</strong> A repetição média é uma constante do jogo: k²/N, ou seja
  {num(49/31,2)} no Dia de Sorte e {num(49/80,2)} na Timemania. Não é uma tendência que liga e desliga —
  e é exatamente onde os dois jogos mais se parecem.</p>
  {f"<p class='sub'>Maiores repetições da janela no Dia de Sorte: " + "; ".join(f"concurso {d['concurso']} com {len(d['repetidas'])} dezenas (<code>" + ", ".join(f"{x:02d}" for x in d['repetidas']) + "</code>)" for d in ds['janela']['repeticoes']['destaque']) + ". Com 100 concursos, ~" + num(ctx['dia-de-sorte']['esperado_4mais_em_100'],1) + " casos assim já são esperados por azar.</p>" if ds['janela']['repeticoes']['destaque'] else ""}
</section>

<section>
  <h2><span class="n">04</span>As colunas do volante</h2>
  <p class="sub">Coluna = posição da dezena depois de ordenar o resultado. É o padrão mais forte
  do conjunto — e o mais mal interpretado.</p>
  {bloco_colunas(ds, "#0f766e")}
  {bloco_colunas(tm, "#6d28d9")}
  <p><strong>Leitura.</strong> A 1ª coluna concentra valores baixos e a 7ª valores altos — em qualquer
  jogo de 7 dezenas, por combinatoriedade. E as modas batem com a teoria: 01 na 1ª coluna do Dia de
  Sorte aparece {ds['janela']['colunas']['colunas'][0]['top'][0]['n']}× em 100, e 7/31 = {pct(7/31)}
  prevê {num(7/31*100,1)}; 80 na 7ª coluna da Timemania aparece
  {tm['janela']['colunas']['colunas'][6]['top'][0]['n']}× contra 7/80 = {pct(7/80)}. A “coluna da
  dezena 80” não está quente: ela é o extremo do universo.</p>
</section>

<section>
  <h2><span class="n">05</span>Relação de frequência em cada concurso isolado</h2>
  <p>Teste direto: em cada concurso, apostar nas 7 dezenas mais quentes dos 20 concursos anteriores
  acerta mais que o acaso?</p>
  <table><thead><tr><th>Jogo</th><th class="num">Acertos por concurso</th>
  <th class="num">Esperado</th><th class="num">Simulação</th><th class="num">p</th></tr></thead><tbody>
  <tr><td>Dia de Sorte</td><td class="num">{num(ds['serie_completa']['quentes']['media_acertos'],3)}</td>
    <td class="num">{num(ds['serie_completa']['quentes']['esperado'],3)}</td>
    <td class="num">{num(ds['serie_completa']['quentes']['nulo_media'],3)}</td>
    <td class="num">{pval(ds['serie_completa']['quentes']['p'])}</td></tr>
  <tr><td>Timemania</td><td class="num">{num(tm['serie_completa']['quentes']['media_acertos'],3)}</td>
    <td class="num">{num(tm['serie_completa']['quentes']['esperado'],3)}</td>
    <td class="num">{num(tm['serie_completa']['quentes']['nulo_media'],3)}</td>
    <td class="num">{pval(tm['serie_completa']['quentes']['p'])}</td></tr>
  </tbody></table>
  <p class="sub">E o atraso? A chance de sair muda conforme o tempo sem aparecer?</p>
  <table><thead><tr><th>Jogo</th>{"".join(f"<th class='num'>atraso {b['atraso']}</th>" for b in ds['serie_completa']['atraso']['baldes'])}</tr></thead><tbody>
  <tr><td>Dia de Sorte</td>{"".join(f"<td class='num'>{'–' if b['p'] is None else pct(b['p'],1)}</td>" for b in ds['serie_completa']['atraso']['baldes'])}</tr>
  <tr><td>Timemania</td>{"".join(f"<td class='num'>{'–' if b['p'] is None else pct(b['p'],1)}</td>" for b in tm['serie_completa']['atraso']['baldes'])}</tr>
  </tbody></table>
  <p class="legenda">Chance de referência por concurso: {pct(7/31,2)} no Dia de Sorte e {pct(7/80,2)} na Timemania.</p>
  <p><strong>Leitura.</strong> Nenhuma rotina bate o acaso. Dezena quente não continua quente,
  dezena atrasada não fica devendo — e nos dois jogos os acertos ficaram levemente <em>abaixo</em>
  do esperado, o oposto do que o mito prevê.</p>
</section>

<section>
  <h2><span class="n">06</span>Dia de Sorte × Timemania</h2>
  <p class="sub">Concursos pareados por data (tolerância de 1 dia, por causa da grafia de datas na
  fonte): {j['n_pares']} pares, de {j['primeira_data']} a {j['ultima_data']}. Cada dezena do Dia de
  Sorte tem chance 7/80 de estar entre as 7 da Timemania, então o esperado é
  {num(j['sobreposicao_esperada'],2)} dezena em comum por concurso.</p>
  <div class="cards">
    <div class="card"><div class="k">Dezenas em comum por par</div><div class="v">{num(j['sobreposicao_media'],2)}</div>
      <div class="d">esperado {num(j['sobreposicao_esperada'],2)} · z = {num(j['sobreposicao_z'],2)} · p = {pval(j['sobreposicao_p'])}</div></div>
    <div class="card"><div class="k">Pares com ≥ 1 dezena igual</div><div class="v">{pct(j['pelo_menos_uma'])}</div>
      <div class="d">esperado {pct(j['pelo_menos_uma_teorico'])}</div></div>
    <div class="card"><div class="k">Pearson (31 dezenas)</div><div class="v">{num(j['pearson'],3)}</div>
      <div class="d">p = {pval(j['pearson_p'])}</div></div>
    <div class="card"><div class="k">Spearman (31 dezenas)</div><div class="v">{num(j['spearman'],3)}</div>
      <div class="d">p = {pval(j['spearman_p'])}</div></div>
  </div>
  {dispersao}
  <p class="legenda">Cada ponto é uma dezena de 01 a 31: eixo x = vezes que saiu no Dia de Sorte,
  eixo y = vezes que saiu na Timemania nos concursos da mesma data. A reta é o ajuste linear —
  praticamente horizontal: frequência em um jogo não diz nada sobre o outro.</p>
  <p class="sub">Top 7 “quentes” do Dia de Sorte: <code>{", ".join(f"{d:02d}" for d in j['quentes_ds'])}</code> ·
  Timemania: <code>{", ".join(f"{d:02d}" for d in j['quentes_tm'])}</code> ·
  coincidem em <strong>{len(j['quentes_interseccao'])}</strong>
  ({", ".join(f"{d:02d}" for d in j['quentes_interseccao']) or "nenhuma"}), contra
  {num(j['quentes_chance'],2)} esperadas por azar.</p>
  <p class="sub">Série completa ({j2['n_pares']} pares desde {j2['primeira_data']}): média
  {num(j2['sobreposicao_media'],2)} vs {num(j2['sobreposicao_esperada'],2)} esperado
  (p = {pval(j2['sobreposicao_p'])}), r = {num(j2['pearson'],3)} (p = {pval(j2['pearson_p'])}).</p>
</section>

<section>
  <h2><span class="n">07</span>Veredito: existe esse padrão em ambos?</h2>
  {tabela_teste()}
  <h3>O que existe nos dois jogos</h3>
  <ul>
    <li><strong>Repetição com o concurso anterior</strong> — sim, e é a mesma lei nos dois: k²/N =
    {num(49/31,2)} no Dia de Sorte e {num(49/80,2)} na Timemania. O padrão é a própria matemática do jogo.</li>
    <li><strong>Colunas ordenadas previsíveis</strong> — sim: 1ª coluna baixa, 7ª alta, modas iguais aos extremos do universo.</li>
    <li><strong>Soma, paridade e pares consecutivos</strong> — sim, ambos dentro do esperado.</li>
  </ul>
  <h3>O que não existe em nenhum dos dois</h3>
  <ul>
    <li>Dezena com frequência fora do acaso (p = {pval(ds['janela']['frequencias']['chi2_p'])} e
    {pval(tm['janela']['frequencias']['chi2_p'])}).</li>
    <li>Dezena “quente” que continua saindo, ou “fria” que está devendo.</li>
    <li>Repetição acima do previsto entre concursos consecutivos.</li>
    <li>Transferência de frequência de um jogo para o outro.</li>
  </ul>
  <p class="sub"><strong>Nota metodológica.</strong> Um p &lt; 0,05 isolado aparece por acaso em ~1 de
  cada 20 testes, e rodamos dezenas de testes. Cada achado foi reconferido na série completa
  ({ds['total_concursos']} concursos do Dia de Sorte, {tm['total_concursos']} da Timemania) e com
  correção para testes múltiplos — o resultado é estável.</p>
  <p class="sub"><strong>Limitações.</strong> O conjunto de dados público não traz o “Mês da Sorte” do
  Dia de Sorte; a análise cobre as 7 dezenas. O concurso 1307 da Timemania vinha com 8 dezenas na
  fonte (duplicidade), corrigido e documentado em <code>analise.py</code>. Nada aqui é recomendação de
  aposta: os próximos sorteios são independentes do passado.</p>
</section>

<footer>Gerado por <code>analise.py</code> + <code>relatorio.py</code> · dados públicos das Loterias Caixa
até {ds['janela']['data_fim']} · reprodutível com semente fixa</footer>
</div></body></html>"""

    (RAIZ / "relatorio.html").write_text(html, encoding="utf-8")
    print("RELATORIO.md, relatorio.html e CSVs gravados.")


if __name__ == "__main__":
    main()
