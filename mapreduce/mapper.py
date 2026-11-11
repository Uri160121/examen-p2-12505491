#!/usr/bin/env python3
import sys

for linea in sys.stdin:
    campos = linea.rstrip("\n").split(",")
    if len(campos) != 8:
        continue
    try:
        cantidad = int(campos[5])
        centavos = round(float(campos[6]) * 100)
    except ValueError:
        continue
    print(f"{campos[4]}\t{cantidad * centavos}")
