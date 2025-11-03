
## Carga de datos e índice

```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/asabatba/grafos-nbs-25/refs/heads/main/content/data/dependency_nodes.csv' AS row
CREATE (:Job {name: row.name, duration_avg: toFloat(row.duration_avg), duration_std: toFloat(row.duration_std)});

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/asabatba/grafos-nbs-25/refs/heads/main/content/data/dependency_edges.csv' AS row
MATCH (src:Job {name: row.source})
MATCH (dst:Job {name: row.target})
CREATE (src)-[:DEPENDS_ON]->(dst);

CREATE INDEX job_name_index FOR (j:Job) ON (j.name);
```

* Crea nodos `:Job` a partir de un CSV, con propiedades `name`, `duration_avg` y `duration_std`.
* Crea relaciones `(:Job)-[:DEPENDS_ON]->(:Job)` desde el trabajo **que depende** (`src`) hacia el **requisito previo** (`dst`).
* Crea un índice en `:Job(name)` para acelerar búsquedas por nombre.

## Marcar trabajos clave

```cypher
MATCH (j: Job)
WHERE j.name in ["ChocolatePartfurt", "RedGroundfort", "AntiqueWhiteTravelstad"]
SET j.key = true
```

* Añade `key: true` a esos tres trabajos (útil para resaltarlos o filtrarlos después).

---

## Limpieza, terminales y “ruta crítica” hacia un nodo

```cypher
MATCH (n) DETACH DELETE n;
```

* Borra todo el grafo (nodos y relaciones) de forma segura.

```cypher
MATCH (j:Job)
WHERE NOT (:Job)-[:DEPENDS_ON]->(j)
RETURN j AS FinalJobs;
```
