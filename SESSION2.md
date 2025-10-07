
# 📘 1-Hour Practical Class: Job Dependency Graph in Neo4j

## ⏱️ Agenda

### **0. Intro (5 min)**

---

### **1. Exploring Dependencies (10 min)**

* List all jobs:

  ```cypher
  MATCH (j:Job) RETURN j;
  ```

* Direct dependencies:

  ```cypher
  MATCH (j:Job {name:"AquaEvershire"})-[d:DEPENDS_ON]->(dep) RETURN j,d,dep;
  ```

* Full chain:

  ```cypher
  MATCH path=(j:Job {name:"AquaEvershire"})-[:DEPENDS_ON*]->(dep)
  RETURN path;
  ```

```cypher
MATCH path=(j:Job {name:"AquaEvershire"})-[:DEPENDS_ON*2]-(dep)
  RETURN path;
```

Ejercicios.

* Que busquen qué jobs dependen de este en concreto
* Que limiten el número

---

### **2. Finding Start Jobs & Execution Order (15 min)**

* Jobs with **no dependencies** (can run first):

  ```cypher
  MATCH (j:Job) WHERE NOT (j)-[:DEPENDS_ON]->() RETURN j;
  ```

¿Cuántos jobs no tienen dependencias?

  ```cypher
  MATCH (j:Job) WHERE NOT (j)-[:DEPENDS_ON]->() RETURN count(1) as c;
  ```

* Jobs with **no dependents** (end jobs):

  ```cypher
  MATCH (j:Job) WHERE NOT ()-[:DEPENDS_ON]->(j) RETURN j;
  ```

¿Cuántos jobs no tienen dependientes (jobs "finales")?

  ```cypher
  MATCH (j:Job) WHERE NOT ()-[:DEPENDS_ON]->(j) RETURN count(1) as c;
  ```

* Approximate ordering by dependency count (dependencias directas):

  ```cypher
  MATCH (j:Job)
  OPTIONAL MATCH (j)-[:DEPENDS_ON]->(dep)
  WITH j, count(dep) AS deps
  ORDER BY deps desc
  RETURN j.name, deps;
  ```

👉 Ask participants: *Does this look like a valid order? Why/why not?*
(Emphasize that Cypher isn’t a scheduler but can help explore.)

Cuantas dependencias en total

```cypher
MATCH (j:Job)
  OPTIONAL MATCH (j)-[:DEPENDS_ON*]->(dep)
  WITH j, count(distinct dep) AS deps
  ORDER BY deps desc
  RETURN j.name, deps;
```

---

### **3. Critical Path with Pure Cypher (15 min)**

* Longest dependency chain:

  ```cypher
  MATCH path=(start:Job {name: "SandyBrownSeatland"})-[:DEPENDS_ON*]->(end:Job)
  WITH path,
       reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
  ORDER BY duration_avg DESC LIMIT 1
  RETURN path AS criticalPath, duration_avg;

  RETURN [n IN nodes(path) | n.name] AS criticalPath, duration_avg;
  ```

👉 Variation: run again after changing one job’s duration. How does the path change?

---

### **4. Detecting Cycles (5 min)**

* Show why cycles = bad for scheduling:

```cypher
MATCH path=(j:Job)-[:DEPENDS_ON*]->(j)
RETURN path LIMIT 1
```

👉 Insert a circular dependency (`OrangeRedSufferborough -> SandyBrownSeatland`) and detect it.

```cypher
MATCH (a:Job {name: "OrangeRedSufferborough"}), (b:Job {name: "SandyBrownSeatland"})
CREATE (a)-[:DEPENDS_ON]->(b)
```

redo the cycle cypher

```cypher
MATCH (a:Job {name: "OrangeRedSufferborough"})-[r:DEPENDS_ON]->(b:Job {name: "SandyBrownSeatland"})
DELETE r
```

---

### **5. Hands-On Challenges (10 min)**

Give 2–3 small tasks for practice:

