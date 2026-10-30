"""Prepara uma ilustração (mangá, arte, etc.) pro painel ASCII.

Uso: python scripts/prep_arte.py arte.png [--inverter] [--corte 120]
Saída: data/portrait-prepped.png — tons de cinza; tudo abaixo de --corte (0-255) vira preto.
Use --inverter quando o sujeito é escuro sobre fundo claro. Roda só local.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

SAIDA = Path(__file__).resolve().parent.parent / "data" / "portrait-prepped.png"


def preparar(caminho: str, inverter: bool, corte: int) -> None:
    imagem = ImageOps.autocontrast(Image.open(caminho).convert("L"), cutoff=1)
    if inverter:
        imagem = ImageOps.invert(imagem)
    pixels = np.asarray(imagem.filter(ImageFilter.GaussianBlur(0.7)), dtype=np.float32)
    nivel = np.clip((pixels - corte) / (235 - corte), 0, 1)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((nivel * 255).astype(np.uint8)).save(SAIDA)
    print(f"arte preparada -> {SAIDA}")


if __name__ == "__main__":
    analisador = argparse.ArgumentParser()
    analisador.add_argument("arquivo")
    analisador.add_argument("--inverter", action="store_true")
    analisador.add_argument("--corte", type=int, default=0)
    args = analisador.parse_args()
    preparar(args.arquivo, args.inverter, args.corte)
