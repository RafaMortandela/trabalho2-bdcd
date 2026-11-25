# Relatório de uso de IA

## Ferramentas e escopo

Codex e Claude foram utilizados como apoio ao desenvolvimento do código, à compreensão da modelagem em grafos e à elaboração do relatório. O apoio incluiu consultas Cypher, revisão de scripts e organização das análises dos resultados.

## Prompts e interações

As interações foram contextualizadas com o enunciado, o repositório e o relatório existente. Os pedidos envolveram identificar requisitos incompletos, formular cinco perguntas analíticas e convertê-las em consultas. O refinamento concentrou-se em contar proposições distintas, definir denominadores, estabelecer filtros mínimos de suporte e distinguir coautoria de concordância no voto.

## Intervenção e integração ao projeto

Os scripts de coleta, pré-processamento e importação, assim como os diagramas, já compunham a estrutura inicial. As consultas analíticas, a conferência independente das métricas e as instruções de reprodução foram desenvolvidas com apoio de IA e integradas a esse fluxo. O tratamento dos votos vazios e as contagens do relatório foram ajustados para manter consistência entre os arquivos tratados e o grafo.

## Validação e testes

A validação conferiu unicidade de chaves, referências entre arquivos, domínio dos votos e contagens de nós e relacionamentos. A importação foi executada novamente para verificar que não duplicava dados. As cinco consultas foram executadas no Neo4j e seus resultados foram recalculados em Python a partir dos CSVs, incluindo proporções, interseções, índices e ordenação. Os arquivos de resultados e os scripts de conferência estão disponíveis no repositório.
