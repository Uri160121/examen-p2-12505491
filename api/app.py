import os, time
from contextlib import contextmanager
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

def conn():
    return psycopg2.connect(
        host="db",
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

@contextmanager
def cursor():
    c = conn()
    try:
        with c, c.cursor() as cur:
            yield cur
    finally:
        c.close()

def init_db():
    for _ in range(20):
        try:
            with cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS resultados (
                    clave TEXT PRIMARY KEY, valor DOUBLE PRECISION NOT NULL)""")
            return
        except psycopg2.OperationalError:
            time.sleep(2)

@app.get("/resultados")
def listar():
    with cursor() as cur:
        cur.execute("SELECT clave, valor FROM resultados ORDER BY valor DESC")
        return jsonify([{"clave": k, "valor": v} for k, v in cur.fetchall()])

@app.get("/resultados/<clave>")
def uno(clave):
    with cursor() as cur:
        cur.execute("SELECT clave, valor FROM resultados WHERE clave = %s", (clave,))
        r = cur.fetchone()
    if not r:
        return jsonify(error="no existe"), 404
    return jsonify({"clave": r[0], "valor": r[1]})

@app.post("/resultados")
def crear():
    d = request.get_json(silent=True) or {}
    if "clave" not in d or "valor" not in d:
        return jsonify(error="se requieren clave y valor"), 400
    try:
        with cursor() as cur:
            cur.execute("INSERT INTO resultados (clave, valor) VALUES (%s, %s)",
                        (d["clave"], d["valor"]))
    except psycopg2.errors.UniqueViolation:
        return jsonify(error="la clave ya existe"), 409
    return jsonify(d), 201

@app.put("/resultados/<clave>")
def actualizar(clave):
    d = request.get_json(silent=True) or {}
    if "valor" not in d:
        return jsonify(error="se requiere valor"), 400
    with cursor() as cur:
        cur.execute("UPDATE resultados SET valor = %s WHERE clave = %s", (d["valor"], clave))
        if cur.rowcount == 0:
            return jsonify(error="no existe"), 404
    return jsonify({"clave": clave, "valor": d["valor"]})

@app.delete("/resultados/<clave>")
def borrar(clave):
    with cursor() as cur:
        cur.execute("DELETE FROM resultados WHERE clave = %s", (clave,))
    return "", 204

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
