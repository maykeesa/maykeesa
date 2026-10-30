"""Gera avatar.png: o retrato ASCII verde-fósforo em PNG quadrado, pra usar de foto de perfil.

Usa data/portrait-prepped.png (mesma entrada do painel). Roda só local (precisa da fonte Consolas).
Uso: python scripts/make_avatar.py [lado_em_px]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from make_ascii_svg import ENTRADA, FAIXAS, RAMPA, gerar_grade
from tema import BRANCO, FUNDO, MEDIO, VERDE

SAIDA = Path(__file__).resolve().parent.parent / "avatar.png"
FONTE = "C:/Windows/Fonts/consolab.ttf"
CORES = ["#1d6b57", MEDIO, VERDE, BRANCO]
COLUNAS = 72
ZOOM = 0.82  # fração central da imagem; o GitHub corta o avatar em círculo


def cor_do(caractere: str) -> str | None:
    indice = RAMPA.index(caractere)
    cor = None
    for (minimo, _), tom in zip(FAIXAS, CORES):
        if indice >= minimo:
            cor = tom
    return cor


def gerar(lado: int) -> None:
    arte = Image.open(ENTRADA).convert("L")
    lado_corte = round(arte.width * ZOOM)
    esquerda, topo = (arte.width - lado_corte) // 2, round((arte.height - lado_corte) * 0.6)
    grade = gerar_grade(arte.crop((esquerda, topo, esquerda + lado_corte, topo + lado_corte)), COLUNAS)
    largura_char = lado / COLUNAS
    altura_char = lado / len(grade)
    fonte = ImageFont.truetype(FONTE, round(altura_char * 1.05))
    imagem = Image.new("RGB", (lado, lado), FUNDO)
    desenho = ImageDraw.Draw(imagem)
    for n, linha in enumerate(grade):
        for m, caractere in enumerate(linha):
            cor = cor_do(caractere)
            if cor:
                desenho.text((m * largura_char, n * altura_char), caractere, font=fonte, fill=cor)
    imagem.save(SAIDA)
    print(f"avatar -> {SAIDA}")


if __name__ == "__main__":
    gerar(int(sys.argv[1]) if len(sys.argv) > 1 else 800)
