"""Conferência independente: recalcula as cinco análises a partir dos CSVs.

Não usa Neo4j. Compara resultados, denominadores e ordenação com os JSONs
produzidos pela execução das consultas Cypher.
"""
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def ler(nome):
    with (RAIZ / "dados/neo4j" / (nome + ".csv")).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def conferir(prefixo, esperado):
    caminho = next((RAIZ / "resultados").glob(prefixo + "*.json"))
    resultado = json.loads(caminho.read_text())
    obtido = resultado["linhas"]
    if len(esperado) != len(obtido):
        raise ValueError(f"{prefixo}: número de linhas diferente")
    for i, (a, b) in enumerate(zip(esperado, obtido)):
        for x, y in zip(a, b):
            igual = abs(x - y) < 0.00001 if isinstance(x, (int, float)) else x == y
            if not igual:
                raise ValueError(f"{prefixo}, linha {i+1}: {a} != {b}")
        if len(a) != len(b):
            raise ValueError(f"{prefixo}: colunas diferentes")
    print(f"{caminho.stem}: OK ({len(obtido)} linhas)")


def main():
    deputados = {r["id"]: r for r in ler("deputados")}
    projetos = {r["id"] for r in ler("proposicoes") if r["ano"] == "2025"}
    autores = defaultdict(set)
    por_uf = defaultdict(set)
    por_partido = defaultdict(set)
    for r in ler("autorias"):
        if r["idProposicao"] in projetos:
            d = deputados[r["idDeputado"]]
            autores[r["idProposicao"]].add(r["idDeputado"])
            por_uf[d["uf"]].add(r["idProposicao"])
            por_partido[d["partido"]].add(r["idProposicao"])
    temas = defaultdict(set)
    nomes_temas = {}
    for r in ler("temas"):
        nomes_temas[r["codTema"]] = r["tema"]
        if r["idProposicao"] in autores:
            temas[r["codTema"]].add(r["idProposicao"])
    universo = set().union(*temas.values())
    linhas = []
    for uf, ps in por_uf.items():
        total = len(ps & universo)
        for cod, ts in temas.items():
            n = len(ps & ts)
            if total >= 100 and n >= 30:
                indice = (n / total) / (len(ts) / len(universo))
                linhas.append((indice, [uf, nomes_temas[cod], n, total, len(ts), len(universo),
                                      round(100*n/total, 2), round(100*len(ts)/len(universo), 2), round(indice, 3)]))
    linhas.sort(key=lambda x: (-x[0], -x[1][2], x[1][0], x[1][1]))
    conferir("01_", [r for _, r in linhas[:10]])

    linhas = []
    for a, b in itertools.combinations(sorted(por_partido), 2):
        pa, pb = por_partido[a], por_partido[b]
        n = len(pa & pb)
        if n:
            linhas.append([a, b, n, len(pa), len(pb), round(100*n/len(pa | pb), 2)])
    linhas.sort(key=lambda x: (-x[2], x[0], x[1]))
    conferir("02_", linhas[:10])

    frentes = {r["id"]: r["titulo"] for r in ler("frentes")}
    membros = defaultdict(set)
    frentes_deputado = defaultdict(set)
    for r in ler("frentes_membros"):
        membros[r["idFrente"]].add(r["idDeputado"])
        frentes_deputado[r["idDeputado"]].add(r["idFrente"])
    linhas = []
    for f, ids in membros.items():
        c = Counter(deputados[d]["partido"] for d in ids)
        n = len(ids)
        if n >= 100:
            efetivo = n*n/sum(v*v for v in c.values())
            linhas.append((efetivo, [int(f), frentes[f], n, len(c), round(100*max(c.values())/n, 2), round(efetivo, 3)]))
    linhas.sort(key=lambda x: (-x[0], -x[1][2], x[1][0]))
    conferir("03_", [r for _, r in linhas[:10]])

    plen = {r["id"] for r in ler("votacoes") if r["orgao"] == "PLEN"}
    votos = defaultdict(dict)
    por_grupo = defaultdict(Counter)
    for r in ler("votos"):
        if r["idVotacao"] in plen and r["voto"] in {"Sim", "Não"}:
            votos[r["idDeputado"]][r["idVotacao"]] = r["voto"]
            por_grupo[deputados[r["idDeputado"]]["partido"], r["idVotacao"]][r["voto"]] += 1
    totais = defaultdict(lambda: [0, 0, 0])
    for (partido, _), c in por_grupo.items():
        if sum(c.values()) >= 5:
            t = totais[partido]
            t[0] += 1
            t[1] += sum(c.values())
            t[2] += max(c.values())
    linhas = [[p, n, v, m, round(100*m/v, 2)] for p, (n, v, m) in totais.items() if n >= 100]
    linhas.sort(key=lambda x: (-x[4], x[0]))
    conferir("04_", linhas)

    pares = Counter()
    for ids in autores.values():
        for a, b in itertools.combinations(sorted(ids, key=int), 2):
            if deputados[a]["partido"] != deputados[b]["partido"]:
                pares[a, b] += 1
    linhas = []
    for (a, b), n in pares.items():
        if n < 10:
            continue
        comuns = votos[a].keys() & votos[b].keys()
        if len(comuns) < 100:
            continue
        iguais = sum(votos[a][v] == votos[b][v] for v in comuns)
        afinidade = iguais/len(comuns)
        da, db = deputados[a], deputados[b]
        linha = [da["nome"], da["partido"], db["nome"], db["partido"], n,
                 len(frentes_deputado[a] & frentes_deputado[b]), len(comuns), iguais, round(100*afinidade, 2)]
        linhas.append((afinidade, -n, int(a), int(b), linha))
    linhas.sort(key=lambda x: x[:4])
    top = [r[-1] for r in linhas[:10]]
    top.sort(key=lambda x: (x[8], -x[4], x[0], x[2]))
    conferir("05_", top)


if __name__ == "__main__":
    main()
