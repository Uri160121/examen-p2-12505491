# Examen P2 - Pipeline de datos contenerizado (125054916)

**Matrícula:** 125054916
**Pregunta asignada (dígito 6):** Top 10 productos por ingreso total en el año.

## Cómo reproducir
1. `python3 generar_dataset.py 125054916` (el CSV queda fuera del repo, en `~/datos`).
2. `cp .env.example .env` y editar la contraseña y `DATASET_PATH` (ruta absoluta).
3. `docker compose up --build -d`
4. Correr el job de Hadoop Streaming con 1 reducer (`mapper.py` y `reducer.py` en `mapreduce/`).
5. `docker compose exec api python /scripts/cargar_resultados.py`
6. `curl localhost:5000/resultados`

## Tiempos medidos
- Hadoop Streaming: 11.880 s
- Secuencial: 3.273 s
- Resultados coinciden: sí (diff vacío)

El script secuencial tardó 3.273 s y Hadoop Streaming 11.880 s, es decir, el secuencial fue unas 3.6 veces más rápido. Con un archivo de ~400 MB que cabe en una sola máquina, Hadoop en modo standalone no tiene paralelismo real: corre todo en una sola JVM local y además paga costos fijos que el script no tiene, como el arranque de la JVM, el lanzamiento de procesos Python para el mapper y el reducer, y el shuffle/sort intermedio escrito a disco. El script secuencial recorre el archivo una sola vez y agrega en memoria, sin esa sobrecarga. MapReduce solo conviene cuando los datos exceden una máquina y hay varios nodos que reparten los mapas en paralelo.

## Evidencias
Carpeta `evidencias/`: versión de Hadoop, SSH sin contraseña (localhost y api -> hadoop), salida del job, comparativa de tiempos, carga a la BD, respuestas de la API y persistencia tras `down`/`up`.

## Teoría (Parte E)
1. **Modos de Hadoop:** standalone corre en una sola JVM sin demonios y sobre el sistema de archivos local (sin HDFS). Pseudo-distribuido levanta todos los demonios en una máquina simulando un clúster y ahí ya se usa HDFS. Totalmente distribuido reparte los demonios en varias máquinas, también con HDFS.
2. **Volumen vs COPY:** 400 MB inflarían la imagen y cada build, push o pull los arrastraría. Además el dato cambia independiente del código (cada alumno tiene el suyo) y no debe quedar dentro de una imagen que se comparte; con `:ro` también se protege el original.
3. **`down` vs `down -v`:** `down` borra contenedores y red, pero el volumen nombrado se conserva y los datos siguen. `down -v` también borra los volúmenes, así que se pierde la base de datos.
4. **MapReduce no siempre es más rápido:** 400 MB caben en una máquina y el costo fijo (JVM, orquestación, shuffle, disco intermedio) supera el beneficio. Conviene con datos que exceden una sola máquina, varios nodos para paralelizar y trabajo batch sobre decenas o cientos de GB.
5. **CMD vs ENTRYPOINT y COPY vs ADD:** CMD es el comando por defecto y se sobreescribe fácil con `docker run imagen otro-comando`; ENTRYPOINT fija el ejecutable y lo que se pasa se agrega como argumentos. COPY solo copia archivos locales; ADD además descomprime tar locales y acepta URLs, por eso se prefiere COPY.

## Comandos del job y la comparativa
Job de Hadoop Streaming (1 reducer):

    docker compose exec -T -u hadoopuser -w /home/hadoopuser/mapreduce hadoop bash -c '
      rm -rf /data/output/resultado
      time hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
        -D mapreduce.job.reduces=1 \
        -files mapper.py,reducer.py \
        -input /data/input/dataset.csv \
        -output /data/output/resultado \
        -mapper "python3 mapper.py" \
        -reducer "python3 reducer.py"
    '

Script secuencial y verificación:

    docker compose exec -T -u hadoopuser hadoop bash -c 'time python3 /home/hadoopuser/mapreduce/secuencial.py > /tmp/secuencial.txt'
    docker compose exec -T hadoop diff /tmp/secuencial.txt /data/output/resultado/part-00000 && echo COINCIDEN

Persistencia: `docker compose down && docker compose up -d` y luego `curl localhost:5000/resultados` (los datos siguen porque `pgdata` es un volumen nombrado).
