// Q1: Em quais temas as UFs têm participação proporcionalmente maior?
// Unidade: proposição distinta de 2025 com autor deputado e tema cadastrado.
MATCH (p:Proposicao {ano: 2025})
WHERE EXISTS { (:Deputado)-[:AUTOR_DE]->(p) }
  AND EXISTS { (p)-[:TRATA_DE]->(:Tema) }
WITH count(p) AS totalBrasil
MATCH (e:Estado)<-[:REPRESENTA]-(:Deputado)-[:AUTOR_DE]->(p:Proposicao {ano: 2025})-[:TRATA_DE]->(t:Tema)
WITH totalBrasil, e, t, count(DISTINCT p) AS projetosTemaUF
CALL (e) {
  MATCH (e)<-[:REPRESENTA]-(:Deputado)-[:AUTOR_DE]->(p:Proposicao {ano: 2025})
  WHERE EXISTS { (p)-[:TRATA_DE]->(:Tema) }
  RETURN count(DISTINCT p) AS totalUF
}
CALL (t) {
  MATCH (p:Proposicao {ano: 2025})-[:TRATA_DE]->(t)
  WHERE EXISTS { (:Deputado)-[:AUTOR_DE]->(p) }
  RETURN count(DISTINCT p) AS projetosTemaBrasil
}
WITH *, (1.0 * projetosTemaUF / totalUF) / (1.0 * projetosTemaBrasil / totalBrasil) AS indice
WHERE totalUF >= 100 AND projetosTemaUF >= 30
RETURN e.uf AS uf, t.nome AS tema, projetosTemaUF, totalUF,
       projetosTemaBrasil, totalBrasil,
       round(100.0 * projetosTemaUF / totalUF, 2) AS percentualUF,
       round(100.0 * projetosTemaBrasil / totalBrasil, 2) AS percentualBrasil,
       round(indice, 3) AS indiceEspecializacao
ORDER BY indice DESC, projetosTemaUF DESC, uf, tema LIMIT 10;
