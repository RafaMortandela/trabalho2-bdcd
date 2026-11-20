// Amostra do grafo com todos os tipos de nó e de relacionamento (para o print do Neo4j Browser).
MATCH (d:Deputado)-[a:AUTOR_DE]->(p:Proposicao {siglaTipo: 'PL'})<-[s:SOBRE]-(v:Votacao)<-[vo:VOTOU]-(d)
WITH d, a, p, s, v, vo LIMIT 6
MATCH (d)-[f:FILIADO_A]->(pa:Partido)
MATCH (d)-[r:REPRESENTA]->(e:Estado)
MATCH (p)-[t:TRATA_DE]->(tm:Tema)
CALL (d) { MATCH (d)-[m:MEMBRO_DE]->(fr:Frente) RETURN m, fr LIMIT 2 }
RETURN *;
