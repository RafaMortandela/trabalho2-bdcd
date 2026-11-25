"""Gera relatorio/textos.html a partir do modelo e dos resultados versionados."""
import csv
import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def tabela(cabecalho, linhas):
    def row(valores, tag):
        return "<tr>" + "".join(f"<{tag}>{html.escape(str(v))}</{tag}>" for v in valores) + "</tr>"
    return "<table><thead>" + row(cabecalho, "th") + "</thead><tbody>" + "".join(row(l, "td") for l in linhas) + "</tbody></table>"


def codigo(caminho):
    return "<pre>" + html.escape((RAIZ / caminho).read_text()) + "</pre>"


def paragrafo(texto):
    return "<p>" + html.escape(texto) + "</p>"


def imagem(nome, legenda):
    return f'<figure><img src="../figuras/{nome}" alt="{html.escape(legenda)}"><figcaption>{html.escape(legenda)}</figcaption></figure>'


def main():
    conteudo = json.loads((RAIZ / "relatorio/conteudo.json").read_text())
    validacao = json.loads((RAIZ / "resultados/validacao.json").read_text())
    texto = (RAIZ / "relatorio/template.html").read_text()
    for a, b in [("8.247", "8.248"), ("8.103", "8.104"), ("19.378", "19.379"),
                 ("550", "549"), ("429", "428"), ("6.643", "6.644"),
                 ("40 em 2026", "41 em 2026"), ("11.476", "9.846")]:
        texto = texto.replace(a, b)
    texto = texto.replace("(preencher com os nomes completos da dupla)",
                          "Antonio Adolfo Geraldino Bernardo (828561) e Rafaela Silva Ruis (834416)")
    texto = texto.replace("A API repete o deputado quando ele troca de partido. Ficamos só com o registro mais recente, então o partido no grafo é o atual, que pode não ser o mesmo da época de um voto.",
                          "A deduplicação mantém o último registro retornado pela API para cada deputado, sem garantia de cronologia de filiação. Esse partido pode diferir do partido na data do voto.")
    quantidades = [
        ["Deputados", 648], ["Partidos", 22], ["Estados", 27], ["Frentes parlamentares", 320],
        ["Participações em frentes", "65.313"], ["Proposições", "8.248"], ["Autorias", "13.123"],
        ["Temas / ligações proposição-tema", "32 / 19.379"], ["Votações nominais válidas", 549],
        ["Ligações votação-proposição", 568], ["Votos individuais", "174.646"]]
    texto = texto.replace("{{TABELA_DADOS}}", tabela(["Dados", "Quantidade"], quantidades) +
                          paragrafo("Snapshot de 25/11/2026. Os 421 votos vazios e a votação sem votos individuais válidos foram excluídos antes da carga."))
    for token, arquivo in [("COLETA", "01_coleta.py"), ("PREPROC", "02_preprocessamento.py"),
                           ("IMPORT", "03_importacao.cypher"), ("VISUAL", "04_consulta_visual.cypher")]:
        texto = texto.replace("{{CODIGO_" + token + "}}", codigo("scripts/" + arquivo))
    texto = texto.replace("{{CODIGO_CMD}}", "<pre>docker compose up -d --wait\ndocker compose exec -T neo4j cypher-shell &lt; scripts/03_importacao.cypher\npython3 scripts/06_validar.py --neo4j</pre>")
    nos, arestas = validacao["nos"], validacao["relacionamentos"]
    texto = texto.replace("{{TABELA_CONTAGEM}}", tabela(["Nó", "Quantidade", "Relacionamento", "Quantidade"],
        [[n, v, a, q] for (n, v), (a, q) in zip(nos.items(), arestas.items())] +
        [["Total", validacao["totalNos"], "Total", validacao["totalRelacionamentos"]]]))
    for token, arquivo, legenda in [("ESQUEMA", "modelo_esquema.png", "Modelo do grafo"),
                                    ("EXEMPLOS", "modelo_exemplos.png", "Dois exemplos de cada nó e relacionamento"),
                                    ("VISUAL", "consulta_visual.png", "Amostra visual no Neo4j Browser")]:
        texto = texto.replace("{{IMG_" + token + "}}", imagem(arquivo, legenda))
    secoes = paragrafo(conteudo["introducao"])
    for i, analise in enumerate(conteudo["analises"], 1):
        titulo = analise["titulo"].replace("6.", "7.", 1)
        secoes += "<section><h3>" + html.escape(titulo) + "</h3>"
        secoes += paragrafo(analise["pergunta"]) + paragrafo(analise["metodo"])
        secoes += codigo("consultas/" + analise["arquivo"] + ".cypher")
        secoes += imagem(f"consulta_{i:02}.png", f"Consulta {i}: resultado no Neo4j Browser (colunas principais)")
        secoes += "".join(paragrafo(p) for p in analise["analise"]) + "</section>"
    texto = texto.replace("<p>(parte da dupla)</p>", secoes, 1)
    texto = texto.replace("<p>(parte da dupla)</p>", "".join(paragrafo(p) for p in conteudo["conclusao"]), 1)
    ia = "".join("<h3>" + html.escape(s["titulo"]) + "</h3>" + paragrafo(s["texto"]) for s in conteudo["ia"])
    texto = texto.replace("<p>(parte da dupla)</p>", ia, 1)
    texto = texto.replace("(colocar o link do GitHub)", '<a href="https://github.com/RafaMortandela/trabalho2-bdcd">https://github.com/RafaMortandela/trabalho2-bdcd</a>')
    texto = texto.replace("<li>dados/brutos: arquivos originais do portal</li>",
        '<li>dados/brutos: arquivos originais disponíveis na <a href="https://github.com/RafaMortandela/trabalho2-bdcd/releases/tag/v1.0-entrega">release da entrega</a>; URLs e hashes em dados/fontes.json</li>')
    texto = texto.replace("</ul>\n\n<h2>10.",
        "<li>consultas/: cinco consultas analíticas</li><li>resultados/: CSVs, JSONs e validação</li><li>scripts/05 a 07: execução e conferência das métricas</li><li>compose.yaml: ambiente reproduzível</li></ul>\n\n<h2>10.")
    if "{{" in texto or "(parte da dupla)" in texto:
        raise ValueError("Conteúdo incompleto")
    estilo = """body{font:11pt Arial,sans-serif;line-height:1.4;max-width:850px;margin:40px auto;color:#111}
    h1{font-size:22pt}h2{font-size:16pt;margin-top:25px}h3{font-size:13pt;margin-top:20px}
    table{border-collapse:collapse;width:100%;font-size:10pt}td,th{padding:6px;border:1px solid #aaa;text-align:left}
    th{background:#eee}pre{font:8pt monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f5f5;padding:10px}
    figure{margin:18px 0;break-inside:avoid}img{display:block;max-width:100%;max-height:680px;margin:auto}
    figcaption{font-size:9pt;margin-top:5px}a{color:#1655a0}@page{size:A4;margin:20mm}
    @media print{body{margin:0;max-width:none}h2,h3{break-after:avoid}p{orphans:3;widows:3}section{break-before:page}}
    """
    saida = '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Trabalho 2 BDCD</title><style>' + estilo + '</style><body>' + texto + '</body></html>'
    (RAIZ / "relatorio/textos.html").write_text(saida)
    print("relatorio/textos.html gerado")


if __name__ == "__main__":
    main()
