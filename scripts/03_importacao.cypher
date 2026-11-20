// Importação dos dados da Câmara (57ª legislatura, ano 2025) no Neo4j 5.
// Os CSVs de dados/neo4j precisam estar na pasta import do Neo4j.

// ---------- Restrições (também criam índices) ----------
CREATE CONSTRAINT deputado_id IF NOT EXISTS FOR (d:Deputado) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT partido_sigla IF NOT EXISTS FOR (p:Partido) REQUIRE p.sigla IS UNIQUE;
CREATE CONSTRAINT estado_uf IF NOT EXISTS FOR (e:Estado) REQUIRE e.uf IS UNIQUE;
CREATE CONSTRAINT frente_id IF NOT EXISTS FOR (f:Frente) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT proposicao_id IF NOT EXISTS FOR (p:Proposicao) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT tema_cod IF NOT EXISTS FOR (t:Tema) REQUIRE t.cod IS UNIQUE;
CREATE CONSTRAINT votacao_id IF NOT EXISTS FOR (v:Votacao) REQUIRE v.id IS UNIQUE;

// ---------- Deputados, partidos e estados ----------
LOAD CSV WITH HEADERS FROM 'file:///deputados.csv' AS r
MERGE (d:Deputado {id: toInteger(r.id)})
  SET d.nome = r.nome, d.partido = r.partido, d.uf = r.uf
MERGE (p:Partido {sigla: r.partido})
MERGE (e:Estado {uf: r.uf})
MERGE (d)-[:FILIADO_A]->(p)
MERGE (d)-[:REPRESENTA]->(e);

// ---------- Frentes parlamentares ----------
LOAD CSV WITH HEADERS FROM 'file:///frentes.csv' AS r
MERGE (f:Frente {id: toInteger(r.id)})
  SET f.titulo = r.titulo, f.dataCriacao = date(r.dataCriacao);

LOAD CSV WITH HEADERS FROM 'file:///frentes_membros.csv' AS r
CALL (r) {
  MATCH (d:Deputado {id: toInteger(r.idDeputado)})
  MATCH (f:Frente {id: toInteger(r.idFrente)})
  MERGE (d)-[m:MEMBRO_DE]->(f)
    SET m.papel = r.papel
} IN TRANSACTIONS OF 5000 ROWS;

// ---------- Proposições, autoria e temas ----------
LOAD CSV WITH HEADERS FROM 'file:///proposicoes.csv' AS r
CALL (r) {
  MERGE (p:Proposicao {id: toInteger(r.id)})
    SET p.siglaTipo = r.siglaTipo,
        p.numero = toInteger(r.numero),
        p.ano = toInteger(r.ano),
        p.nome = r.siglaTipo + ' ' + r.numero + '/' + r.ano,
        p.dataApresentacao = CASE r.dataApresentacao WHEN '' THEN null ELSE date(r.dataApresentacao) END,
        p.ementa = r.ementa
} IN TRANSACTIONS OF 5000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///autorias.csv' AS r
CALL (r) {
  MATCH (d:Deputado {id: toInteger(r.idDeputado)})
  MATCH (p:Proposicao {id: toInteger(r.idProposicao)})
  MERGE (d)-[a:AUTOR_DE]->(p)
    SET a.ordemAssinatura = toInteger(r.ordemAssinatura),
        a.proponente = r.proponente = '1'
} IN TRANSACTIONS OF 5000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///temas.csv' AS r
CALL (r) {
  MATCH (p:Proposicao {id: toInteger(r.idProposicao)})
  MERGE (t:Tema {cod: toInteger(r.codTema)})
    SET t.nome = r.tema
  MERGE (p)-[:TRATA_DE]->(t)
} IN TRANSACTIONS OF 5000 ROWS;

// ---------- Votações e votos ----------
LOAD CSV WITH HEADERS FROM 'file:///votacoes.csv' AS r
MERGE (v:Votacao {id: r.id})
  SET v.data = date(r.data),
      v.orgao = r.orgao,
      v.aprovada = r.aprovacao = '1',
      v.votosSim = toInteger(r.votosSim),
      v.votosNao = toInteger(r.votosNao),
      v.descricao = r.descricao;

LOAD CSV WITH HEADERS FROM 'file:///votacoes_proposicoes.csv' AS r
MATCH (v:Votacao {id: r.idVotacao})
MATCH (p:Proposicao {id: toInteger(r.idProposicao)})
MERGE (v)-[:SOBRE]->(p);

LOAD CSV WITH HEADERS FROM 'file:///votos.csv' AS r
CALL (r) {
  WITH r WHERE r.voto IS NOT NULL AND r.voto <> ''
  MATCH (d:Deputado {id: toInteger(r.idDeputado)})
  MATCH (v:Votacao {id: r.idVotacao})
  MERGE (d)-[x:VOTOU]->(v)
    SET x.voto = r.voto
} IN TRANSACTIONS OF 10000 ROWS;
