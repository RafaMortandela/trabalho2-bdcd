# Evidências da execução

As imagens `figuras/consulta_01.png` a `consulta_05.png` são capturas do Neo4j Browser conectado à base local da entrega, em Neo4j 5.26.33. Para manter legibilidade no relatório, as telas mostram uma projeção das colunas principais, definida nos arquivos `vista_01.cypher` a `vista_05.cypher`. Essas consultas envolvem a consulta analítica completa em uma subconsulta e selecionam apenas as colunas exibidas; filtros e métricas são preservados.

Os resultados completos estão em `resultados/*.csv` e `resultados/*.json`. `resultados/validacao.json` registra as contagens verificadas. A conferência matemática independente é executada por `python3 scripts/07_conferir_resultados.py`.

Snapshot: 25/11/2026. Os hashes de cada arquivo original e suas URLs estão em `dados/fontes.json`.
