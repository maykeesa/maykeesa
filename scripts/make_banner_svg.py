"""Gera stack-banner.svg: bancos de memória (stack) à esquerda e xícara de café do Java em ASCII à direita."""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from make_ascii_svg import CSS_FAIXAS, desenhar_grade, gerar_grade
from tema import APAGADO, ESTATICO, abrir_svg, caixa, moldura, prompt

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "stack-banner.svg"

LARGURA = 860
ALTURA = 240

BANCOS = [
    ("BANK 1", ["JAVA", "KOTLIN", "GROOVY", "PYTHON"]),
    ("BANK 2", ["SPRING BOOT", "GRAILS", "JPA", "REST API"]),
    ("BANK 3", ["POSTGRES", "MYSQL", "ORACLE", "MONGODB"]),
    ("BANK 4", ["DOCKER", "RABBITMQ", "GIT", "LINUX"]),
]


def xicara() -> Image.Image:
    """Xícara de café do logo do Java: vapor, corpo com listra, alça e pires, em tons de cinza."""
    imagem = Image.new("L", (720, 400), 0)
    desenho = ImageDraw.Draw(imagem)
    cx = 360
    for dx, fase in ((-45, 0.0), (35, 1.6)):  # dois fios de vapor ondulados
        pontos = [(cx + dx + 28 * math.sin(fase + t / 22), 12 + t) for t in range(0, 135, 3)]
        desenho.line(pontos, fill=255, width=17, joint="curve")
    desenho.ellipse((cx + 70, 185, cx + 205, 300), outline=255, width=20)  # alça
    desenho.polygon([(cx - 165, 165), (cx + 135, 165), (cx + 115, 295), (cx + 60, 330), (cx - 110, 330), (cx - 150, 295)], fill=255)
    desenho.rectangle((cx - 170, 212, cx + 140, 232), fill=0)  # listra vazada
    desenho.rounded_rectangle((cx - 235, 352, cx + 210, 384), radius=16, fill=200)  # pires
    return imagem


def renderizar() -> str:
    linhas = []
    for n, (nome, itens) in enumerate(BANCOS):
        y = 62 + n * 40
        anim = "" if ESTATICO else f' style="animation-delay:{0.4 + n * 0.25:.2f}s"'
        celulas = "".join(
            f'<text class="forte" x="{98 + i * 78}" y="{y}" style="font-size:11px">{item}</text>'
            for i, item in enumerate(itens)
        )
        linhas.append(f'<g class="ln"{anim}><text class="dim" x="24" y="{y}">{nome}</text>{celulas}</g>')

    clips, textos = desenhar_grade(gerar_grade(xicara(), 70), 470, 44, 340, ALTURA - 62, "b", colunas=70)
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
