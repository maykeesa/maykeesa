"""Renderiza data/contributions.json como painel BIOS com heatmap de contribuições."""
import json
from datetime import date
from pathlib import Path

from tema import APAGADO, ESTATICO, abrir_svg, caixa, moldura, prompt

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "contributions.json"
SAIDA = RAIZ / "contrib-heatmap.svg"

PALETA = ["#0a2a22", "#14614d", "#1f9f7e", "#4fe0b4", "#a8ffe6", "#ffffff"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ABAS = ["SUMMARY", "STACK", "BOOT", "SEQ", "MORE+"]

LARGURA = 860
ESQ = 56
DIR = 24
TOPO = 150


def maior_sequencia(dias: list[dict]) -> int:
    maior = atual = 0
    for dia in dias:
        atual = atual + 1 if dia["contagem"] > 0 else 0
        maior = max(maior, atual)
    return maior


def renderizar(dados: dict) -> str:
    dias = dados["dias"]
    primeiro = date.fromisoformat(dias[0]["data"])
    deslocamento = (primeiro.weekday() + 1) % 7  # domingo = 0

    total_colunas = (len(dias) + deslocamento + 6) // 7
    passo = (LARGURA - ESQ - DIR) / total_colunas
    celula = round(passo * 0.8, 2)

    celulas = []
    rotulos_mes = []
    mes_anterior = None
    for i, dia in enumerate(dias):
        coluna, linha = divmod(i + deslocamento, 7)
        x = round(ESQ + coluna * passo, 2)
        y = round(TOPO + linha * passo, 2)
        cor = PALETA[5] if dia["contagem"] >= 20 else PALETA[min(dia["nivel"], 4)]
        anim = "" if ESTATICO else f' style="animation-delay:{0.5 + (coluna + linha) * 0.018:.3f}s"'
        celulas.append(
            f'<rect class="c" x="{x}" y="{y}" width="{celula}" height="{celula}" fill="{cor}"{anim}>'
            f'<title>{dia["data"]}: {dia["contagem"]}</title></rect>'
        )
        mes = date.fromisoformat(dia["data"]).month
        if linha == 0 and mes != mes_anterior:
            if rotulos_mes and coluna - rotulos_mes[-1][0] < 3:
                rotulos_mes.pop()  # mês anterior ocupou menos de 3 colunas: evita sobreposição
            rotulos_mes.append((coluna, f'<text class="dim" x="{x}" y="{TOPO - 10}">{MESES[mes - 1].upper()}</text>'))
            mes_anterior = mes

    rotulos_dia = "".join(
        f'<text class="dim" x="{ESQ - 10}" y="{TOPO + l * passo + 10}" text-anchor="end">{nome}</text>'
        for l, nome in [(1, "SEG"), (3, "QUA"), (5, "SEX")]
    )

    base = TOPO + 7 * passo + 16
    legenda_x = ESQ + total_colunas * passo - 5 * passo - 60
    legenda = f'<text class="dim" x="{legenda_x - 8}" y="{base + 10}" text-anchor="end">MENOS</text>'
    legenda += "".join(
        f'<rect x="{legenda_x + n * passo}" y="{base}" width="{celula}" height="{celula}" fill="{PALETA[n + 1 if n else 0]}"/>'
        for n in range(5)
    )
    legenda += f'<text class="dim" x="{legenda_x + 5 * passo + 4}" y="{base + 10}">MAIS</text>'

    ativos = sum(1 for d in dias if d["contagem"] > 0)
    recorde = max(dias, key=lambda d: d["contagem"])
    media = dados["total"] / ativos if ativos else 0
    estatisticas = [
        ("TOTAL", f'{dados["total"]}'),
        ("DIAS ATIVOS", f"{ativos}"),
        ("MAIOR SEQUENCIA", f"{maior_sequencia(dias)}d"),
        ("MEDIA/DIA ATIVO", f"{media:.1f}"),
        ("MELHOR DIA", f'{recorde["contagem"]}'),
    ]
    rodape_y = base + 44
    rodape = ""
    coluna_largura = (LARGURA - 2 * 28) / len(estatisticas)
    for n, (rotulo, valor) in enumerate(estatisticas):
        x = 28 + n * coluna_largura
        anim = "" if ESTATICO else f' style="animation-delay:{2.2 + n * 0.12:.2f}s"'
        rodape += (
            f'<g class="ln"{anim}><text class="num" x="{x}" y="{rodape_y}">{valor}</text>'
            f'<text class="dim" x="{x}" y="{rodape_y + 17}">{rotulo}</text></g>'
        )

    altura = round(rodape_y + 38)
    tabs = "".join(
        f'<text class="aba" x="{LARGURA * (2 * n + 1) / (2 * len(ABAS))}" y="84" text-anchor="middle">{nome}</text>'
        for n, nome in enumerate(ABAS)
    )
    caixa_conteudo_y = 100
    css = """
.num{font-size:20px;font-weight:700;fill:#e8fff7}
.aba{font-size:16px;letter-spacing:1px}
.topo{font-size:12px;letter-spacing:1.5px}
"""
    if not ESTATICO:
        css += """
.c{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s steps(5) forwards}
@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}
.ln{opacity:0;animation:desce .4s steps(4) forwards}
@keyframes desce{to{opacity:1}}
"""
    corpo = f"""{moldura(LARGURA, altura, barra=False)}
<text class="topo" x="22" y="30">MAYKE-OS BIOS (TM)</text>
<text class="topo dim" x="230" y="30">COPYRIGHT MAYKEESA (C) 2026</text>
<text class="topo dim" x="520" y="30">RESEARCH</text>
<text class="topo dim" x="640" y="30">VER V1.03</text>
<text class="topo dim" x="{LARGURA - 22}" y="30" text-anchor="end">PORT......3</text>
{caixa(18, 58, LARGURA - 36, 38)}
{tabs.replace('y="84"', 'y="83"')}
{caixa(18, caixa_conteudo_y, LARGURA - 36, altura - caixa_conteudo_y - 18, APAGADO, 0.9)}
<text x="32" y="{caixa_conteudo_y + 26}" style="font-size:12px">{prompt("./contributions.sh")} <tspan class="cursor">_</tspan></text>
{"".join(r for _, r in rotulos_mes)}
{rotulos_dia}
{"".join(celulas)}
{legenda}
{rodape}"""
    return abrir_svg(LARGURA, altura, css, corpo)


if __name__ == "__main__":
    dados = json.loads(ENTRADA.read_text(encoding="utf-8"))
    SAIDA.write_text(renderizar(dados), encoding="utf-8")
    print(f"heatmap -> {SAIDA}")
