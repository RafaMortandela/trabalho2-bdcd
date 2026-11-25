"""Executa Cypher no Neo4j 5 via HTTP e salva resultados reais em JSON/CSV.

Uso: python3 scripts/05_executar_consultas.py
Configuração: NEO4J_HTTP_URL (padrão http://localhost:17474),
NEO4J_USER e NEO4J_PASSWORD (opcionais para instâncias autenticadas).
"""
import base64
import csv
import json
import os
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def consultar(cypher):
    base = os.environ.get("NEO4J_HTTP_URL", "http://localhost:17474").rstrip("/")
    body = json.dumps({"statements": [{"statement": cypher}]}).encode()
    headers = {"Content-Type": "application/json"}
    if os.environ.get("NEO4J_PASSWORD"):
        credentials = os.environ.get("NEO4J_USER", "neo4j") + ":" + os.environ["NEO4J_PASSWORD"]
        headers["Authorization"] = "Basic " + base64.b64encode(credentials.encode()).decode()
    request = urllib.request.Request(base + "/db/neo4j/tx/commit", body, headers)
    with urllib.request.urlopen(request, timeout=600) as response:
        result = json.load(response)
    if result["errors"]:
        raise RuntimeError(result["errors"])
    return result["results"][0]


def main():
    output = RAIZ / "resultados"
    output.mkdir(exist_ok=True)
    for path in sorted((RAIZ / "consultas").glob("*.cypher")):
        started = time.monotonic()
        result = consultar(path.read_text())
        rows = [row["row"] for row in result["data"]]
        document = {"consulta": path.relative_to(RAIZ).as_posix(),
                    "colunas": result["columns"], "linhas": rows}
        (output / (path.stem + ".json")).write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n")
        with (output / (path.stem + ".csv")).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(result["columns"])
            writer.writerows(rows)
        print(f"{path.name}: {len(rows)} linhas ({time.monotonic() - started:.2f}s)", flush=True)


if __name__ == "__main__":
    main()
