"""Gera divider.svg: linha divisória fina com o prompt `cat contato.txt`, entre os painéis e os contatos."""
from pathlib import Path

from tema import BORDA, FUNDO, abrir_svg, prompt

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "divider.svg"

LARGURA = 860
ALTURA = 34


def renderizar() -> str:
    corpo = f"""<line x1="0" y1="17" x2="{LARGURA}" y2="17" stroke="{BORDA}" stroke-width="1.2"/>
<rect x="0" y="9" width="6" height="16" fill="{BORDA}"/><rect x="{LARGURA - 6}" y="9" width="6" height="16" fill="{BORDA}"/>
<rect x="14" y="5" width="256" height="24" fill="{FUNDO}"/>
<text x="22" y="21" style="font-size:12px">{prompt("cat contato.txt")} <tspan class="cursor">_</tspan></text>"""
    return abrir_svg(LARGURA, ALTURA, "", corpo)


if __name__ == "__main__":
    SAIDA.write_text(renderizar(), encoding="utf-8")
    print(f"divisor -> {SAIDA}")
