
# 📘 Job Dependency Graph in Neo4j

## **0. Intro (5 min)**

Comentar el PPT

Entrar a Neo4j.

Guia básica de la interfaz. Ejecutar una query. doble click. atributos

## Queries

### 🧩 Conceptos iniciales

Un **grafo** está compuesto por:

* **Nodos** (`( )`): entidades (en este caso, *Jobs*)
* **Relaciones** (`-[ ]->`): conexiones entre nodos (en este caso, *DEPENDS_ON*)

Ejemplo:
`(A)-[:DEPENDS_ON]->(B)` significa que **A depende de B**.

Cláusulas. Explicar (slides)

* MATCH
  * Construir caminos
  * Filtrar en el match
* WHERE
  * Atributos
* RETURN
* WITH
  * La manera de hacer subqueries
  * Distinct

---

## **1. Explorando dependencias**

* Devolver un listado de todos los jobs

```cypher
MATCH (j:Job) RETURN j;
```

* Dependencias directas

```cypher
MATCH (j:Job {name:"AquaEvershire"})-[d:DEPENDS_ON]->(dep)
RETURN j,d,dep;
```

* Cadena completa, usando **caminos variables** (explicar)

Explicar asterisco *

```cypher
MATCH path=(j:Job {name:"AquaEvershire"})-[:DEPENDS_ON*]->(dep)
RETURN path;
```

Ejercicios.

* Que busquen qué jobs dependen de este en concreto (1 salto) VioletEntireborough

```cypher
MATCH path=(j:Job {name: "VioletEntireborough"})<-[:DEPENDS_ON]-(dep)
RETURN path;
```

* ¿Cómo podemos limitar el número de saltos? (Para evitar entrar en ciclos, que vaya mas rapido, etc)

p.ej

```cypher
MATCH path=(j:Job {name:"AquaEvershire"})-[:DEPENDS_ON*2]-(dep)
  RETURN path;
```

**Reto adicional:**
Queremos buscar caminos de exactamente 10 dependencias.
¿Qué jobs forman una cadena 10 niveles de dependencia?

```cypher
MATCH path=(j:Job)-[:DEPENDS_ON*10]->(dep)
RETURN DISTINCT j;
```

---

## **3. Identificando trabajos iniciales y finales**

### 🟢 Jobs sin dependencias (pueden arrancar primero)

```cypher
MATCH (j:Job)
WHERE NOT (j)-[:DEPENDS_ON]->()
RETURN j;
```

### 🔢 Contar cuántos jobs iniciales hay

```cypher
MATCH (j:Job)
WHERE NOT (j)-[:DEPENDS_ON]->()
RETURN count(1) AS c;
```

### 🔴 Jobs finales (nadie depende de ellos)

```cypher
MATCH (j:Job)
WHERE NOT ()-[:DEPENDS_ON]->(j)
RETURN j;
```

### 🔢 Cuántos jobs finales existen

```cypher
MATCH (j:Job)
WHERE NOT ()-[:DEPENDS_ON]->(j)
RETURN count(1) AS c;
```

### 📈 Orden aproximado por número de dependencias

```cypher
MATCH (j:Job)
OPTIONAL MATCH (j)-[:DEPENDS_ON]->(dep)
WITH j, count(dep) AS deps
ORDER BY deps DESC
RETURN j.name, deps;
```

### 🔍 Dependencias totales (directas + indirectas)

```cypher
MATCH (j:Job)
OPTIONAL MATCH (j)-[:DEPENDS_ON*]->(dep)
WITH j, count(DISTINCT dep) AS deps
ORDER BY deps DESC
RETURN j.name, deps;
```

---

## **4. Camino crítico con Cypher**

El **camino crítico** es la secuencia de tareas que determina la duración total del proyecto.

```cypher
MATCH path=(start:Job {name: "SandyBrownSeatland"})-[:DEPENDS_ON*]->(end:Job)
WITH path,
     reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
ORDER BY duration_avg DESC LIMIT 1
RETURN [n IN nodes(path) | n.name] AS criticalPath, duration_avg;
```

🧠 **Concepto clave:**
`reduce()` acumula valores sobre los nodos del camino (aquí, la duración promedio).