1. Which jobs can start right away?
2. Cuánto tardamos en que se ejecute todo, si podemos paralelizar indefinidamente?
(max del camino crítico)

 ```cypher

  MATCH path=(start:Job )-[:DEPENDS_ON*]->(end:Job)
    WITH path,
        reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
    ORDER BY duration_avg DESC LIMIT 1
    RETURN path AS criticalPath, duration_avg;

  ```

JOBS criticos

cual es el job crítico (con ejecución completa) más lento?

MATCH path=(start:Job )-[:DEPENDS_ON*]->(end:Job)
WHERE start.key = TRUE
WITH path,
    reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
ORDER BY duration_avg DESC LIMIT 1
RETURN path AS criticalPath, duration_avg;

Tenemos un problema con un job, a qué criticos afecta?

```cypher
MATCH path=(start:Job )-[:DEPENDS_ON*]->(affected:Job)
WHERE start.key = TRUE and affected.name = "MediumVioletRedOfffort"
RETURN path
```

3. Add a new job `E` depending on `C`, and recompute the critical path.

* Shortest (pensar per que serveix aqui?)

```cypher
MATCH p = SHORTEST 1 (wos:Job)-[]-+(bmv:Job)
WHERE wos.name = "WhiteSmokeYourselfburgh" AND bmv.name = "LightCoralDeepport"
RETURN p, length(p) AS result
```

MATCH p = SHORTEST 1 (wos:Job)-[]->+(bmv:Job)
WHERE wos.name = "WhiteSmokeYourselfburgh" AND bmv.name = "LightCoralDeepport"
RETURN p, length(p) AS result

* shortest path con duraciones

```cypher
MATCH path=(start:Job )-[:DEPENDS_ON*]->(end:Job)
WHERE start.name = "WhiteSmokeYourselfburgh" AND end.name = "LightCoralDeepport"
WITH path,
        reduce(total=0, n IN nodes(path) | total + n.duration_avg) AS duration_avg
ORDER BY duration_avg ASC LIMIT 1
RETURN path, duration_avg, length(path) AS result
```

<!-- borrar tiempos -->
```cypher
MATCH (a :Job)
REMOVE a.earliest_finish, a.earliest_start, a.latest_finish, a.latest_start, a.slack_time
```

```cypher
// forward pass (correct direction)
MATCH (j:Job)
WITH j
// all paths from roots (jobs with no outgoing DEPENDS_ON) to this job
MATCH path=(root:Job)<-[:DEPENDS_ON*0..]-(j)
WHERE NOT (root)-[:DEPENDS_ON]->() 
WITH j,
     max( reduce(t=0, n IN nodes(path)[0..-1] | t + coalesce(n.duration_avg,0)) ) AS earliest_start
SET j.earliest_start = earliest_start,
    j.earliest_finish = earliest_start + coalesce(j.duration_avg,0)
RETURN j.name, j.earliest_start, j.earliest_finish
ORDER BY j.earliest_start


// get total project duration
MATCH (end:Job)
WHERE end.key = TRUE // no one depends on it
RETURN max(end.earliest_finish) AS project_duration


// backward pass (correct direction)

MATCH (j:Job)
WITH j
// all paths from j forward to any critical job
MATCH path=(j)<-[:DEPENDS_ON*0..]-(end:Job)
WHERE end.key = TRUE // end job
WITH j,
     min( end.earliest_finish - reduce(t=0, n IN tail(nodes(path)) | t + coalesce(n.duration_avg,0)) ) AS latest_finish
SET j.latest_finish = latest_finish,
    j.latest_start  = latest_finish - coalesce(j.duration_avg,0)
RETURN j.name, j.latest_start, j.latest_finish
ORDER BY j.latest_start



```

job afectado = MediumVioletRedOfffort

---

### **6. Wrap-Up (5 min)**

* Recap: querying dependencies, start jobs, critical path, cycles.
* Highlight real-world analogies: build pipelines, ETL workflows, manufacturing tasks.
* Encourage participants to experiment further with Cypher.

---

✅ Deliverables: Dataset + “cheat sheet” of Cypher queries for them to keep.

---

Would you like me to **prepare a ready-to-use worksheet** (like a PDF or Markdown with exercises + solutions) so participants can follow along step by step?
