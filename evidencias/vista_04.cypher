CALL () {
// Q4: Quão coesos são os agrupamentos partidários nos votos de Plenário?
// Só Sim/Não. Empate fica no denominador com maioria de 50%.
MATCH (p:Partido)<-[:FILIADO_A]-(d:Deputado)-[r:VOTOU]->(v:Votacao {orgao: 'PLEN'})
WHERE r.voto IN ['Sim', 'Não']
WITH p, v, count(DISTINCT d) AS presentes,
     sum(CASE WHEN r.voto = 'Sim' THEN 1 ELSE 0 END) AS sim
WHERE presentes >= 5
WITH p, count(*) AS votacoes, sum(presentes) AS votos,
     sum(CASE WHEN sim >= presentes - sim THEN sim ELSE presentes - sim END) AS votosMajoritarios
WHERE votacoes >= 100
RETURN p.sigla AS partido, votacoes, votos, votosMajoritarios,
       round(100.0 * votosMajoritarios / votos, 2) AS coesaoPercentual
ORDER BY coesaoPercentual DESC, partido
}
RETURN partido, votacoes, votos, coesaoPercentual;
