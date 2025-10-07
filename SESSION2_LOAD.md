
## Carga de datos e índice

```cypher
LOAD CSV WITH HEADERS FROM '.../dependency_nodes.csv' AS row
CREATE (:Job {name: row.name, duration_avg: toFloat(row.duration_avg), duration_std: toFloat(row.duration_std)});

LOAD CSV WITH HEADERS FROM '.../dependency_edges.csv' AS row
MATCH (src:Job {name: row.source})
MATCH (dst:Job {name: row.target})
CREATE (src)-[:DEPENDS_ON]->(dst);

CREATE INDEX job_name_index FOR (j:Job) ON (j.name);
```

* Crea nodos `:Job` a partir de un CSV, con propiedades `name`, `duration_avg` y `duration_std`.
* Crea relaciones `(:Job)-[:DEPENDS_ON]->(:Job)` desde el trabajo **que depende** (`src`) hacia el **requisito previo** (`dst`).
* Crea un índice en `:Job(name)` para acelerar búsquedas por nombre.

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

* Devuelve los **trabajos terminales** (sin **entrantes** `DEPENDS_ON`), es decir, de los que **nadie depende**.

```cypher
MATCH p = (root:Job)<-[r:DEPENDS_ON*]-(j:Job {name:"TealPagefurt"})
WITH p, reduce(total=0.0, rel IN relationships(p) | total + rel.average_duration) AS totalDuration
ORDER BY totalDuration DESC
LIMIT 3
RETURN p AS CriticalPath, totalDuration;
```

* Recorre todas las rutas de **predecesores** que acaban en `TealPagefurt` (el patrón va “a contraflujo”: `TealPagefurt` depende de otros).
* Calcula `totalDuration` sumando `rel.average_duration` a lo largo de cada ruta y devuelve las 3 rutas con mayor duración (una aproximación a rutas críticas **hacia** ese nodo).

  * Nota: para que la suma funcione, las relaciones deben tener la propiedad `average_duration`. Si no se cargó antes, esta suma dará `null`/0.

---

## Marcar trabajos clave

```cypher
MATCH (j: Job)
WHERE j.name in ["ChocolatePartfurt", "RedGroundfort", "AntiqueWhiteTravelstad"]
SET j.key = true
```

* Añade `key: true` a esos tres trabajos (útil para resaltarlos o filtrarlos después).
