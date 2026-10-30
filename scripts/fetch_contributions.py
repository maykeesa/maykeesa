"""Raspa o calendário público de contribuições e salva em data/contributions.json.

Não precisa de token: usa https://github.com/users/<usuario>/contributions.
"""
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USUARIO = os.environ.get("GH_USER", "maykeesa")
RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "contributions.json"


def extrair_contagem(texto: str) -> int:
    achado = re.match(r"\s*([\d,]+)\s+contribution", texto)
    return int(achado.group(1).replace(",", "")) if achado else 0


def buscar() -> dict:
    resposta = requests.get(
        f"https://github.com/users/{USUARIO}/contributions",
        headers={"User-Agent": "profile-art-bot"},
        timeout=30,
    )
    resposta.raise_for_status()
    sopa = BeautifulSoup(resposta.text, "html.parser")

    contagens = {
        dica.get("for"): extrair_contagem(dica.get_text())
        for dica in sopa.find_all("tool-tip")
    }

    dias = []
    for celula in sopa.select("td.ContributionCalendar-day[data-date]"):
        dias.append(
            {
                "data": celula["data-date"],
                "nivel": int(celula.get("data-level", 0)),
                "contagem": contagens.get(celula.get("id"), 0),
            }
        )
    dias.sort(key=lambda dia: dia["data"])
    if not dias:
        raise SystemExit("Nenhum dia encontrado — o HTML do GitHub mudou?")

    return {
        "usuario": USUARIO,
        "total": sum(dia["contagem"] for dia in dias),
        "dias": dias,
    }


if __name__ == "__main__":
    dados = buscar()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, indent=1, ensure_ascii=False))
    print(f"{len(dados['dias'])} dias · {dados['total']} contribuições → {SAIDA}")
