"""Gera stack-banner.svg: bancos de memória (stack) à esquerda e banner ASCII vazado à direita."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from make_ascii_svg import CSS_FAIXAS, desenhar_grade, gerar_grade
from tema import APAGADO, ESTATICO, abrir_svg, caixa, moldura, prompt

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "stack-banner.svg"
FONTE = "C:/Windows/Fonts/consolab.ttf"  # só roda local; o SVG gerado é commitado

LARGURA = 860
ALTURA = 210
NOME = "MAYKE"

BANCOS = [
    ("BANK 1", ["JAVA", "KOTLIN", "GROOVY", "PYTHON"]),
    ("BANK 2", ["SPRING BOOT", "GRAILS", "JPA", "REST API"]),
    ("BANK 3", ["POSTGRES", "MYSQL", "ORACLE", "MONGODB"]),
    ("BANK 4", ["DOCKER", "RABBITMQ", "GIT", "LINUX"]),
]


def banner() -> Image.Image:
    """Texto com contorno (miolo preto), pra virar letras vazadas em ASCII."""
    imagem = Image.new("L", (1600, 400), 0)
    desenho = ImageDraw.Draw(imagem)
    fonte = ImageFont.truetype(FONTE, 400)
    caixa_texto = desenho.textbbox((0, 0), NOME, font=fonte)
    x = (1600 - (caixa_texto[2] - caixa_texto[0])) // 2 - caixa_texto[0]
    y = (400 - (caixa_texto[3] - caixa_texto[1])) // 2 - caixa_texto[1]
    desenho.text((x, y), NOME, font=fonte, fill=0, stroke_width=14, stroke_fill=255)
    return imagem


def renderizar() -> str:
    linhas = []
    for n, (nome, itens) in enumerate(BANCOS):
        y = 58 + n * 34
        anim = "" if ESTATICO else f' style="animation-delay:{0.4 + n * 0.25:.2f}s"'
        celulas = "".join(
            f'<text class="forte" x="{98 + i * 78}" y="{y}" style="font-size:11px">{item}</text>'
            for i, item in enumerate(itens)
        )
        linhas.append(f'<g class="ln"{anim}><text class="dim" x="24" y="{y}">{nome}</text>{celulas}</g>')

    clips, textos = desenhar_grade(gerar_grade(banner(), 150), 440, 56, 396, ALTURA - 76, "b")
    css = f"text{{white-space:pre}}\n{CSS_FAIXAS}\n.t3,.t4{{fill:#8ff7d4}}\n"
    if not ESTATICO:
        css += ".ln{opacity:0;animation:entra .4s steps(4) forwards}\n@keyframes entra{to{opacity:1}}\n"
    corpo = f"""<defs>{clips}</defs>
{moldura(LARGURA, ALTURA, prompt("ls ./stack"), "PORT......4")}
{caixa(16, 38, 400, ALTURA - 54, APAGADO, 0.8)}
{"".join(linhas)}
<text class="fraco" x="24" y="{ALTURA - 26}">&gt; HOT-SWAP OK <tspan class="cursor">_</tspan></text>
<g xml:space="preserve">
{textos}
</g>
<text class="fraco" x="{LARGURA - 18}" y="{ALTURA - 14}" text-anchor="end" style="font-size:9px">(C)</text>"""
    return abrir_svg(LARGURA, ALTURA, css, corpo)


if __name__ == "__main__":
    SAIDA.write_text(renderizar(), encoding="utf-8")
    print(f"banner -> {SAIDA}")
