"""Tema BIOS fósforo-verde compartilhado pelos painéis SVG: paleta, CSS base e molduras."""
import os

ESTATICO = os.environ.get("STATIC") == "1"

FUNDO = "#020b09"
FUNDO2 = "#04150f"
VERDE = "#8ff7d4"  # texto principal
MEDIO = "#3fae8f"
BORDA = "#2a8c74"
APAGADO = "#1f6a56"
BRANCO = "#e8fff7"

CSS_BASE = f"""
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Courier New',monospace;font-size:11px;fill:{VERDE}}}
.dim{{fill:{MEDIO}}}.fraco{{fill:{APAGADO}}}.forte{{fill:{BRANCO};font-weight:700}}
.cabecalho{{font-size:11px;letter-spacing:1.5px}}
"""

CSS_ANIMADO = """
.cursor{animation:pisca 1s steps(1) infinite}
@keyframes pisca{50%{opacity:0}}
.glitch{animation:glitch 5s infinite steps(1)}
@keyframes glitch{0%,93%,100%{transform:none}94%{transform:translateX(-2px)}96%{transform:translateX(3px)}98%{transform:translateX(-1px)}}
.varre{animation:varre 7s linear infinite}
@keyframes varre{from{transform:translateY(0)}to{transform:translateY(var(--h))}}
"""


def caixa(x: float, y: float, largura: float, altura: float, cor: str = BORDA, espessura: float = 1.2) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{largura}" height="{altura}" fill="none" '
        f'stroke="{cor}" stroke-width="{espessura}"/>'
    )


def moldura(largura: int, altura: int, titulo: str = "", direita: str = "", barra: bool = True) -> str:
    """Fundo, scanlines, feixe de varredura, borda dupla e barra de rótulos."""
    varredura = (
        ""
        if ESTATICO
        else f'<rect class="varre" style="--h:{altura}px" x="0" y="-40" width="{largura}" height="40" fill="url(#feixe)"/>'
    )
    rotulos = (
        f'<text class="cabecalho dim" x="14" y="19">{titulo}</text>'
        f'<text class="cabecalho fraco" x="{largura - 14}" y="19" text-anchor="end">{direita}</text>'
        f'<line x1="4.5" y1="26" x2="{largura - 4.5}" y2="26" stroke="{APAGADO}" stroke-width="0.8"/>'
        if barra
        else ""
    )
    return f"""<defs>
<filter id="brilho" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#000" opacity=".4"/></pattern>
<linearGradient id="feixe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VERDE}" stop-opacity="0"/><stop offset="1" stop-color="{VERDE}" stop-opacity=".07"/></linearGradient>
<linearGradient id="fundo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{FUNDO2}"/><stop offset="1" stop-color="{FUNDO}"/></linearGradient>
</defs>
<rect width="{largura}" height="{altura}" fill="url(#fundo)"/>
{varredura}
<rect width="{largura}" height="{altura}" fill="url(#scan)"/>
{caixa(0.6, 0.6, largura - 1.2, altura - 1.2)}
{caixa(4.5, 4.5, largura - 9, altura - 9, APAGADO, 0.8)}
{rotulos}"""


def abrir_svg(largura: int, altura: int, css: str, corpo: str) -> str:
    animado = "" if ESTATICO else CSS_ANIMADO
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">\n'
        f"<style>{CSS_BASE}{animado}{css}</style>\n{corpo}\n</svg>\n"
    )
