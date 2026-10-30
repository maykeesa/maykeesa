"""Converte uma imagem em retrato ASCII verde-fósforo (SVG animado).

Entrada: data/portrait-prepped.png (gerada por prep_photo.py). Sem foto, usa uma cena
procedural (sol com fatias + skyline), só pra o painel não ficar vazio.
Pixel claro vira caractere denso, fundo vira espaço. Cada linha é revelada por um clip
que varre da esquerda pra direita.
"""
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image, ImageDraw

from tema import APAGADO, BRANCO, ESTATICO, MEDIO, VERDE, abrir_svg, caixa, moldura, prompt

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "portrait-prepped.png"
SAIDA = RAIZ / "mayke-ascii.svg"

RAMPA = " .`:-=+*cs#%@"
COLUNAS = 150
FAIXAS = [(1, "t1"), (4, "t2"), (7, "t3"), (10, "t4")]
CSS_FAIXAS = f".t1{{fill:#1d6b57}}.t2{{fill:{MEDIO}}}.t3{{fill:{VERDE}}}.t4{{fill:{BRANCO}}}"


def cena() -> Image.Image:
    """Placeholder: sol com fatias e skyline de janelas acesas, em tons de cinza."""
    lado = 800
    y, x = np.mgrid[0:lado, 0:lado].astype(np.float32)
    cx, cy, raio = lado / 2, 330, 250
    sol = (np.hypot(x - cx, y - cy) < raio).astype(np.float32)
    sol *= np.clip(1.05 - (y - (cy - raio)) / (2 * raio), 0.25, 1.0)
    for n in range(8):
        topo = cy + 20 + n * 34
        sol[(y > topo) & (y < topo + 4 + n * 3)] = 0
    imagem = Image.fromarray((sol * 235).astype(np.uint8))
    desenho = ImageDraw.Draw(imagem)
    sorteio = np.random.default_rng(7)
    x0 = 0
    while x0 < lado:
        largura = int(sorteio.integers(50, 110))
        altura = int(sorteio.integers(120, 360))
        topo = lado - altura
        desenho.rectangle((x0, topo, x0 + largura - 6, lado), fill=0)
        for jx in range(x0 + 10, x0 + largura - 16, 18):
            for jy in range(topo + 14, lado - 10, 24):
                if sorteio.random() < 0.38:
                    desenho.rectangle((jx, jy, jx + 8, jy + 10), fill=255)
        x0 += largura
    for _ in range(40):
        ex, ey = int(sorteio.integers(0, lado)), int(sorteio.integers(0, 150))
        desenho.ellipse((ex, ey, ex + 4, ey + 4), fill=int(sorteio.integers(120, 230)))
    return imagem


def gerar_grade(imagem: Image.Image, colunas: int) -> list[str]:
    linhas = round(colunas * imagem.height / imagem.width * 0.5)
    pixels = np.asarray(imagem.resize((colunas, linhas), Image.LANCZOS), dtype=np.float32) / 255
    indices = np.clip((pixels**0.75) * (len(RAMPA) - 1) + 0.5, 0, len(RAMPA) - 1).astype(int)
    indices[pixels < 0.04] = 0
    return ["".join(RAMPA[i] for i in linha).rstrip() for linha in indices]


def classe_do(caractere: str) -> str:
    indice = RAMPA.index(caractere)
    atual = ""
    for minimo, classe in FAIXAS:
        if indice >= minimo:
            atual = classe
    return atual


def colorir(linha: str) -> str:
    """Agrupa caracteres vizinhos da mesma faixa em <tspan>."""
    partes, trecho, classe_atual = [], "", None
    for caractere in linha:
        classe = classe_do(caractere)
        if classe != classe_atual and trecho:
            partes.append((classe_atual, trecho))
            trecho = ""
        classe_atual = classe
        trecho += caractere
    if trecho:
        partes.append((classe_atual, trecho))
    return "".join(
        f'<tspan class="{classe}">{escape(texto)}</tspan>' if classe else escape(texto)
        for classe, texto in partes
    )


def desenhar_grade(grade: list[str], x: float, y: float, largura: float, altura: float, prefixo: str) -> tuple[str, str]:
    """Devolve (clips, textos) com a grade espremida em (x, y, largura, altura)."""
    altura_linha = altura / len(grade)
    colunas = max(len(l) for l in grade)
    largura_char = largura / colunas
    clips, textos = [], []
    for n, linha in enumerate(grade):
        if not linha:
            continue
        ly = y + (n + 1) * altura_linha
        atributos = (
            f'x="{x}" y="{ly:.2f}" textLength="{len(linha) * largura_char:.2f}" '
            f'lengthAdjust="spacingAndGlyphs" style="font-size:{altura_linha * 0.98:.2f}px"'
        )
        if ESTATICO:
            textos.append(f"<text {atributos}>{colorir(linha)}</text>")
            continue
        inicio = 0.3 + n * 0.045
        clips.append(
            f'<clipPath id="{prefixo}{n}"><rect x="{x}" y="{ly - altura_linha:.2f}" width="0" height="{altura_linha + 1:.2f}">'
            f'<animate attributeName="width" from="0" to="{largura}" begin="{inicio:.2f}s" dur="0.4s" fill="freeze"/>'
            "</rect></clipPath>"
        )
        textos.append(f'<text {atributos} clip-path="url(#{prefixo}{n})">{colorir(linha)}</text>')
    return "".join(clips), "\n".join(textos)


def renderizar() -> str:
    largura, altura = 370, 400
    imagem = Image.open(ENTRADA).convert("L") if ENTRADA.exists() else cena()
    clips, textos = desenhar_grade(gerar_grade(imagem, COLUNAS), 22, 40, largura - 44, altura - 60, "l")
    css = f"text{{white-space:pre}}\n{CSS_FAIXAS}"
    corpo = f"""<defs>{clips}</defs>
{moldura(largura, altura, prompt("whoami"))}
{caixa(16, 34, largura - 32, altura - 50, APAGADO, 0.8)}
<g class="glitch" xml:space="preserve">
{textos}
</g>"""
    return abrir_svg(largura, altura, css, corpo)


if __name__ == "__main__":
    SAIDA.write_text(renderizar(), encoding="utf-8")
    print(f"retrato ASCII -> {SAIDA}")
