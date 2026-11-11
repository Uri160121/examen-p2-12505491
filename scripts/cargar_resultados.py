#!/usr/bin/env python3
import os, sys
import psycopg2

ruta = sys.argv[1] if len(sys.argv) > 1 else "/data/output/resultado/part-00000"

conn = psycopg2.connect(
    host="db",
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
with conn, conn.cursor() as cur:
    cur.execute("""CREATE TABLE IF NOT EXISTS resultados (
        clave TEXT PRIMARY KEY, valor DOUBLE PRECISION NOT NULL)""")
    n = 0
    for linea in open(ruta):
        producto, ingreso = linea.rstrip("\n").split("\t")
        cur.execute(
            """INSERT INTO resultados (clave, valor) VALUES (%s, %s)
               ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor""",
            (producto, float(ingreso)),
        )
        n += 1
conn.close()
print(f"{n} registros cargados")
