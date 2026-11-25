# Câmara dos Deputados em grafos com Neo4j

Trabalho de Banco de Dados para Ciência de Dados. **Antonio Adolfo Geraldino Bernardo (828561)** e **Rafaela Silva Ruis (834416)**.

O projeto relaciona deputados, partidos, UFs, frentes parlamentares, proposições, temas e votações. O recorte reúne a 57ª legislatura e votações nominais de 2025. As cinco análises investigam especialização temática, coautoria, pluralidade das frentes, coesão de votos e divergência entre coautores.

## Entrega

- [Relatório em PDF](relatorio/Trabalho2_BDCD_AntonioRafaela.pdf)
- [Dataset original compactado](https://github.com/RafaMortandela/trabalho2-bdcd/releases/download/v1.0-entrega/dataset-original-2026-11-25.zip), com os nove arquivos coletados e o manifesto de fontes
- [Fontes e hashes SHA-256](dados/fontes.json)
- [Relatório de uso de IA](relatorio/uso-de-ia.md)

Os CSVs tratados estão versionados em `dados/neo4j`. Os arquivos originais somam cerca de 306 MB e estão no arquivo da release, com aproximadamente 25 MB compactados. A fonte é pública e recebe atualizações; o snapshot da entrega é identificado pelos hashes do manifesto. Uma nova coleta pode produzir contagens diferentes.

## Reproduzir a carga e as análises

Requisitos: Python 3.9 ou superior e Docker com Compose. Os scripts de dados usam somente a biblioteca padrão do Python. Reserve aproximadamente 2 GB de memória para o Neo4j.

```bash
git clone https://github.com/RafaMortandela/trabalho2-bdcd.git
cd trabalho2-bdcd
docker compose up -d --wait
docker compose exec -T neo4j cypher-shell < scripts/03_importacao.cypher
python3 scripts/06_validar.py --neo4j
python3 scripts/05_executar_consultas.py
python3 scripts/07_conferir_resultados.py
```

O Browser fica em [localhost:17474/browser](http://localhost:17474/browser/). Na conexão, informe `neo4j://localhost:17687`. Essa configuração de desenvolvimento dispensa senha e publica as portas somente na interface local. O script de importação usa `MERGE` e pode ser repetido sobre o mesmo snapshot sem duplicar nós ou relações. Para trocar de snapshot, use uma base vazia, pois `MERGE` não remove registros que desapareceram da fonte.

Execute a [consulta visual](scripts/04_consulta_visual.cypher) no Browser para explorar uma amostra com todos os tipos de nó e relacionamento. A consulta completa `MATCH (n)-[r]->(m) RETURN n,r,m` também é válida, mas seu resultado tem 274 mil relações; a amostra é a figura legível do relatório. A validação por contagens cobre o conjunto inteiro.

### Reproduzir a partir do dataset original da entrega

Baixe o ZIP da release e extraia-o na raiz do repositório, preservando `dados/brutos` e `dados/fontes.json`. Em seguida:

```bash
python3 scripts/02_preprocessamento.py
python3 scripts/06_validar.py
```

Para obter uma **nova coleta** do portal:

```bash
python3 scripts/01_coleta.py
python3 scripts/02_preprocessamento.py
```

O coletor busca deputados com paginação e baixa os oito CSVs do portal. Arquivos bulk já presentes são reaproveitados; remova-os da pasta de trabalho se quiser atualizar esses arquivos. O manifesto registra o conteúdo efetivamente disponível. A deduplicação de deputados mantém o último registro retornado pela API para cada ID; isso não reconstrói a filiação histórica de cada voto.

## Contagens verificadas

| Nó | Quantidade | Relacionamento | Quantidade |
|---|---:|---|---:|
| Deputado | 648 | FILIADO_A | 648 |
| Partido | 22 | REPRESENTA | 648 |
| Estado | 27 | MEMBRO_DE | 65.313 |
| Frente | 320 | AUTOR_DE | 13.123 |
| Proposicao | 8.248 | TRATA_DE | 19.379 |
| Tema | 32 | SOBRE | 568 |
| Votacao | 549 | VOTOU | 174.646 |
| **Total** | **9.846** | **Total** | **274.325** |

São excluídos 421 registros de voto vazio e a votação sem qualquer voto individual válido. Permanecem votos `Sim`, `Não`, `Abstenção`, `Obstrução` e `Artigo 17`; as análises de concordância usam apenas `Sim` e `Não`. Das proposições, 8.104 têm ano 2025 e 144 são de outros anos, vinculadas a votações do recorte. Data de apresentação e campo `ano` não coincidem em todos os registros; os valores da fonte foram preservados.

## Perguntas e resultados

| Pergunta | Consulta | Resultado |
|---|---|---|
| Quais UFs se especializam proporcionalmente em determinados temas? | [Q1](consultas/01_especializacao_uf.cypher) | [CSV](resultados/01_especializacao_uf.csv) |
| Quais pares de partidos mais compartilham projetos por coautoria? | [Q2](consultas/02_pontes_coautoria.cypher) | [CSV](resultados/02_pontes_coautoria.csv) |
| Quais frentes têm composição partidária mais distribuída? | [Q3](consultas/03_pluralidade_frentes.cypher) | [CSV](resultados/03_pluralidade_frentes.csv) |
| Quão coesos são os agrupamentos partidários nos votos de Plenário? | [Q4](consultas/04_coesao_votos.cypher) | [CSV](resultados/04_coesao_votos.csv) |
| Coautores frequentes de partidos diferentes também divergem no voto? | [Q5](consultas/05_coautoria_e_divergencia.cypher) | [CSV](resultados/05_coautoria_e_divergencia.csv) |

Os JSONs guardam todas as colunas e linhas retornadas, e as figuras registram as telas dos resultados. Cada análise inclui filtros mínimos de suporte e interpretação no relatório. Coautoria inclui signatários de apoio, participação em frente não mede atividade e as associações observadas não demonstram causalidade. A filiação é a do registro de deputado escolhido na coleta, não necessariamente a filiação na data da votação.

## Estrutura e verificação

`scripts/01` e `02` coletam e preparam os dados; `03` importa; `04` explora o grafo; `05` executa as cinco consultas; `06` confere chaves, referências, domínio dos votos e contagens CSV/Neo4j; `07` recalcula as métricas diretamente dos CSVs, de forma independente do banco. `consultas/` contém o Cypher analítico, `resultados/` contém as saídas, `figuras/` contém os diagramas e prints e `relatorio/` reúne os documentos da entrega.

`python3 scripts/08_gerar_relatorio_html.py` atualiza a versão HTML a partir do modelo, dos textos analíticos e das saídas versionadas. O PDF é a exportação do Google Docs, com os acréscimos destacados em amarelo para revisão. O hash do ZIP original está em `dados/dataset-original-2026-11-25.zip.sha256`.

A integração contínua carrega uma instância Neo4j limpa, verifica a idempotência da importação, executa as consultas e confere os resultados por Python. A documentação oficial da [API e dos arquivos da Câmara](https://dadosabertos.camara.leg.br/swagger/api.html) descreve as fontes.
