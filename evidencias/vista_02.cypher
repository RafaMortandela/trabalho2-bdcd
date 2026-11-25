CALL () {
// Q2: Quais pares de partidos compartilham mais proposições por coautoria?
// Cada projeto conta uma vez por par; pares são ordenados para evitar espelhos.
MATCH (a:Partido)<-[:FILIADO_A]-(:Deputado)-[:AUTOR_DE]->(p:Proposicao {ano: 2025})
      <-[:AUTOR_DE]-(:Deputado)-[:FILIADO_A]->(b:Partido)
WHERE a.sigla < b.sigla
WITH a, b, count(DISTINCT p) AS projetosCompartilhados
CALL (a) {
  MATCH (a)<-[:FILIADO_A]-(:Deputado)-[:AUTOR_DE]->(p:Proposicao {ano: 2025})
  RETURN count(DISTINCT p) AS projetosA
}
CALL (b) {
  MATCH (b)<-[:FILIADO_A]-(:Deputado)-[:AUTOR_DE]->(p:Proposicao {ano: 2025})
  RETURN count(DISTINCT p) AS projetosB
}
RETURN a.sigla AS partidoA, b.sigla AS partidoB, projetosCompartilhados,
       projetosA, projetosB,
       round(100.0 * projetosCompartilhados / (projetosA + projetosB - projetosCompartilhados), 2) AS jaccardPercentual
ORDER BY projetosCompartilhados DESC, partidoA, partidoB LIMIT 10
}
RETURN partidoA, partidoB, projetosCompartilhados, jaccardPercentual;
