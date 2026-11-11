#!/usr/bin/env python3
import sys

totales = {}
for linea in sys.stdin:
    try:
        producto, valor = linea.rstrip("\n").split("\t")
        totales[producto] = totales.get(producto, 0) + int(valor)
    except ValueError:
        continue

top = sorted(totales.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
for producto, c in top:
    print(f"{producto}\t{c // 100}.{c % 100:02d}")
