#!/usr/bin/env python3
import sys

ruta = sys.argv[1] if len(sys.argv) > 1 else "/data/input/dataset.csv"
totales = {}
with open(ruta) as f:
    for linea in f:
        campos = linea.rstrip("\n").split(",")
        if len(campos) != 8:
            continue
        try:
            cantidad = int(campos[5])
            centavos = round(float(campos[6]) * 100)
        except ValueError:
            continue
        totales[campos[4]] = totales.get(campos[4], 0) + cantidad * centavos

top = sorted(totales.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
for producto, c in top:
    print(f"{producto}\t{c // 100}.{c % 100:02d}")