💡 **Ejercicio:**
Modificar la duración de un *Job* (`SET j.duration_avg = 999`) y observa cómo cambia el camino crítico. ¿Qué pasa cuando vuelven a ejecutar la consulta?

```cypher
MATCH (j:Job) 
WHERE j.name = "DarkGrayNeedport"
SET j.duration_avg = 999; // 39
```

---

## **5. Detectando ciclos**

Los ciclos son problemáticos: impiden determinar un orden de ejecución.

```cypher
MATCH path=(j:Job)-[:DEPENDS_ON*]->(j)
RETURN path LIMIT 1;
```

👉 Crear manualmente un ciclo:

```cypher
MATCH (a:Job {name: "OrangeRedSufferborough"}), (b:Job {name: "SandyBrownSeatland"})
CREATE (a)-[:DEPENDS_ON]->(b);
```

👉 Eliminar el ciclo:

```cypher
MATCH (a:Job {name: "OrangeRedSufferborough"})-[r:DEPENDS_ON]->(b:Job {name: "SandyBrownSeatland"})
DELETE r;
```

---

## **6. Desafíos prácticos (10 min)**

1. **¿Qué jobs pueden empezar ya?**

```cypher
MATCH (j:Job)
WHERE NOT ()-[:DEPENDS_ON]->(j)
RETURN j;
```

2. **Duración total del proyecto (si paralelizamos todo):**

```cypher
MATCH path=(start:Job)-[:DEPENDS_ON*]->(end:Job)
WITH path,
    reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
ORDER BY duration_avg DESC LIMIT 1
RETURN path AS criticalPath, duration_avg;
```

3. **Jobs con mayor duración total acumulada (top 5):**

```cypher
MATCH path=(j:Job)-[:DEPENDS_ON*]->(dep)
WITH j, sum(dep.duration_avg) AS total
ORDER BY total DESC LIMIT 5
RETURN j.name, total;
```

4. **Extra (conceptual):**
Buscar el *shortest path* tiene poco sentido aquí, pero imagina que las relaciones representan distancias o tiempos de viaje.

```cypher
MATCH p = SHORTEST 1 (a:Job)-[]-+(b:Job)
WHERE a.name = "WhiteSmokeYourselfburgh" AND b.name = "LightCoralDeepport"
RETURN p, length(p) AS result
```

```cypher
MATCH p = SHORTEST 1 (a:Job)-[]->+(b:Job)
WHERE a.name = "WhiteSmokeYourselfburgh" AND b.name = "LightCoralDeepport"
RETURN p, length(p) AS result
```

* shortest path con duraciones

```cypher
MATCH path=(start:Job )-[:DEPENDS_ON*]->(end:Job)
WHERE start.name = "WhiteSmokeYourselfburgh" AND end.name = "LightCoralDeepport"
WITH path,
        reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
ORDER BY duration_avg ASC LIMIT 1
RETURN path, duration_avg, length(path) AS result
```

## **7. Key Jobs y tiempos de ejecución**

## Borrar tiempos

```cypher
MATCH (a :Job)
REMOVE a.earliest_finish, a.earliest_start, a.latest_finish, a.latest_start, a.slack_time, a.ES, a.EF
```

### 🔑 Identificar jobs críticos del cliente

Los key jobs son unos jobs de gran importancia para el cliente. Los hemos marcado con un atributo.

```cypher
MATCH (job:Job)
WHERE job.key
RETURN job
```

### 🔗 Ver sus dependencias directas

* Preguntar: ¿qué dependencias (directas) tienen estos jobs?

```cypher
MATCH path=(job:Job)-[]->(dep:Job)
WHERE job.key
RETURN path
```

### 🕒 Cálculo de tiempos (forward y backward pass)

* Calculamos información de tiempos de ejecución
* Analizar un poco las siguientes consultas

#### Forward pass

```cypher
MATCH (j:Job)
WITH j
MATCH path=(root:Job)<-[:DEPENDS_ON*0..]-(j)
WHERE NOT (root)-[:DEPENDS_ON]->()
WITH j, max(reduce(t=0, n IN nodes(path)[0..-1] | t + coalesce(n.duration_avg,0))) AS earliest_start
SET j.earliest_start = earliest_start,
    j.earliest_finish = earliest_start + coalesce(j.duration_avg,0)
RETURN j.name, j.earliest_start, j.earliest_finish
ORDER BY j.earliest_start;
```

