// Q5: Coautores de partidos diferentes também divergem no voto?
// Coautores frequentes: >=10 proposições conjuntas e >=100 votos comparáveis.
MATCH (a:Deputado)-[:AUTOR_DE]->(p:Proposicao {ano: 2025})<-[:AUTOR_DE]-(b:Deputado)
WHERE a.id < b.id AND a.partido <> b.partido
WITH a, b, count(DISTINCT p) AS coautorias
WHERE coautorias >= 10
CALL (a, b) {
  MATCH (a)-[ra:VOTOU]->(v:Votacao {orgao: 'PLEN'})<-[rb:VOTOU]-(b)
  WHERE ra.voto IN ['Sim', 'Não'] AND rb.voto IN ['Sim', 'Não']
  RETURN count(*) AS votosComuns,
         sum(CASE WHEN ra.voto = rb.voto THEN 1 ELSE 0 END) AS votosIguais
}
WITH * WHERE votosComuns >= 100
WITH *, 1.0 * votosIguais / votosComuns AS afinidade
ORDER BY afinidade ASC, coautorias DESC, a.id, b.id LIMIT 10
CALL (a, b) {
  MATCH (a)-[:MEMBRO_DE]->(f:Frente)<-[:MEMBRO_DE]-(b)
  RETURN count(DISTINCT f) AS frentesComuns
}
RETURN a.nome AS deputadoA, a.partido AS partidoA,
       b.nome AS deputadoB, b.partido AS partidoB,
       coautorias, frentesComuns, votosComuns, votosIguais,
       round(100.0 * afinidade, 2) AS afinidadePercentual
ORDER BY afinidadePercentual ASC, coautorias DESC, deputadoA, deputadoB;
