// Q3: Quais frentes têm composição partidária mais distribuída?
// Número efetivo = 1 / soma das proporções partidárias ao quadrado.
MATCH (f:Frente)<-[:MEMBRO_DE]-(d:Deputado)-[:FILIADO_A]->(p:Partido)
WITH f, p, count(DISTINCT d) AS membrosPartido
WITH f, sum(membrosPartido) AS membros, count(*) AS partidos,
     max(membrosPartido) AS maiorBancada, sum(membrosPartido * membrosPartido) AS somaQuadrados
WHERE membros >= 100
RETURN f.id AS idFrente, f.titulo AS frente, membros, partidos,
       round(100.0 * maiorBancada / membros, 2) AS maiorBancadaPercentual,
       round(1.0 * membros * membros / somaQuadrados, 3) AS numeroEfetivoPartidos
ORDER BY numeroEfetivoPartidos DESC, membros DESC, idFrente LIMIT 10;