#### Backward pass

```cypher
MATCH (j:Job)
WITH j
MATCH path=(j)<-[:DEPENDS_ON*0..]-(end:Job)
WHERE NOT ()-[:DEPENDS_ON]->(end)
WITH j, min(end.earliest_finish - reduce(t=0, n IN tail(nodes(path)) | t + coalesce(n.duration_avg,0))) AS latest_finish
SET j.latest_finish = latest_finish,
    j.latest_start  = latest_finish - coalesce(j.duration_avg,0)
RETURN j.name, j.latest_start, j.latest_finish
ORDER BY j.latest_start;
```

#### Slack Time

```cypher
MATCH (j:Job)
RETURN j.name AS job_name, round(j.latest_start - j.earliest_start, 2) AS slack
ORDER BY slack;
```

👉 Jobs con `slack = 0` son **críticos**.

### Cuál es el key job (con ejecución completa) más lenta?

```cypher
MATCH path=(start:Job )-[:DEPENDS_ON*]->(end:Job)
WHERE start.key = TRUE
WITH path,
    reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
ORDER BY duration_avg DESC LIMIT 1
RETURN path AS criticalPath, duration_avg;
```

### Tenemos un problema con un job, a qué criticos afecta?

```cypher
MATCH path=(start:Job )-[:DEPENDS_ON*]->(affected:Job)
WHERE start.key = TRUE and affected.name = "MediumVioletRedOfffort"
RETURN path
```

## Calcular diagrama de ejecución para todos los jobs (+ slack)

Ejecutar lo siguiente para calcular *earliest/latest*, *start/finish*:

```cypher

// forward pass
MATCH (j:Job)
WITH j
MATCH path=(root:Job)<-[:DEPENDS_ON*0..]-(j)
WHERE NOT (root)-[:DEPENDS_ON]->() 
WITH j,
     max( reduce(t=0, n IN nodes(path)[0..-1] | t + coalesce(n.duration_avg,0)) ) AS earliest_start
SET j.earliest_start = earliest_start,
    j.earliest_finish = earliest_start + coalesce(j.duration_avg,0)
RETURN j.name, j.earliest_start, j.earliest_finish
ORDER BY j.earliest_start;

// backward pass
MATCH (j:Job)
WITH j
MATCH path=(j)<-[:DEPENDS_ON*0..]-(end:Job)
WHERE NOT ()-[:DEPENDS_ON]->(end) // end job
WITH j,
     min( end.earliest_finish - reduce(t=0, n IN tail(nodes(path)) | t + coalesce(n.duration_avg,0)) ) AS latest_finish
SET j.latest_finish = latest_finish,
    j.latest_start  = latest_finish - coalesce(j.duration_avg,0)
RETURN j.name, j.latest_start, j.latest_finish
ORDER BY j.latest_start;
```

Buscar paralelismo en tramos de 5 minutos.

```cypher
with range(0, 1700, 5) as moments
unwind moments as mstart
with mstart, mstart+5 as mend
match (j:Job)
where j.earliest_start <= mend and j.earliest_finish >= mstart
return mstart, mend, count(distinct j) as num_jobs_in_execution
```

### Calcular el slack time para cualquier job

```cypher
match (j:Job)
return j.name as job_name, round(j.latest_start - j.earliest_start, 2) as slack
//order by slack desc
```

### Número de jobs sin slack (criticals)

```cypher
match (j:Job)
with j.name as job_name, round(j.latest_start - j.earliest_start, 2) as slack
where slack = 0
return count(1) as critical_jobs
```

---

## **6. Wrap-Up (5 min)**

✅ **Resumen:**

* Exploramos dependencias con `MATCH` y caminos variables.
* Identificamos jobs iniciales/finales.
* Calculamos caminos críticos y *slack time*.
* Detectamos ciclos problemáticos.
* Vimos cómo analizar tiempos y paralelismo.

🎯 **Analogías reales:**

* Flujos ETL
* Procesos de fabricación o de negocio

💬 **Para seguir practicando:**

* Añadir nuevos atributos (`owner`, `priority`)
* Probar la extensión **Graph Data Science (GDS)** para calcular métricas como centralidad o pagerank
