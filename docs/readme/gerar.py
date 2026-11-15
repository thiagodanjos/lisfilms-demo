#!/usr/bin/env python3
"""
Gera as imagens animadas do README da demo (docs/readme/*.svg).

    pip install fonttools brotli pillow
    python docs/readme/gerar.py

Mesma identidade da demo (src/index.css): fundo #0b0d10, cartões #161a20, verde #1ed760, Inter.
Os SVG são mostrados pelo GitHub como <img>: animações CSS sim, JavaScript e recursos externos não, por isso a
fonte (só com as letras usadas) e as capturas vão embutidas. Sem animação fica sempre um estado completo.

Os «cartazes» são os da própria demo: os gradientes dos títulos fictícios de src/data/mock.ts, desenhados como o
componente Poster os desenha. Os números (títulos, pessoas, críticas, páginas) contam-se a partir do código.
"""

from __future__ import annotations

import base64
import io
import json
import math
import re
import sys
from html import unescape
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
REC = AQUI / "recursos"
CAPTURAS = RAIZ / "docs" / "capturas"
ICONES = json.loads((REC / "icones.json").read_text(encoding="utf-8"))["linhas"]
URL_DEMO = "thiagodanjos.github.io"
BASE_DEMO = "/lisfilms-demo"

C = {
    "bg": "#0b0d10",
    "lateral": "#08090c",
    "elevado": "#121519",
    "cartao": "#161a20",
    "cartao2": "#1d222a",
    "borda": "#252b34",
    "borda2": "#323a45",
    "texto": "#f4f6f8",
    "suave": "#9aa3ad",
    "tenue": "#838d99",
    "verde": "#1ed760",
    "verde2": "#7cf3a8",
    "verde_suave": "#122b1b",
    "ouro": "#f5c518",
}
FAMILIA = "'LisInter','Inter','Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
CURVA = "cubic-bezier(.22,1,.36,1)"


def esc(s: str) -> str:
    return escape(str(s), {'"': "&quot;"})


def n(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def pct(v: float) -> str:
    return f"{max(0.0, min(100.0, v)):.3f}".rstrip("0").rstrip(".") + "%"


# --------------------------------------------------------------------------------------------
# Os dados da demo, lidos de src/data/mock.ts
# --------------------------------------------------------------------------------------------
def dados() -> dict:
    mock = (RAIZ / "src" / "data" / "mock.ts").read_text(encoding="utf-8")
    bloco_g = mock[mock.index("const GRADIENTS"): mock.index("export const users")]
    gradientes = re.findall(r"\['(#[0-9a-fA-F]{6})',\s*'(#[0-9a-fA-F]{6})'\]", bloco_g)
    bloco_m = mock[mock.index("export const media"): mock.index("export const reviews")]
    titulos = {}
    for parte in re.split(r"\n  \{\n", bloco_m)[1:]:
        ident = re.search(r"id: '([^']+)'", parte).group(1)
        titulos[ident] = {
            "tipo": re.search(r"type: '([^']+)'", parte).group(1),
            "titulo": re.search(r"title: '([^']+)'", parte).group(1),
            "ano": int(re.search(r"year: (\d+)", parte).group(1)),
            "nota": float(re.search(r"communityRating: ([\d.]+)", parte).group(1)),
            "gradiente": gradientes[int(re.search(r"gradient: GRADIENTS\[(\d+)\]", parte).group(1))],
        }
    bloco_u = mock[mock.index("export const users"): mock.index("export const media")]
    bloco_r = mock[mock.index("export const reviews"): mock.index("export const feed")]
    paginas = [p for p in (RAIZ / "src" / "pages").glob("*.tsx") if p.stem != "NotFound"]
    return {
        "titulos": titulos,
        "filmes": sum(1 for t in titulos.values() if t["tipo"] == "filme"),
        "series": sum(1 for t in titulos.values() if t["tipo"] == "serie"),
        "pessoas": len(re.findall(r"username: '", bloco_u)),
        "criticas": len(re.findall(r"\{ id: 'r\d+'", bloco_r)),
        "paginas": len(paginas),
        "generos": len(set(re.findall(r"'([^']+)'", " ".join(re.findall(r"genres: \[([^\]]*)\]", bloco_m))))),
    }


DADOS = dados()


# --------------------------------------------------------------------------------------------
# Fonte, texto, ícones e imagens
# --------------------------------------------------------------------------------------------
class Fonte:
    def __init__(self) -> None:
        self.bytes = (REC / "inter.woff2").read_bytes()
        self._inst: dict[int, tuple] = {}

    def _metricas(self, peso: int):
        if peso not in self._inst:
            from fontTools.ttLib import TTFont
            from fontTools.varLib import instancer

            f = TTFont(io.BytesIO(self.bytes), recalcTimestamp=False)
            st = instancer.instantiateVariableFont(f, {"wght": peso})
            self._inst[peso] = (st.getBestCmap(), st["hmtx"].metrics, st["head"].unitsPerEm)
        return self._inst[peso]

    def largura(self, texto: str, tamanho: float, peso: int = 400, espacamento: float = 0.0) -> float:
        cmap, hmtx, upm = self._metricas(peso)
        total = 0.0
        for ch in texto:
            g = cmap.get(ord(ch)) or cmap.get(ord("?"))
            total += hmtx[g][0] * tamanho / upm
        return total + espacamento * len(texto)

    def face(self, letras: str) -> str:
        from fontTools import subset
        from fontTools.ttLib import TTFont

        opcoes = subset.Options()
        opcoes.flavor = "woff2"
        opcoes.layout_features = ["kern", "liga", "calt", "tnum"]
        opcoes.name_IDs = [0, 1, 2]
        f = TTFont(io.BytesIO(self.bytes), recalcTimestamp=False)
        sub = subset.Subsetter(opcoes)
        sub.populate(text="".join(sorted(set(letras + " ?"))))
        sub.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff2"
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return (
            "@font-face{font-family:'LisInter';font-style:normal;font-weight:100 900;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )


FONTE = Fonte()

BASE_CSS = (
    f"text{{font-family:{FAMILIA};font-kerning:normal;}}"
    ".fb{transform-box:fill-box;transform-origin:center;}"
    "@keyframes surgir{from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:none;}}"
    "@keyframes aparecer{from{opacity:0;}to{opacity:1;}}"
    "@keyframes pulso{0%,100%{opacity:1;}50%{opacity:.35;}}"
    "@keyframes deriva1{0%,100%{transform:translate(0,0);}50%{transform:translate(34px,-14px);}}"
    "@keyframes deriva2{0%,100%{transform:translate(0,0);}50%{transform:translate(-30px,16px);}}"
    "@keyframes fluir{from{stroke-dashoffset:9;}to{stroke-dashoffset:0;}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important;}}"
)

DEFS_COMUNS = (
    '<pattern id="pontos" width="22" height="22" patternUnits="userSpaceOnUse">'
    '<circle cx="1" cy="1" r=".9" fill="#ffffff" fill-opacity=".05"/></pattern>'
    '<filter id="desfoque" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>'
    '<filter id="sombra" x="-30%" y="-30%" width="160%" height="170%">'
    '<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".55"/></filter>'
)


def documento(largura: int, altura: float, titulo: str, descricao: str, css: str, corpo: str) -> str:
    letras = "".join(unescape(t) for t in re.findall(r">([^<>]+)<", corpo)) + titulo + descricao
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{n(altura)}" '
        f'viewBox="0 0 {largura} {n(altura)}" role="img" aria-labelledby="titulo descricao">\n'
        f'<title id="titulo">{esc(titulo)}</title>\n<desc id="descricao">{esc(descricao)}</desc>\n'
        f"<style>{FONTE.face(letras)}{BASE_CSS}{css}</style>\n{corpo}\n</svg>\n"
    )


def texto(x, y, conteudo, tamanho, peso=400, cor=C["texto"], ancora="start", espacamento=None, extra=""):
    attrs = [f'x="{n(x)}"', f'y="{n(y)}"', f'font-size="{n(tamanho)}"', f'font-weight="{peso}"', f'fill="{cor}"']
    if ancora != "start":
        attrs.append(f'text-anchor="{ancora}"')
    if espacamento is not None:
        attrs.append(f'letter-spacing="{n(espacamento)}"')
    return f'<text {" ".join(attrs)}{extra}>{conteudo}</text>'


def icone(nome, x, y, tamanho=18, cor=C["verde"], traco=2.0, extra=""):
    return (
        f'<g transform="translate({n(x)} {n(y)}) scale({tamanho / 24:.4f})" fill="none" stroke="{cor}" '
        f'stroke-width="{n(traco)}" stroke-linecap="round" stroke-linejoin="round"{extra}>{ICONES[nome]}</g>'
    )


def seta(x, y, tamanho, cor, direcao="direita", traco=2.2):
    d = "M9 18l6-6-6-6" if direcao == "direita" else "M15 18l-6-6 6-6"
    return (
        f'<g transform="translate({n(x)} {n(y)}) scale({tamanho / 24:.4f})" fill="none" stroke="{cor}" '
        f'stroke-width="{n(traco)}" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></g>'
    )


def radial(id_, cor, opacidade):
    return (
        f'<radialGradient id="{id_}"><stop offset="0" stop-color="{cor}" stop-opacity="{opacidade}"/>'
        f'<stop offset="1" stop-color="{cor}" stop-opacity="0"/></radialGradient>'
    )


def chip(x, y, rotulo, tamanho=11, peso=700, cor=C["texto"], fundo=C["cartao"], borda=C["borda2"], h=26):
    w = FONTE.largura(rotulo, tamanho, peso) + 22
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{h}" rx="{h / 2}" fill="{fundo}" stroke="{borda}"/>'
        + texto(x + w / 2, y + h / 2 + tamanho * 0.36, esc(rotulo), tamanho, peso, cor, "middle")
    ), w


