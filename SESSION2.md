# Sesión práctica de 1 hora: Grafo de dependencias de trabajos en Neo4j

## Agenda

### 0. Introducción (5 min)

* Presentar el conjunto de datos de trabajos y dependencias que vamos a cargar en Neo4j.
* Explicar el objetivo de la sesión: practicar consultas en **Cypher** para analizar ordenaciones, rutas críticas y problemas típicos de planificación.

---

### 1. Explorar las dependencias (10 min)

* Recordar cómo está estructurado el grafo: tenemos nodos `Job` y relaciones `DEPENDS_ON` que van desde un trabajo hacia aquellos que deben ejecutarse antes.

* Listar todos los trabajos disponibles para verificar que la carga de datos se hizo correctamente:

  ```cypher
  MATCH (j:Job)
  RETURN j;
  ```

  > Devuelve cada nodo `Job` con todas sus propiedades.

* Consultar las dependencias directas de un trabajo específico (por ejemplo, `AquaEvershire`):

  ```cypher
  MATCH (j:Job {name: "AquaEvershire"})-[:DEPENDS_ON]->(dep)
  RETURN j, dep;
  ```

  > Muestra qué trabajos deben completarse justo antes de `AquaEvershire`.

* Revisar toda la cadena de dependencias hacia atrás (predecesores):

  ```cypher
  MATCH path=(j:Job {name: "AquaEvershire"})-[:DEPENDS_ON*]->(dep)
  RETURN path;
  ```

  > Devuelve todas las rutas en las que `AquaEvershire` depende indirectamente de otros trabajos.

* **Ejercicio guiado:** pedirles que encuentren qué trabajos dependen de `AquaEvershire` (hacia adelante) y que limiten la profundidad de la ruta con `*1..3` para comparar los resultados.

---

### 2. Identificar trabajos iniciales y orden aproximado (12 min)

* Localizar los trabajos sin dependencias de entrada, que son candidatos para ejecutarse primero:

  ```cypher
  MATCH (j:Job)
  WHERE NOT (j)-[:DEPENDS_ON]->()
  RETURN j.name;
  ```

  > Devuelve los trabajos raíz: aquellos que no dependen de ningún otro.

* Contar cuántos trabajos podemos lanzar desde el inicio:

  ```cypher
  MATCH (j:Job)
  WHERE NOT (j)-[:DEPENDS_ON]->()
  RETURN count(*) AS trabajos_iniciales;
  ```

  > Nos da una idea del paralelismo potencial en la primera ronda.

* Encontrar los trabajos finales (de los que nadie depende) para entender cuáles son los posibles puntos de entrega:

  ```cypher
  MATCH (j:Job)
  WHERE NOT ()-[:DEPENDS_ON]->(j)
  RETURN j.name;
  ```

* Obtener un orden aproximado ordenando por número de dependencias directas:

  ```cypher
  MATCH (j:Job)
  OPTIONAL MATCH (j)-[:DEPENDS_ON]->(dep)
  WITH j, count(dep) AS dependencias_directas
  RETURN j.name, dependencias_directas
  ORDER BY dependencias_directas DESC;
  ```

---

### 3. Calcular la ruta crítica usando solo Cypher (12 min)

* Definir qué es la **ruta crítica**: la secuencia más larga (en duración) desde un trabajo inicial hasta uno final.

* Usar un punto de partida representativo (por ejemplo, `SandyBrownSeatland`) para calcular la ruta más costosa:

  ```cypher
  MATCH path=(start:Job {name: "SandyBrownSeatland"})-[:DEPENDS_ON*]->(end:Job)
  WITH path,
       reduce(total = 0, n IN nodes(path) | total + coalesce(n.duration_avg, 0)) AS duracion
  RETURN [n IN nodes(path) | n.name] AS trabajos, duracion
  ORDER BY duracion DESC
  LIMIT 1;
  ```

  > Suma la duración promedio guardada en cada nodo de la ruta y devuelve la secuencia más larga encontrada.

* **Variación para practicar:** cambiar la duración de un trabajo y volver a ejecutar la consulta para ver cómo cambia la ruta crítica.

---

### 4. Detectar ciclos en el grafo (6 min)

* Explicar por qué un ciclo nos impide planificar (un trabajo terminaría dependiendo de sí mismo) y cómo localizarlo:

  ```cypher
  MATCH path=(j:Job)-[:DEPENDS_ON*]->(j)
  RETURN path
  LIMIT 1;
  ```

  > Si esta consulta devuelve resultados, hay al menos un ciclo problemático.

* **Ejercicio guiado:** crear una dependencia circular de forma controlada (por ejemplo, de `OrangeRedSufferborough` hacia `SandyBrownSeatland`), ejecutar de nuevo la detección para confirmarla y, finalmente, eliminar la relación para dejar el grafo consistente.

---

### 5. Retos prácticos en grupos (10 min)

1. **Trabajos prioritarios:** listar todos los trabajos que se pueden lanzar de inmediato y validar el resultado con `count(*)`.

2. **Duración total del proyecto:** obtener el tiempo del camino crítico más largo (pueden reutilizar la consulta de la sección 3 pero sin fijar el nodo inicial).

   ```cypher
   MATCH path=(start:Job)-[:DEPENDS_ON*]->(end:Job)
   WITH path,
        reduce(total = 0, n IN nodes(path) | total + coalesce(n.duration_avg, 0)) AS duracion
   RETURN [n IN nodes(path) | n.name] AS trabajos, duracion
   ORDER BY duracion DESC
   LIMIT 1;
   ```

3. **Impacto de un fallo:** encontrar todas las rutas críticas que pasan por `MediumVioletRedOfffort`.

   ```cypher
   MATCH path=(inicio:Job)-[:DEPENDS_ON*]->(fin:Job)
   WHERE inicio.critical = TRUE AND "MediumVioletRedOfffort" IN [n IN nodes(path) | n.name]
   RETURN path;
   ```

* **Extensión opcional:** calcular tiempos tempranos y tardíos usando consultas de *forward pass* y *backward pass* si el grupo quiere profundizar en márgenes y holguras.

---

### 6. Cierre (5 min)

* Repasar las ideas clave: detección de dependencias, identificación de trabajos iniciales y finales, cálculo de rutas críticas y búsqueda de ciclos.
* Conectar lo aprendido con procesos del mundo real (pipelines de CI/CD, cadenas de suministro, ETL, etc.).
* Entregar como material de apoyo el dataset que usamos y una hoja resumen con las consultas en **Cypher** que practicamos.
