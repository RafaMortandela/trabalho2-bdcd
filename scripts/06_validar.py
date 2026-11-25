"""Valida chaves, domínios e referências dos CSVs; --neo4j confere a carga.

Não altera dados. Falha com mensagem explícita ao detectar inconsistência.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from importlib import import_module

RAIZ = Path(__file__).resolve().parents[1]


def validar(neo4j=False):
    tabelas = {p.stem: list(csv.DictReader(p.open(encoding="utf-8", newline="")))
               for p in (RAIZ / "dados/neo4j").glob("*.csv")}
    chaves = {"deputados": ("id",), "frentes": ("id",), "proposicoes": ("id",),
              "votacoes": ("id",), "votos": ("idDeputado", "idVotacao"),
              "frentes_membros": ("idDeputado", "idFrente"),
              "autorias": ("idDeputado", "idProposicao"),
              "temas": ("idProposicao", "codTema"),
              "votacoes_proposicoes": ("idVotacao", "idProposicao")}
    for nome, campos in chaves.items():
        keys = [tuple(r[c] for c in campos) for r in tabelas[nome]]
        if any(not all(k) for k in keys) or len(keys) != len(set(keys)):
            raise ValueError(f"Chave vazia ou repetida: {nome} {campos}")
    referencias = [("votos", "idDeputado", "deputados"), ("votos", "idVotacao", "votacoes"),
                   ("frentes_membros", "idDeputado", "deputados"), ("frentes_membros", "idFrente", "frentes"),
                   ("autorias", "idDeputado", "deputados"), ("autorias", "idProposicao", "proposicoes"),
                   ("temas", "idProposicao", "proposicoes"),
                   ("votacoes_proposicoes", "idVotacao", "votacoes"),
                   ("votacoes_proposicoes", "idProposicao", "proposicoes")]
    for origem, campo, destino in referencias:
        ids = {r["id"] for r in tabelas[destino]}
        faltantes = {r[campo] for r in tabelas[origem]} - ids
        if faltantes:
            raise ValueError(f"Referência inexistente em {origem}.{campo}: {faltantes}")
    if any(r["voto"] not in {"Sim", "Não", "Abstenção", "Obstrução", "Artigo 17"}
           for r in tabelas["votos"]):
        raise ValueError("Voto vazio ou fora do domínio")
    if {r["id"] for r in tabelas["votacoes"]} != {r["idVotacao"] for r in tabelas["votos"]}:
        raise ValueError("Votação sem voto válido")
    nos = {"Deputado": len(tabelas["deputados"]), "Frente": len(tabelas["frentes"]),
           "Proposicao": len(tabelas["proposicoes"]), "Votacao": len(tabelas["votacoes"]),
           "Tema": len({r["codTema"] for r in tabelas["temas"]}),
           "Partido": len({r["partido"] for r in tabelas["deputados"]}),
           "Estado": len({r["uf"] for r in tabelas["deputados"]})}
    arestas = {"FILIADO_A": nos["Deputado"], "REPRESENTA": nos["Deputado"],
               "MEMBRO_DE": len(tabelas["frentes_membros"]), "AUTOR_DE": len(tabelas["autorias"]),
               "TRATA_DE": len(tabelas["temas"]), "SOBRE": len(tabelas["votacoes_proposicoes"]),
               "VOTOU": len(tabelas["votos"])}
    if neo4j:
        consultar = import_module("05_executar_consultas").consultar
        for cypher, esperado in [
            ("MATCH (n) RETURN labels(n)[0], count(*)", nos),
            ("MATCH ()-[r]->() RETURN type(r), count(*)", arestas)]:
            obtido = dict(x["row"] for x in consultar(cypher)["data"])
            if obtido != esperado:
                raise ValueError(f"Divergência CSV/Neo4j: {obtido} != {esperado}")
    resultado = {"nos": nos, "relacionamentos": arestas,
                 "totalNos": sum(nos.values()), "totalRelacionamentos": sum(arestas.values()),
                 "votos": dict(Counter(r["voto"] for r in tabelas["votos"]))}
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--neo4j", action="store_true")
    validar(parser.parse_args().neo4j)
