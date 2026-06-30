#!/usr/bin/env python3
"""Seguimiento del estado de los reclamos de RECHAZADOS (genérico, plugin cod-ops).
Mantiene reclamos_estado.csv: una fila por pedido rechazado con su estado ante
el proveedor. Siembra nuevos como 'pendiente' y PRESERVA lo ya marcado. El
operador edita el CSV (o se lo dice a Claude) cuando el proveedor responde.

CSV: ID, estado(pendiente|aprobado|rechazado), fecha_respuesta, valor_reconocido, nota
Uso: python3 seguimiento_reclamos.py [ruta/al/tienda.config.json]
"""
import openpyxl, os, sys, json, csv
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "tienda.config.json")
CFG = json.load(open(CFG_PATH, encoding="utf-8"))
COL = CFG["dropi_columnas"]; REPS = CFG["reportes"]["dropi"]
CSV = os.path.join(os.path.dirname(CFG_PATH), "reclamos_estado.csv")

seen = set(); rech = {}
for f in REPS:
    if not os.path.exists(f): continue
    ws = openpyxl.load_workbook(f, data_only=True).active
    rows = list(ws.iter_rows(values_only=True)); idx = {h: i for i, h in enumerate(rows[0])}
    def g(r, cn): return r[idx[cn]] if cn in idx else ""
    for r in rows[1:]:
        oid = g(r, COL["id"])
        if oid in seen: continue
        seen.add(oid)
        if str(g(r, COL["estatus"])) != "RECHAZADO": continue
        try: v = float(g(r, COL["total"]) or 0)
        except: v = 0
        rech[str(oid)] = v

prev = {}
if os.path.exists(CSV):
    for row in csv.DictReader(open(CSV)): prev[row["ID"]] = row
out = [prev.get(oid, {"ID": oid, "estado": "pendiente", "fecha_respuesta": "", "valor_reconocido": "", "nota": ""})
       for oid in rech]
with open(CSV, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["ID", "estado", "fecha_respuesta", "valor_reconocido", "nota"])
    w.writeheader(); w.writerows(out)

res = defaultdict(lambda: [0, 0.0]); recon = 0.0
for row in out:
    est = (row.get("estado") or "pendiente").strip().lower()
    res[est][0] += 1; res[est][1] += rech.get(row["ID"], 0)
    if est == "aprobado":
        try: recon += float(row.get("valor_reconocido") or 0)
        except: pass
print("=== SEGUIMIENTO DE RECLAMOS ===  ->", CSV)
for est in ("pendiente", "aprobado", "rechazado"):
    n, v = res.get(est, [0, 0.0]); print("  %-10s %3d  ($%s)" % (est, n, format(round(v), ",")))
print("Recuperado (aprobados): $%s" % format(round(recon), ","))
print("Actualizar: editar 'estado/fecha_respuesta/valor_reconocido/nota' en reclamos_estado.csv (o pedírselo a Claude).")
