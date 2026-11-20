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
import urllib.request

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
        urllib.request.urlretrieve(url, destino)


if __name__ == "__main__":
    os.makedirs(PASTA, exist_ok=True)
    coletar_deputados()
    baixar_arquivos()
