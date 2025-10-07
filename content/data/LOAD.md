
```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/asabatba/grafos-nbs-25/refs/heads/main/content/data/dependency_nodes.csv' AS row
CREATE (:Job {name: row.name, duration_avg: toFloat(row.duration_avg), duration_std: toFloat(row.duration_std)});

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/asabatba/grafos-nbs-25/refs/heads/main/content/data/dependency_edges.csv' AS row
MATCH (src:Job {name: row.source})
MATCH (dst:Job {name: row.target})
CREATE (src)-[:DEPENDS_ON]->(dst);

CREATE INDEX job_name_index FOR (j:Job) ON (j.name);
```

```cypher
MATCH (n) DETACH DELETE n;


MATCH (j:Job)
WHERE NOT (:Job)-[:DEPENDS_ON]->(j)
RETURN j AS FinalJobs;


MATCH p = (root:Job)<-[r:DEPENDS_ON*]-(j:Job {name:"TealPagefurt"})
WITH p, reduce(total=0.0, rel IN relationships(p) | total + rel.average_duration) AS totalDuration
ORDER BY totalDuration DESC
LIMIT 3
RETURN p AS CriticalPath, totalDuration;


```

```cypher

MATCH (j: Job)
WHERE j.name in ["ChocolatePartfurt", "RedGroundfort", "AntiqueWhiteTravelstad"]
SET j.key = true

```



```
CALL apoc.periodic.iterate(
  "
  MATCH (j:Job)
  WHERE NOT (j)-[:DEPENDS_ON]->()
  RETURN j
  ",
  "
  SET j.ES = 0,
      j.EF = j.duration_avg
  ",
  {batchSize:100}
)
```

```
CALL apoc.periodic.iterate(
  "
  MATCH (j:Job)
  WHERE (j)-[:DEPENDS_ON]->(:Job)
  RETURN j
  ",
  "
  WITH j
  MATCH (pred:Job)<-[:DEPENDS_ON]-(j)
  WITH j, max(pred.EF) AS maxEF
  SET j.ES = maxEF,
      j.EF = maxEF + j.duration_avg
  ",
  {batchSize:100, parallel:false}
)
```

