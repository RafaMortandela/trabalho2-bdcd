"""
Limpa e filtra os CSVs brutos e gera arquivos prontos pro LOAD CSV do Neo4j.

Filtros:
- Deputados: 57ª legislatura (um registro por deputado, partido mais recente).
- Frentes: só as da 57ª legislatura.
- Proposições: apresentadas em 2025, só tipos de projeto (PL, PLP, PEC, PDL, MPV, PRC),
  mais qualquer proposição (de qualquer ano) que tenha ido a votação nominal em 2025.
- Autoria: só autores que são deputados da 57ª legislatura.
- Votações: só as nominais de 2025 (as que têm votos individuais).

Uso: python3 scripts/02_preprocessamento.py
Saída: dados/neo4j/*.csv
"""
import csv
import os
import sys

csv.field_size_limit(sys.maxsize)

ANO = 2025
LEG = "57"
TIPOS = {"PL", "PLP", "PEC", "PDL", "MPV", "PRC"}
RAIZ = os.path.join(os.path.dirname(__file__), "..", "dados")
BRUTOS = os.path.join(RAIZ, "brutos")
SAIDA = os.path.join(RAIZ, "neo4j")


def ler(nome):
    with open(os.path.join(BRUTOS, nome), encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f, delimiter=";")


def escrever(nome, campos, linhas):
    with open(os.path.join(SAIDA, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(campos)
        n = 0
        for l in linhas:
            w.writerow(l)
            n += 1
    print(f"{nome}: {n} linhas")


def limpa(txt, tam=500):
    return " ".join((txt or "").split())[:tam]


def id_de_uri(uri):
    return uri.rstrip("/").rsplit("/", 1)[-1]


os.makedirs(SAIDA, exist_ok=True)

# Deputados (a API repete o deputado quando ele troca de partido; fica o último)
deputados = {}
for r in ler("deputados.csv"):
    deputados[r["id"]] = r
escrever("deputados.csv", ["id", "nome", "partido", "uf"],
         ([d["id"], d["nome"], d["siglaPartido"], d["siglaUf"]] for d in deputados.values()))

# Frentes e membros
frentes = {r["id"]: r for r in ler("frentes.csv") if r["idLegislatura"] == LEG}
escrever("frentes.csv", ["id", "titulo", "dataCriacao"],
         ([f["id"], limpa(f["titulo"]), f["dataCriacao"]] for f in frentes.values()))
escrever("frentes_membros.csv", ["idFrente", "idDeputado", "papel"],
         ([r["id"], r["deputado_.id"], r["deputado_.titulo"]] for r in ler("frentesDeputados.csv")
          if r["id"] in frentes and r["deputado_.id"] in deputados))

# Votações nominais
votos = [r for r in ler(f"votacoesVotos-{ANO}.csv") if r["deputado_id"] in deputados]
ids_votacoes = {v["idVotacao"] for v in votos}
escrever("votos.csv", ["idVotacao", "idDeputado", "voto"],
         ([v["idVotacao"], v["deputado_id"], v["voto"]] for v in votos))
escrever("votacoes.csv", ["id", "data", "orgao", "aprovacao", "votosSim", "votosNao", "descricao"],
         ([v["id"], v["data"], v["siglaOrgao"], v["aprovacao"], v["votosSim"], v["votosNao"],
           limpa(v["descricao"], 300)]
          for v in ler(f"votacoes-{ANO}.csv") if v["id"] in ids_votacoes))

# Ligação votação -> proposição (e proposições votadas, mesmo de outros anos)
vot_prop = [r for r in ler(f"votacoesProposicoes-{ANO}.csv") if r["idVotacao"] in ids_votacoes]
escrever("votacoes_proposicoes.csv", ["idVotacao", "idProposicao"],
         ([r["idVotacao"], r["proposicao_id"]] for r in vot_prop))

proposicoes = {}
for r in vot_prop:
    proposicoes[r["proposicao_id"]] = [r["proposicao_id"], r["proposicao_siglaTipo"], r["proposicao_numero"],
                                       r["proposicao_ano"], "", limpa(r["proposicao_ementa"])]
for r in ler(f"proposicoes-{ANO}.csv"):
    if r["siglaTipo"] in TIPOS or r["id"] in proposicoes:
        proposicoes[r["id"]] = [r["id"], r["siglaTipo"], r["numero"], r["ano"],
                                r["dataApresentacao"][:10], limpa(r["ementa"])]
escrever("proposicoes.csv", ["id", "siglaTipo", "numero", "ano", "dataApresentacao", "ementa"],
         proposicoes.values())

# Autoria (só deputados)
escrever("autorias.csv", ["idProposicao", "idDeputado", "ordemAssinatura", "proponente"],
         ([r["idProposicao"], r["idDeputadoAutor"], r["ordemAssinatura"], r["proponente"]]
          for r in ler(f"proposicoesAutores-{ANO}.csv")
          if r["idProposicao"] in proposicoes and r["idDeputadoAutor"] in deputados))

# Temas
escrever("temas.csv", ["idProposicao", "codTema", "tema"],
         ([id_de_uri(r["uriProposicao"]), r["codTema"], r["tema"]]
          for r in ler(f"proposicoesTemas-{ANO}.csv") if id_de_uri(r["uriProposicao"]) in proposicoes))