def logotipo(x, base, tamanho, peso=850, brilho=True):
    """O logótipo da demo (ui.tsx → Logo): um ponto verde e «LisFilms»."""
    r = tamanho * 0.17
    cx, cy = x + r, base - tamanho * 0.35
    halo = f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 2)}" fill="{C["verde"]}" opacity=".45" filter="url(#desfoque)"/>' if brilho else ""
    return (
        halo
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{C["verde"]}"/>'
        + texto(x + 2 * r + tamanho * 0.22, base, 'Lis<tspan fill="url(#marcaVerde)">Films</tspan>', tamanho, peso, C["texto"], espacamento=-tamanho * 0.03)
    ), 2 * r + tamanho * 0.22 + FONTE.largura("LisFilms", tamanho, peso, -tamanho * 0.03)


GRAD_MARCA = (
    f'<linearGradient id="marcaVerde" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["verde"]}"/>'
    f'<stop offset=".55" stop-color="{C["verde2"]}"/><stop offset="1" stop-color="{C["verde"]}"/></linearGradient>'
)


def linhas(texto_: str, tamanho: float, peso: int, largura: float) -> list[str]:
    palavras, out, atual = texto_.split(), [], ""
    for p in palavras:
        tenta = f"{atual} {p}".strip()
        if FONTE.largura(tenta, tamanho, peso) <= largura or not atual:
            atual = tenta
        else:
            out.append(atual)
            atual = p
    return out + [atual]


def poster(id_def: str, x, y, w, h, t: dict, defs: list, rx=10) -> str:
    """Um título da demo como o componente Poster o desenha: gradiente a 155°, véu escuro, etiqueta, ano e título."""
    de, ate = t["gradiente"]
    a = math.radians(155)
    dx, dy = math.sin(a) / 2, -math.cos(a) / 2
    defs.append(
        f'<linearGradient id="{id_def}" x1="{.5 - dx:.3f}" y1="{.5 - dy:.3f}" x2="{.5 + dx:.3f}" y2="{.5 + dy:.3f}">'
        f'<stop offset="0" stop-color="{de}"/><stop offset="1" stop-color="{ate}"/></linearGradient>'
    )
    p = w / 11
    etiqueta = "Série" if t["tipo"] == "serie" else "Filme"
    te = w * 0.072
    we = FONTE.largura(etiqueta, te, 700) + te * 1.3
    out = [
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{rx}" fill="url(#{id_def})"/>',
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{rx}" fill="#000" fill-opacity=".1"/>',
        f'<rect x="{n(x + w - p * .7 - we)}" y="{n(y + p * .7)}" width="{n(we)}" height="{n(te * 1.75)}" rx="{n(te * .875)}" fill="#000" fill-opacity=".55"/>',
        texto(x + w - p * .7 - we / 2, y + p * .7 + te * 1.2, etiqueta, te, 700, C["texto"], "middle"),
    ]
    tt = w * 0.1
    ls = linhas(t["titulo"], tt, 800, w - 2 * p)
    yb = y + h - p
    for i, linha in enumerate(reversed(ls)):
        out.append(texto(x + p, yb - i * tt * 1.15, esc(linha), tt, 800, "#ffffff"))
    out.append(texto(x + p, yb - len(ls) * tt * 1.15 - tt * 0.05, str(t["ano"]), tt * 0.72, 500, "#ffffffd0"))
    out.append(f'<rect x="{n(x + .5)}" y="{n(y + .5)}" width="{n(w - 1)}" height="{n(h - 1)}" rx="{rx - .5}" fill="none" stroke="#fff" stroke-opacity=".08"/>')
    return "".join(out)


def captura(nome: str, largura: int, qualidade=80) -> str:
    from PIL import Image

    im = Image.open(CAPTURAS / f"{nome}.webp").convert("RGB")
    if im.width != largura:
        im = im.resize((largura, round(largura * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=qualidade, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def barra_navegador(x, y, w, h):
    """A barra de cima de uma janela de navegador com o endereço da demo."""
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["lateral"]}"/>',
        f'<line x1="{x}" y1="{n(y + h - .5)}" x2="{x + w}" y2="{n(y + h - .5)}" stroke="{C["borda"]}"/>',
    ]
    for i in range(3):
        out.append(f'<circle cx="{x + 20 + i * 15}" cy="{y + h / 2}" r="4.2" fill="{C["borda2"]}"/>')
    return "".join(out)


# --------------------------------------------------------------------------------------------
# 1. Banner
# --------------------------------------------------------------------------------------------
GALERIA = ["m1", "s1", "m2", "m5", "s3", "m4"]


def banner() -> str:
    W, H, TB = 900, 420, 40
    N = len(GALERIA)
    passo = 2.6
    T = N * passo
    s = 100 / N
    tr = 0.6 / T * 100
    pw, ph = 132, 198
    gx, gy = 702, 214
    dx = 130
    css = [
        ".gal{transform-box:fill-box;transform-origin:center;}"
        "@keyframes galeria{"
        "0%{transform:none;opacity:1;}"
        f"{pct(s - tr)}{{transform:none;opacity:1;}}"
        f"{pct(s)}{{transform:translateX(-{dx}px) scale(.76);opacity:.5;}}"
        f"{pct(2 * s - tr)}{{transform:translateX(-{dx}px) scale(.76);opacity:.5;}}"
        f"{pct(2 * s)}{{transform:translateX(-{2 * dx}px) scale(.6);opacity:0;}}"
        f"{pct(3 * s)}{{transform:translateX(-{2 * dx}px) scale(.6);opacity:0;}}"
        f"{pct(3 * s + 0.01)}{{transform:translateX({2 * dx}px) scale(.6);opacity:0;}}"
        f"{pct(100 - s - tr)}{{transform:translateX({2 * dx}px) scale(.6);opacity:0;}}"
        f"{pct(100 - s)}{{transform:translateX({dx}px) scale(.76);opacity:.5;}}"
        f"{pct(100 - tr)}{{transform:translateX({dx}px) scale(.76);opacity:.5;}}"
        "100%{transform:none;opacity:1;}}"
        "@keyframes legenda{"
        f"0%,{pct(s - tr)}{{opacity:1;}}{pct(s - tr / 2)},{pct(100 - tr / 2)}{{opacity:0;}}100%{{opacity:1;}}}}"
        "@keyframes luz{"
        f"0%,{pct(s - tr)}{{opacity:1;}}{pct(s + tr)},{pct(100 - tr * 1.5)}{{opacity:0;}}100%{{opacity:1;}}}}"
    ]
    defs = [
        DEFS_COMUNS,
        GRAD_MARCA,
        f'<clipPath id="quadro"><rect width="{W}" height="{H}" rx="20"/></clipPath>',
        f'<clipPath id="palco"><rect x="500" y="{TB}" width="{W - 500}" height="{H - TB}"/></clipPath>',
        '<linearGradient id="bordas" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".14" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="esbater"><rect x="500" y="{TB}" width="{W - 500}" height="{H - TB}" fill="url(#bordas)"/></mask>',
        radial("aurora1", C["verde"], 0.2),
        radial("aurora2", "#9b5de5", 0.08),
    ]
    p = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>', f'<rect y="{TB}" width="{W}" height="{H - TB}" fill="url(#pontos)"/>']
    p.append('<ellipse cx="190" cy="230" rx="320" ry="200" fill="url(#aurora1)" style="animation:deriva1 12s ease-in-out infinite"/>')
    p.append('<ellipse cx="560" cy="380" rx="260" ry="150" fill="url(#aurora2)" style="animation:deriva2 14s ease-in-out infinite"/>')

    luzes, capas, leg = [], [], []
    for i, ident in enumerate(GALERIA):
        t = DADOS["titulos"][ident]
        atraso = -((T - i * passo) % T)
        base = "" if i == 0 else "opacity:0;"
        defs.append(radial(f"luz{i}", t["gradiente"][0], 0.4))
        luzes.append(f'<ellipse cx="{gx}" cy="{gy}" rx="200" ry="165" fill="url(#luz{i})" style="{base}animation:luz {T}s linear {n(atraso)}s infinite"/>')
        if i == 0:
            inicial = "transform:none;opacity:1;"
        elif i == 1:
            inicial = f"transform:translateX({dx}px) scale(.76);opacity:.5;"
        elif i == N - 1:
            inicial = f"transform:translateX(-{dx}px) scale(.76);opacity:.5;"
        else:
            inicial = "opacity:0;"
        capas.append(
            f'<g class="gal" style="{inicial}animation:galeria {T}s {CURVA} {n(atraso)}s infinite">'
            f'<rect x="{gx - pw / 2}" y="{gy - ph / 2}" width="{pw}" height="{ph}" rx="10" fill="#000" filter="url(#sombra)"/>'
            + poster(f"cartaz{i}", gx - pw / 2, gy - ph / 2, pw, ph, t, defs)
            + "</g>"
        )
        ly = gy + ph / 2 + 30
        estrelas = f'<tspan fill="{C["ouro"]}">★</tspan> {str(t["nota"]).replace(".", ",")}'
        leg.append(
            f'<g style="{base}animation:legenda {T}s linear {n(atraso)}s infinite">'
            + texto(gx, ly, f'{esc(t["titulo"])}<tspan fill="{C["tenue"]}" font-weight="500"> · {t["ano"]} · </tspan><tspan font-weight="600" fill="{C["suave"]}">{estrelas}</tspan>', 13, 700, C["texto"], "middle")
            + texto(gx, ly + 33, f"{i + 1} de {N}", 10.5, 600, C["tenue"], "middle")
            + "</g>"
        )
    p.append(f'<g clip-path="url(#palco)">{"".join(luzes)}</g>')
    p.append(f'<g clip-path="url(#palco)" mask="url(#esbater)">{"".join(capas)}</g>')
    p.append("".join(leg))
    ly = gy + ph / 2 + 30
    for lado, x in (("esquerda", gx - 52), ("direita", gx + 52)):
        p.append(f'<circle cx="{x}" cy="{ly + 29.5}" r="13" fill="{C["cartao"]}" stroke="{C["borda2"]}"/>')
        p.append(seta(x - 7, ly + 22.5, 14, C["texto"] if lado == "direita" else C["tenue"], lado))

    kick = "DEMONSTRAÇÃO PÚBLICA"
    wk = FONTE.largura(kick, 9.5, 800, 1.8) + 34
    p.append(
        f'<g style="animation:surgir .8s {CURVA} .1s both">'
        f'<rect x="48" y="76" width="{n(wk)}" height="24" rx="12" fill="{C["verde_suave"]}" stroke="{C["verde"]}" stroke-opacity=".35"/>'
        f'<circle cx="62" cy="88" r="3.2" fill="{C["verde"]}" style="animation:pulso 1.8s ease-in-out infinite"/>'
        + texto(72, 91.4, kick, 9.5, 800, C["verde"], espacamento=1.8)
        + "</g>"
    )
    lg, wl = logotipo(48, 159, 54)
    sc, _ = chip(48 + wl + 12, 128, "demo", 12, 800, C["texto"], C["cartao2"], C["borda2"], 26)
    p.append(f'<g style="animation:surgir .9s {CURVA} .2s both">{lg}{sc}</g>')
    p.append(
        f'<g style="animation:surgir .9s {CURVA} .32s both">'
        + texto(49, 205, "A rede social de cinema, no teu navegador.", 21, 750, C["texto"], espacamento=-0.3)
        + "</g>"
    )
    p.append(
        f'<g style="animation:surgir .9s {CURVA} .42s both">'
        + texto(50, 235, "Catálogo, críticas, feed, perfis e watchlist com dados", 14.5, 500, "#c9d1d9")
        + texto(50, 256, "fictícios. Sem servidor, sem contas e sem chaves.", 14.5, 500, "#c9d1d9")
        + "</g>"
    )
    x = 50
    chips = []
    for rot in ("React 19", "TypeScript", "Tailwind 4", "Zustand"):
        sc, w = chip(x, 284, rot)
        chips.append(sc)
        x += w + 8
    p.append(f'<g style="animation:surgir .9s {CURVA} .55s both">{"".join(chips)}</g>')
    rodape, xr = [], 50
    for ic, t in (("server-off", "Sem servidor"), ("key-round", "Sem segredos"), ("hard-drive", "Fica no teu navegador")):
        rodape.append(icone(ic, xr, 341, 14, C["tenue"], 2.2) + texto(xr + 20, 352.5, t, 11.5, 500, C["tenue"]))
        xr += 20 + FONTE.largura(t, 11.5, 500) + 22
    p.append(f'<g style="animation:aparecer 1s ease-out .75s both">{"".join(rodape)}</g>')

    b = [barra_navegador(0, 0, W, TB)]
    bx, bw = W / 2 - 170, 340
    b.append(f'<rect x="{bx}" y="8" width="{bw}" height="24" rx="12" fill="{C["elevado"]}" stroke="{C["borda"]}"/>')
    b.append(icone("lock", bx + 12, 14, 12, C["tenue"], 2.4))
    b.append(texto(bx + 30, 24, f'{URL_DEMO}<tspan fill="{C["tenue"]}">{BASE_DEMO}/</tspan>', 11, 600, C["texto"]))
    rot = "Site oficial"
    wbt = FONTE.largura(rot, 10.5, 750) + 40
    b.append(f'<rect x="{W - 20 - wbt}" y="8" width="{n(wbt)}" height="24" rx="12" fill="{C["verde"]}"/>')
    b.append(icone("external-link", W - 20 - wbt + 11, 14, 12, "#04130a", 2.4))
    b.append(texto(W - 20 - wbt + 28, 24.3, rot, 10.5, 750, "#04130a"))

    corpo = (
        f"<defs>{''.join(defs)}</defs>"
        f'<g clip-path="url(#quadro)">{"".join(p)}{"".join(b)}</g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="none" stroke="{C["borda"]}"/>'
    )
    return documento(
        W,
        H,
        "LisFilms, demonstração pública",
        "LisFilms demo: a rede social de cinema, no teu navegador. Catálogo, críticas, feed, perfis e watchlist com dados "
        "fictícios, sem servidor, sem contas e sem chaves. A galeria passa por títulos inventados para a demo: "
        + ", ".join(DADOS["titulos"][i]["titulo"] for i in GALERIA)
        + ".",
        "".join(css),
        corpo,
    )


# --------------------------------------------------------------------------------------------
# 2. Ecrãs a passar
# --------------------------------------------------------------------------------------------
ECRAS = [
    ("inicio", "/", "Início", "o destaque e as sugestões pelos teus géneros"),
    ("catalogo", "/catalogo", "Catálogo", "filmes e séries, por tipo, género e nota"),
    ("ficha", "/titulo/m1", "Ficha de um filme", "a nota da comunidade, a da crítica e a tua crítica"),
    ("ficha-serie", "/titulo/s1", "Ficha de uma série", "temporadas, elenco e o que a comunidade achou"),
    ("feed", "/feed", "Feed", "as críticas mais recentes da comunidade"),
    ("descobrir", "/descobrir", "Descobrir", "o Top LisFilms e os lançamentos"),
    ("interesse", "/watchlist", "Watchlist", "guardada só neste navegador"),
    ("perfil", "/perfil/thiago", "Perfil", "estatísticas, géneros favoritos e críticas"),
]


def ecras() -> str:
    W, m = 900, 20
    iw = W - 2 * m
    ih = iw * 10 / 16
    tb = 36
    H = m + tb + ih + 62
    por = 3.4
    N = len(ECRAS)
    total = por * N
    a = 100 * 0.5 / total
    f = 100 * por / total
    css = [
        f"@keyframes primeiro{{0%,{pct(f + a)}{{opacity:1;}}{pct(f + a + .01)},100%{{opacity:0;}}}}"
        f"@keyframes seguinte{{0%{{opacity:0;}}{pct(a)},{pct(f + a)}{{opacity:1;}}{pct(f + a + .01)},100%{{opacity:0;}}}}"
        f"@keyframes ultimo{{0%{{opacity:0;}}{pct(a)},{pct(f)}{{opacity:1;}}{pct(f + a)},100%{{opacity:0;}}}}"
        f"@keyframes texto{{0%,{pct(a / 2)}{{opacity:0;}}{pct(a)},{pct(f)}{{opacity:1;}}{pct(f + a / 2)},100%{{opacity:0;}}}}"
        f"@keyframes texto0{{0%,{pct(f)}{{opacity:1;}}{pct(f + a / 2)},{pct(100 - a / 2)}{{opacity:0;}}100%{{opacity:1;}}}}"
        f"@keyframes progresso{{0%{{transform:scaleX(0);}}{pct(f)}{{transform:scaleX(1);}}{pct(f + .01)},100%{{transform:scaleX(0);}}}}"
        ".ecra{opacity:0;}.ecra0{opacity:1;}"
        ".barra{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);}.barra0{transform:scaleX(1);}"
    ]
    defs = [f'<clipPath id="janela"><rect x="{m}" y="{m}" width="{iw}" height="{tb + ih}" rx="12"/></clipPath>']
    bx, bw = W / 2 - 190, 380
    camadas, urls, legendas, pontos = [], [], [], []
    for i, (fich, rota, tit, sub) in enumerate(ECRAS):
        anim = "primeiro" if i == 0 else ("ultimo" if i == N - 1 else "seguinte")
        estilo = f'style="animation:{anim} {n(total)}s ease-in-out {n(i * por)}s infinite both"'
        estilo_t = f'style="animation:{"texto0" if i == 0 else "texto"} {n(total)}s linear {n(i * por)}s infinite both"'
        camadas.append(f'<g class="ecra ecra{i}" {estilo}><image x="{m}" y="{m + tb}" width="{iw}" height="{n(ih)}" href="{captura(fich, 1600)}"/></g>')
        caminho = BASE_DEMO + rota
        assert FONTE.largura(URL_DEMO + caminho, 11, 600) < bw - 40, caminho
        urls.append(
            f'<g class="ecra ecra{i}" {estilo_t}>'
            + texto(bx + 30, m + 22.5, f'{URL_DEMO}<tspan fill="{C["tenue"]}">{esc(caminho)}</tspan>', 11, 600, C["texto"])
            + "</g>"
        )
        assert FONTE.largura(tit, 15, 800) + 10 + FONTE.largura(sub, 12, 500) < iw - 8, tit
        legendas.append(
            f'<g class="ecra ecra{i}" {estilo_t}>'
            + texto(m + 4, m + tb + ih + 38, esc(tit), 15, 800, C["texto"])
            + texto(m + 4 + FONTE.largura(tit, 15, 800) + 10, m + tb + ih + 38, esc(sub), 12, 500, C["suave"])
            + "</g>"
        )
        pw = 14
        px = W - m - 14 - (N - i) * (pw + 5) + 5
        pontos.append(
            f'<rect x="{px}" y="{m + 16}" width="{pw}" height="4" rx="2" fill="{C["borda2"]}"/>'
            f'<rect class="barra barra{i}" x="{px}" y="{m + 16}" width="{pw}" height="4" rx="2" fill="{C["verde"]}" '
            f'style="animation:progresso {n(total)}s linear {n(i * por)}s infinite"/>'
        )
    barra = [barra_navegador(m, m, iw, tb)]
    barra.append(f'<rect x="{bx}" y="{m + 7}" width="{bw}" height="22" rx="11" fill="{C["elevado"]}" stroke="{C["borda"]}"/>')
    barra.append(icone("lock", bx + 12, m + 12, 12, C["tenue"], 2.4))
    corpo = (
        f"<defs>{''.join(defs)}</defs>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{n(H - 1)}" rx="20" fill="{C["lateral"]}" stroke="{C["borda"]}"/>'
        f'<rect x="{m}" y="{m + tb}" width="{iw}" height="{n(ih)}" fill="{C["bg"]}"/>'
        f'<g clip-path="url(#janela)">{"".join(camadas)}{"".join(barra)}</g>'
        + "".join(urls)
        + f'<rect x="{m + .5}" y="{m + .5}" width="{iw - 1}" height="{n(tb + ih - 1)}" rx="11.5" fill="none" stroke="{C["borda"]}"/>'
        + "".join(legendas)
        + "".join(pontos)
    )
    return documento(
        W,
        H,
        "Ecrãs da demo do LisFilms",
        "Capturas da demo, com os dados fictícios que traz: " + "; ".join(f"{t}: {s}" for _, _, t, s in ECRAS) + ".",
        "".join(css),
        corpo,
    )


# --------------------------------------------------------------------------------------------
# 3. No telemóvel
# --------------------------------------------------------------------------------------------
TELEMOVEIS = [
    ("inicio-movel", "Início", "o destaque primeiro"),
    ("ficha-movel", "Ficha", "o título em grande"),
    ("catalogo-movel", "Catálogo", "filtros à mão"),
    ("perfil-movel", "Perfil", "a tua watchlist"),
]


def telemovel() -> str:
    W = 900
    sw, sh = 178, 178 * 844 / 390
    bz = 7
    fw, fh = sw + 2 * bz, sh + 2 * bz
    gap = (W - 40 - len(TELEMOVEIS) * fw) / (len(TELEMOVEIS) - 1)
    y0 = 30
    H = y0 + fh + 72
    css = ["@keyframes flutuarT{0%,100%{transform:translateY(0);}50%{transform:translateY(-7px);}}"]
    defs = [DEFS_COMUNS, radial("auroraV", C["verde"], 0.16), radial("auroraR", "#9b5de5", 0.14)]
    p = [
        f'<rect x=".5" y=".5" width="{W - 1}" height="{n(H - 1)}" rx="20" fill="{C["bg"]}" stroke="{C["borda"]}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{n(H - 1)}" rx="20" fill="url(#pontos)"/>',
        f'<ellipse cx="330" cy="{H / 2}" rx="360" ry="230" fill="url(#auroraV)" style="animation:deriva1 13s ease-in-out infinite"/>',
        f'<ellipse cx="{W - 140}" cy="{H / 2}" rx="220" ry="220" fill="url(#auroraR)" style="animation:deriva2 15s ease-in-out infinite"/>',
    ]
    for i, (fich, tit, sub) in enumerate(TELEMOVEIS):
        x = 20 + i * (fw + gap)
        defs.append(f'<clipPath id="ecraT{i}"><rect x="{n(x + bz)}" y="{n(y0 + bz)}" width="{n(sw)}" height="{n(sh)}" rx="24"/></clipPath>')
        tel = (
            f'<rect x="{n(x - 2)}" y="{n(y0 + 90)}" width="3" height="34" rx="1.5" fill="{C["borda2"]}"/>'
            f'<rect x="{n(x + fw - 1)}" y="{n(y0 + 110)}" width="3" height="54" rx="1.5" fill="{C["borda2"]}"/>'
            f'<rect x="{n(x)}" y="{y0}" width="{n(fw)}" height="{n(fh)}" rx="31" fill="#050607" stroke="{C["borda2"]}" filter="url(#sombra)"/>'
            f'<image x="{n(x + bz)}" y="{n(y0 + bz)}" width="{n(sw)}" height="{n(sh)}" clip-path="url(#ecraT{i})" href="{captura(fich, 390, 82)}"/>'
            f'<rect x="{n(x + .5)}" y="{y0 + .5}" width="{n(fw - 1)}" height="{n(fh - 1)}" rx="30.5" fill="none" stroke="#fff" stroke-opacity=".08"/>'
        )
        p.append(
            f'<g style="animation:surgir .9s {CURVA} {0.1 + i * 0.12:.2f}s both">'
            f'<g style="animation:flutuarT {6 + i * 0.7:.1f}s ease-in-out {-i * 1.3:.1f}s infinite">{tel}</g>'
            + texto(x + fw / 2, y0 + fh + 34, esc(tit), 14, 800, C["texto"], "middle")
            + texto(x + fw / 2, y0 + fh + 52, esc(sub), 11, 500, C["tenue"], "middle")
            + "</g>"
        )
    corpo = f"<defs>{''.join(defs)}</defs>" + "".join(p)
    return documento(
        W,
        H,
        "A demo do LisFilms no telemóvel",
        "Capturas da demo num telemóvel (390 por 844): " + "; ".join(f"{t}, {s}" for _, t, s in TELEMOVEIS) + ".",
        "".join(css),
        corpo,
    )


# --------------------------------------------------------------------------------------------
# 4. O que podes fazer e como é feita
# --------------------------------------------------------------------------------------------
FUNCOES = [
    ("O que podes fazer", C["verde"], C["verde_suave"], [
        ("layout-grid", "Catálogo", "filmes e séries, por tipo e género"),
        ("clapperboard", "Ficha de cada título", "sinopse, elenco e duas notas"),
        ("star", "Escrever críticas", "com estrelas, ficam na ficha"),
        ("heart", "Gostar de críticas", "as dos outros, com um toque"),
        ("rss", "Feed", "o que a comunidade avaliou"),
        ("circle-user", "Perfis", "estatísticas e géneros favoritos"),
        ("bookmark", "Watchlist", "a tua lista para ver mais tarde"),
        ("trending-up", "Top LisFilms", "e os lançamentos que aí vêm"),
    ]),
    ("Como é feita", C["texto"], C["cartao2"], [
        ("film", "Dados fictícios", f'{DADOS["filmes"] + DADOS["series"]} títulos, {DADOS["pessoas"]} pessoas, {DADOS["criticas"]} críticas'),
        ("server-off", "Sem servidor", "tudo corre no teu navegador"),
        ("key-round", "Sem segredos", "nenhuma chave nem variável"),
        ("hard-drive", "Guardado só aqui", "no localStorage do navegador"),
    ]),
]


def funcoes() -> str:
    W = 900
    colunas, tw, th, gap = 4, 206, 80, 10
    x0 = (W - (colunas * tw + (colunas - 1) * gap)) / 2
    css = ["@keyframes realce{0%,100%{opacity:0;}4%{opacity:1;}14%{opacity:0;}}"]
    p, y, k = [], 28, 0
    total = sum(len(g[3]) for g in FUNCOES)
    ciclo = 9.0
    for nome, cor, suave, itens in FUNCOES:
        p.append(f'<rect x="{x0}" y="{y}" width="4" height="18" rx="2" fill="{cor}"/>')
        p.append(texto(x0 + 13, y + 14, esc(nome), 13.5, 800, C["texto"]))
        y += 30
        for j, (ic, tit, sub) in enumerate(itens):
            assert FONTE.largura(tit, 12.5, 750) <= tw - 66 and FONTE.largura(sub, 10.5, 500) <= tw - 26, (tit, sub)
            c, linha = j % colunas, j // colunas
            x = x0 + c * (tw + gap)
            yy = y + linha * (th + gap)
            p.append(
                f'<g style="animation:surgir .6s {CURVA} {0.1 + k * 0.04:.2f}s both">'
                f'<rect x="{n(x)}" y="{yy}" width="{tw}" height="{th}" rx="14" fill="{C["cartao"]}" stroke="{C["borda"]}"/>'
                f'<rect x="{n(x)}" y="{yy}" width="{tw}" height="{th}" rx="14" fill="{cor}" fill-opacity=".05" stroke="{cor}" '
                f'stroke-opacity=".7" opacity="0" style="animation:realce {ciclo}s ease-in-out {1.2 + k * ciclo / total:.2f}s infinite"/>'
                f'<rect x="{n(x + 14)}" y="{yy + 13}" width="30" height="30" rx="9" fill="{suave}"/>'
                + icone(ic, x + 20, yy + 19, 18, cor)
                + texto(x + 54, yy + 33, esc(tit), 12.5, 750, C["texto"])
                + texto(x + 14, yy + 63, esc(sub), 10.5, 500, C["tenue"])
                + "</g>"
            )
            k += 1
        y += ((len(itens) + colunas - 1) // colunas) * (th + gap) + 14
    H = y + 6
    corpo = (
        f"<defs>{DEFS_COMUNS}</defs>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{C["bg"]}" stroke="{C["borda"]}"/>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="url(#pontos)"/>' + "".join(p)
    )
    return documento(
        W,
        H,
        "O que a demo faz",
        "; ".join(f"{g}: " + ", ".join(f"{t} ({s})" for _, t, s in it) for g, _, _, it in FUNCOES) + ".",
        "".join(css),
        corpo,
    )


# --------------------------------------------------------------------------------------------
# 5. A demo e o LisFilms real
# --------------------------------------------------------------------------------------------
COMPARACAO = [
    ("Catálogo", f'{DADOS["filmes"] + DADOS["series"]} títulos inventados para a demo', "o catálogo real, da TMDB, MyAnimeList e IGDB"),
    ("Contas", "uma pessoa fictícia, sem login", "contas reais, com login Google"),
    ("Servidor", "nenhum: só o teu navegador", "API própria (FastAPI) e PostgreSQL"),
    ("O que fazes", "fica no localStorage deste navegador", "fica na tua conta, em qualquer aparelho"),
    ("Tamanho", f'{DADOS["paginas"]} páginas', "LisGames, LisPlayer, Wrapped, listas, grupos…"),
    ("Onde", "GitHub Pages", "lisfilms.pt e app para Windows"),
    ("Idiomas", "português", "português, inglês, espanhol e francês"),
]


def comparacao() -> str:
    W = 900
    xl, xd, xr = 28, 196, 548
    wd, wr = xr - xd - 16, W - 28 - xr
    y0, hl = 108, 40
    H = y0 + len(COMPARACAO) * hl + 66
    css = []
    defs = [DEFS_COMUNS, GRAD_MARCA, radial("auroraV", C["verde"], 0.14)]
    p = [
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{C["bg"]}" stroke="{C["borda"]}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="url(#pontos)"/>',
        f'<ellipse cx="{xr + wr / 2}" cy="{H / 2}" rx="300" ry="230" fill="url(#auroraV)" style="animation:deriva2 14s ease-in-out infinite"/>',
        # a coluna do LisFilms real, realçada
        f'<rect x="{xr - 14}" y="22" width="{wr + 28}" height="{H - 44}" rx="16" fill="{C["verde"]}" fill-opacity=".04" stroke="{C["verde"]}" stroke-opacity=".35"/>',
    ]
    # cabeçalhos
    p.append(texto(xd, 52, "Esta demo", 15, 800, C["texto"]))
    p.append(texto(xd, 72, f"{URL_DEMO}{BASE_DEMO}", 10.5, 500, C["tenue"]))
    lg, _ = logotipo(xr, 56, 19, brilho=False)
    p.append(lg)
    p.append(texto(xr, 76, "lisfilms.pt · a versão completa", 10.5, 600, C["verde"]))
    for i, (rot, demo, real) in enumerate(COMPARACAO):
        y = y0 + i * hl
        assert FONTE.largura(demo, 12, 500) <= wd and FONTE.largura(real, 12, 600) <= wr - 22, (demo, real)
        p.append(
            f'<g style="animation:surgir .6s {CURVA} {0.15 + i * 0.08:.2f}s both">'
            + f'<line x1="{xl}" y1="{y - 14}" x2="{W - 28}" y2="{y - 14}" stroke="{C["borda"]}" stroke-opacity=".7"/>'
            + texto(xl, y + 10, esc(rot.upper()), 9.5, 800, C["tenue"], espacamento=1.2)
            + texto(xd, y + 10, esc(demo), 12, 500, C["suave"])
            + icone("check", xr, y - 1, 14, C["verde"], 2.6)
            + texto(xr + 22, y + 10, esc(real), 12, 600, C["texto"])
            + "</g>"
        )
    yb = y0 + len(COMPARACAO) * hl - 14
    p.append(f'<line x1="{xl}" y1="{yb}" x2="{W - 28}" y2="{yb}" stroke="{C["borda"]}" stroke-opacity=".7"/>')
    p.append(texto(xl, H - 28, "A demo foi reconstruída de raiz para o portefólio: não partilha código, dados nem servidores com a app real.", 11, 500, C["tenue"]))
    corpo = f"<defs>{''.join(defs)}</defs>" + "".join(p)
    return documento(
        W,
        H,
        "A demo e o LisFilms real",
        "Comparação entre esta demo e o LisFilms real em lisfilms.pt: "
        + "; ".join(f"{r}: na demo, {d}; no LisFilms, {x}" for r, d, x in COMPARACAO)
        + ".",
        "".join(css),
        corpo,
    )


# --------------------------------------------------------------------------------------------
# 6. Como funciona
# --------------------------------------------------------------------------------------------
def como() -> str:
    W, H = 900, 330
    defs = [DEFS_COMUNS]
    p = [
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{C["bg"]}" stroke="{C["borda"]}"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="url(#pontos)"/>',
    ]
    hn, wn, gap = 58, 182, 38
    x0 = (W - (4 * wn + 3 * gap)) / 2

    def no(x, y, ic, tit, sub, destaque=False, cor=C["verde"]):
        assert FONTE.largura(tit, 12, 750) <= wn - 62 and FONTE.largura(sub, 10.5, 500) <= wn - 62, (tit, sub)
        return (
            f'<rect x="{n(x)}" y="{y}" width="{wn}" height="{hn}" rx="14" fill="{C["cartao"]}" stroke="{cor if destaque else C["borda"]}" stroke-opacity="{".55" if destaque else "1"}"/>'
            f'<rect x="{n(x + 12)}" y="{y + 13}" width="32" height="32" rx="10" fill="{C["verde_suave"]}"/>'
            + icone(ic, x + 19, y + 20, 18, C["verde"])
            + texto(x + 54, y + 26, esc(tit), 12, 750, C["texto"])
            + texto(x + 54, y + 43, esc(sub), 10.5, 500, C["tenue"])
        )

    def ligar(i, x1, x2, y, atraso, duplo=False):
        d = f"M{n(x1)} {y} H{n(x2 - 7)}"
        defs.append(f'<path id="lig{i}" d="{d}"/>')
        out = [
            f'<path d="{d}" fill="none" stroke="{C["borda2"]}" stroke-width="1.6"/>',
            f'<path d="{d}" fill="none" stroke="{C["verde"]}" stroke-opacity=".5" stroke-width="1.6" stroke-dasharray="3 6" style="animation:fluir 1.2s linear infinite"/>',
            f'<path d="M{n(x2 - 7)} {y - 4.5} L{n(x2)} {y} L{n(x2 - 7)} {y + 4.5}" fill="none" stroke="{C["verde"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<circle r="4" fill="{C["verde"]}" opacity="0"><animateMotion dur="4s" begin="{atraso}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.25;1" calcMode="linear"><mpath href="#lig{i}"/></animateMotion>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.03;.22;.26;1" dur="4s" begin="{atraso}s" repeatCount="indefinite"/></circle>',
        ]
        if duplo:
            out.append(f'<path d="M{n(x1 + 7)} {y - 4.5} L{n(x1)} {y} L{n(x1 + 7)} {y + 4.5}" fill="none" stroke="{C["verde"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
        return "".join(out)

    p.append(texto(x0, 40, "Como funciona", 15, 800, C["texto"]))
    p.append(texto(W - x0, 40, "no teu navegador", 10.5, 500, C["tenue"], "end"))
    y1 = 64
    linha1 = [
        ("file-code", "src/data/mock.ts", f'{DADOS["filmes"] + DADOS["series"]} títulos fictícios'),
        ("layers", "React 19 + Router", f'{DADOS["paginas"]} páginas'),
        ("workflow", "Zustand", "estado com persist"),
        ("hard-drive", "localStorage", "o que guardas"),
    ]
    for i, (ic, t, s) in enumerate(linha1):
        x = x0 + i * (wn + gap)
        p.append(f'<g style="animation:surgir .6s {CURVA} {0.1 + i * 0.08:.2f}s both">{no(x, y1, ic, t, s, i == 3)}</g>')
        if i:
            p.append(ligar(i, x - gap, x, y1 + hn / 2, 0.5 * i, duplo=(i == 3)))
    p.append(texto(x0, 160, "Publicação", 15, 800, C["texto"]))
    p.append(texto(W - x0, 160, "a cada envio para o main", 10.5, 500, C["tenue"], "end"))
    y2 = 184
    linha2 = [
        ("git-branch", "git push", "no ramo main"),
        ("rocket", "GitHub Actions", "npm ci · npm run build"),
        ("package", "dist/", "só ficheiros estáticos"),
        ("globe", "GitHub Pages", "a demo ao vivo"),
    ]
    for i, (ic, t, s) in enumerate(linha2):
        x = x0 + i * (wn + gap)
        p.append(f'<g style="animation:surgir .6s {CURVA} {0.4 + i * 0.08:.2f}s both">{no(x, y2, ic, t, s, i == 3)}</g>')
        if i:
            p.append(ligar(10 + i, x - gap, x, y2 + hn / 2, 2 + 0.5 * i))
    notas = [("server-off", "Sem API nem base de dados"), ("key-round", "Sem chaves nem .env"), ("eye-off", "O que fazes não sai do navegador")]
    xn, yn = x0, H - 52
    for ic, t in notas:
        w = FONTE.largura(t, 11, 600) + 46
        p.append(
            f'<rect x="{n(xn)}" y="{yn}" width="{n(w)}" height="30" rx="15" fill="{C["cartao"]}" stroke="{C["borda"]}"/>'
            + icone(ic, xn + 12, yn + 8, 14, C["verde"], 2.2)
            + texto(xn + 32, yn + 19.5, esc(t), 11, 600, C["suave"])
        )
        xn += w + 10
    corpo = f"<defs>{''.join(defs)}</defs>" + "".join(p)
    return documento(
        W,
        H,
        "Como a demo funciona",
        "No navegador: os dados fictícios de src/data/mock.ts alimentam as páginas em React 19 com React Router; o estado "
        "(watchlist, gostos e críticas) vive no Zustand e guarda-se no localStorage. Publicação: cada envio para o main "
        "corre o GitHub Actions (npm ci e npm run build) e publica a pasta dist no GitHub Pages. Sem API, sem base de dados "
        "e sem chaves.",
        "",
        corpo,
    )


def main() -> int:
    gerar = {
        "banner.svg": banner,
        "ecras.svg": ecras,
        "telemovel.svg": telemovel,
        "funcoes.svg": funcoes,
        "comparacao.svg": comparacao,
        "como.svg": como,
    }
    so = set(sys.argv[1:])
    for nome, fn in gerar.items():
        if so and nome not in so and nome[:-4] not in so:
            continue
        svg = fn()
        (AQUI / nome).write_text(svg, encoding="utf-8")
        print(f"{nome}: {len(svg.encode()) / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
