"""Gera info-card.svg: script de boot estilo BIOS (@ECHO OFF) com linhas digitadas em sequência.

Edite LINHAS pra atualizar o conteúdo. STATIC=1 gera versão congelada.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from tema import ESTATICO, abrir_svg, moldura

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "info-card.svg"

LARGURA = 490
ALTURA = 400
ESQ = 20
PASSO_LINHA = 16.5

CABECALHO = ["@ECHO OFF", "TITLE MAYKE-OS BIOS", "MODE CON: COLS=80 LINES=30", "COLOR 0A", "CLS"]
LINHAS = [
    ("NOME", "Mayke Erick S. Andrade"),
    ("CLASSE", "Desenvolvedor Back-end"),
    ("FOCO", "Java / Spring Boot · APIs REST"),
    ("ATUAL", "SEFAZ-SE · Dev Jr · desde 10/2024"),
    ("ANTES", "PGM Aracaju · 08/2022 a 06/2024"),
    ("GRAD", "Ciência da Computação · UNIT 2025"),
    ("POS", "Sist. Embarcados Automotivos · UTFPR"),
    ("LINGUAGENS", "Java · Kotlin · Groovy · Python"),
    ("FRAMEWORKS", "Spring Boot · Grails · JPA"),
    ("DADOS", "PostgreSQL · MySQL · Oracle · Mongo"),
    ("INFRA", "Docker · RabbitMQ · Linux · Maven"),
    ("TESTES", "JUnit · Mockito · 100% branch cov."),
    ("PRATICAS", "SOLID · Clean Arch. · Patterns"),
    ("STATUS", "ONLINE"),
]


def animacao(ordem: int) -> str:
    return "" if ESTATICO else f' style="animation-delay:{0.3 + ordem * 0.13:.2f}s"'


def renderizar() -> str:
    y = 48
    blocos = []
    n = 0
    for texto in CABECALHO:
        blocos.append(f'<g class="ln"{animacao(n)}><text class="fraco" x="{ESQ}" y="{y}">{escape(texto)}</text></g>')
        y += PASSO_LINHA
        n += 1
    y += 6
    blocos.append(
        f'<g class="ln"{animacao(n)}><text class="forte" x="{ESQ}" y="{y}" style="font-size:13px">:: MAYKEESA@GITHUB</text></g>'
    )
    y += PASSO_LINHA + 8
    n += 1
    for chave, valor in LINHAS:
        classe = "forte" if chave == "STATUS" else ""
        pontos = "." * (12 - len(chave))
        blocos.append(
            f'<g class="ln"{animacao(n)}><text class="dim" x="{ESQ}" y="{y}">ECHO {escape(chave)}{pontos}:</text>'
            f'<text class="{classe}" x="{ESQ + 112}" y="{y}">{escape(valor)}</text></g>'
        )
        y += PASSO_LINHA
        n += 1
    y += 4
    blocos.append(
        f'<g class="ln"{animacao(n)}><text class="dim" x="{ESQ}" y="{y}">C:\\MAYKE&gt;</text></g>'
        f'<rect class="cursor" x="{ESQ + 62}" y="{y - 10}" width="7" height="12" fill="#8ff7d4"/>'
    )

    css = ""
    if not ESTATICO:
        css = """
.ln{opacity:0;animation:entra .3s steps(4) forwards}
@keyframes entra{to{opacity:1}}
"""
    return abrir_svg(LARGURA, ALTURA, css, moldura(LARGURA, ALTURA, "BOOT.BAT", "PORT......2") + "\n".join(blocos))


if __name__ == "__main__":
    SAIDA.write_text(renderizar(), encoding="utf-8")
    print(f"card -> {SAIDA}")
