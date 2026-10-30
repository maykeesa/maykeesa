"""Recorta o fundo da foto (GrabCut) e realça contraste (CLAHE).

Uso: python scripts/prep_photo.py foto.png
Saída: data/portrait-prepped.png — tons de cinza, fundo preto (0).
Roda só local; o CI não precisa disso.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "portrait-prepped.png"


def remover_fundo(imagem: np.ndarray) -> np.ndarray:
    altura, largura = imagem.shape[:2]
    mascara = np.zeros((altura, largura), np.uint8)
    margem = int(largura * 0.02)
    retangulo = (margem, margem, largura - 2 * margem, altura - margem)
    fundo_modelo = np.zeros((1, 65), np.float64)
    frente_modelo = np.zeros((1, 65), np.float64)
    cv2.grabCut(imagem, mascara, retangulo, fundo_modelo, frente_modelo, 8, cv2.GC_INIT_WITH_RECT)
    frente = np.where((mascara == cv2.GC_FGD) | (mascara == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    # mantém só o maior componente conectado (a pessoa) e fecha buracos
    quantidade, rotulos, stats, _ = cv2.connectedComponentsWithStats(frente)
    if quantidade > 1:
        maior = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        frente = np.where(rotulos == maior, 255, 0).astype(np.uint8)
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    frente = cv2.morphologyEx(frente, cv2.MORPH_CLOSE, nucleo)
    return cv2.GaussianBlur(frente, (5, 5), 0)


def enquadrar_busto(imagem: np.ndarray, mascara: np.ndarray, lado_rel: float = 0.48) -> tuple[np.ndarray, np.ndarray]:
    """Recorta um quadrado de cabeça + ombros a partir do topo da silhueta."""
    linhas_pessoa = np.where(mascara.max(axis=1) > 128)[0]
    if len(linhas_pessoa) == 0:
        return imagem, mascara
    topo_cabeca = int(linhas_pessoa[0])
    altura_total, largura_total = mascara.shape
    lado = int(min(altura_total, largura_total) * lado_rel)
    faixa_cabeca = mascara[topo_cabeca : topo_cabeca + lado // 4]
    centro_x = int(np.mean(np.where(faixa_cabeca > 128)[1]))
    topo = max(0, topo_cabeca - lado // 14)
    esquerda = max(0, min(centro_x - int(lado * 0.44), largura_total - lado))
    corte = (slice(topo, topo + lado), slice(esquerda, esquerda + lado))
    return imagem[corte], mascara[corte]


def preparar(caminho: str) -> None:
    imagem = cv2.imread(caminho, cv2.IMREAD_COLOR)
    if imagem is None:
        raise SystemExit(f"Não consegui abrir {caminho}")
    if imagem.dtype != np.uint8:
        imagem = (imagem / 257).astype(np.uint8)

    mascara = remover_fundo(imagem)
    imagem, mascara = enquadrar_busto(imagem, mascara)
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # estica o histograma usando só a metade de cima (rosto), não a camiseta
    metade = cinza.shape[0] // 2
    pessoa = cinza[:metade][mascara[:metade] > 128]
    baixo, alto = np.percentile(pessoa, (2, 99))
    esticada = np.clip((cinza.astype(np.float32) - baixo) / max(alto - baixo, 1) * 255, 0, 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6))
    realcada = clahe.apply(esticada)
    # atenua o terço de baixo pra camiseta branca não roubar o foco do rosto
    altura = realcada.shape[0]
    atenuacao = np.ones(altura, np.float32)
    inicio = int(altura * 0.66)
    atenuacao[inicio:] = np.linspace(1.0, 0.55, altura - inicio)
    composta = realcada.astype(np.float32) * (mascara.astype(np.float32) / 255) * atenuacao[:, None]
    composta = np.clip(composta, 0, 255).astype(np.uint8)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(SAIDA), composta)
    print(f"foto preparada → {SAIDA}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("uso: python scripts/prep_photo.py foto.png")
    preparar(sys.argv[1])
