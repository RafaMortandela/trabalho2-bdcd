"""
Coleta dos dados do Portal de Dados Abertos da Câmara dos Deputados.

- Deputados da 57ª legislatura (2023-2027) vêm da API REST (/deputados),
  porque o CSV de deputados não traz o partido atual.
- O resto vem dos arquivos CSV anuais (bulk) do portal, ano de 2025.

Uso: python3 scripts/01_coleta.py
Saída: dados/brutos/*.csv
"""
import csv
import json
import os
import hashlib
import time
import urllib.request
from datetime import datetime, timezone

LEGISLATURA = 57
ANO = 2025
BASE_API = "https://dadosabertos.camara.leg.br/api/v2"
BASE_ARQ = "https://dadosabertos.camara.leg.br/arquivos"
PASTA = os.path.join(os.path.dirname(__file__), "..", "dados", "brutos")

ARQUIVOS = {
    "frentes.csv": f"{BASE_ARQ}/frentes/csv/frentes.csv",
    "frentesDeputados.csv": f"{BASE_ARQ}/frentesDeputados/csv/frentesDeputados.csv",
    f"proposicoes-{ANO}.csv": f"{BASE_ARQ}/proposicoes/csv/proposicoes-{ANO}.csv",
    f"proposicoesAutores-{ANO}.csv": f"{BASE_ARQ}/proposicoesAutores/csv/proposicoesAutores-{ANO}.csv",
    f"proposicoesTemas-{ANO}.csv": f"{BASE_ARQ}/proposicoesTemas/csv/proposicoesTemas-{ANO}.csv",
    f"votacoes-{ANO}.csv": f"{BASE_ARQ}/votacoes/csv/votacoes-{ANO}.csv",
    f"votacoesVotos-{ANO}.csv": f"{BASE_ARQ}/votacoesVotos/csv/votacoesVotos-{ANO}.csv",
    f"votacoesProposicoes-{ANO}.csv": f"{BASE_ARQ}/votacoesProposicoes/csv/votacoesProposicoes-{ANO}.csv",
}


def get_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def coletar_deputados():
    """Percorre a paginação da API e salva os deputados da legislatura."""
    url = f"{BASE_API}/deputados?idLegislatura={LEGISLATURA}&itens=100&ordem=ASC&ordenarPor=nome"
    deputados = []
    while url:
        resp = get_json(url)
        deputados.extend(resp["dados"])
        url = next((l["href"] for l in resp["links"] if l["rel"] == "next"), None)

    campos = ["id", "nome", "siglaPartido", "siglaUf", "idLegislatura", "email"]
    destino = os.path.join(PASTA, "deputados.csv")
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(deputados)
    print(f"deputados.csv: {len(deputados)} registros")


def baixar_arquivos():
    for nome, url in ARQUIVOS.items():
        destino = os.path.join(PASTA, nome)
        if os.path.exists(destino):
            print(f"{nome}: já existe, pulando")
            continue
        print(f"baixando {nome} ...")
        temporario = destino + ".part"
        for tentativa in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "bdcd-coleta/1.0"})
                with urllib.request.urlopen(req, timeout=120) as origem, open(temporario, "wb") as saida:
                    while True:
                        bloco = origem.read(1024 * 1024)
                        if not bloco:
                            break
                        saida.write(bloco)
                os.replace(temporario, destino)
                break
            except (OSError, TimeoutError):
                if os.path.exists(temporario):
                    os.remove(temporario)
                if tentativa == 2:
                    raise
                time.sleep(2 ** tentativa)


def registrar_fontes():
    """Registra URLs e hashes do snapshot local, sem guardar credenciais."""
    fontes = dict(ARQUIVOS)
    fontes["deputados.csv"] = f"{BASE_API}/deputados?idLegislatura={LEGISLATURA}&itens=100&ordem=ASC&ordenarPor=nome"
    arquivos = []
    for nome, url in sorted(fontes.items()):
        caminho = os.path.join(PASTA, nome)
        digest = hashlib.sha256()
        with open(caminho, "rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)
        arquivos.append({"arquivo": "brutos/" + nome, "url": url,
                         "bytes": os.path.getsize(caminho), "sha256": digest.hexdigest()})
    manifesto = {"manifesto_em_utc": datetime.now(timezone.utc).isoformat(),
                 "ano": ANO, "legislatura": LEGISLATURA, "arquivos": arquivos}
    with open(os.path.join(PASTA, "..", "fontes.json"), "w", encoding="utf-8") as arquivo:
        json.dump(manifesto, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")


if __name__ == "__main__":
    os.makedirs(PASTA, exist_ok=True)
    coletar_deputados()
    baixar_arquivos()
    registrar_fontes()
