#!/usr/bin/env python3
"""Snapshot diario del funnel de confirmación (Chatea Pro / UChat).
Captura el estado VIVO (los tags son efímeros), saca la lista accionable
del día (frescos en ventana 72h + falta dirección) y acumula una línea
en confirmacion_log.jsonl para construir la serie histórica desde hoy.

Uso: set -a && . ./.env && set +a && python3 snapshot_confirmacion.py [YYYY-MM-DD]
"""
import os, sys, json, time, urllib.request, urllib.error
from collections import defaultdict
from datetime import datetime

BASE = os.environ.get("CHATEAPRO_BASE", "https://chateapro.app/api")
KEY = os.environ.get("CHATEAPRO_API_KEY") or sys.exit("Falta CHATEAPRO_API_KEY")
HERE = os.path.dirname(os.path.abspath(__file__))
HOY = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
NOW = datetime.strptime(HOY + " 23:59:59", "%Y-%m-%d %H:%M:%S")

TAG_FUNNEL = "Embudo: Confirmaciones"
TAGS_CONFIRM = {"PEDIDO CONFIRMADO", "Ya confirmado✅"}
TAG_ADDR = "[Confirmaciones] Faltan datos en la dirección"

def get(path, retries=6):
    for i in range(retries):
        try:
            req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY,
                "Accept": "application/json", "User-Agent": "cod-ops/1.0"})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and i < retries - 1: time.sleep(3 + i * 2); continue
            raise

def fval(s, name):
    for f in s.get("user_fields", []):
        if f["name"] == name: return f.get("value")
    return None
def num(v):
    try: return float(str(v or 0).replace(".", "").replace(",", "."))
    except: return 0.0
def age_days(s):
    try: return (NOW - datetime.strptime(s, "%Y-%m-%d %H:%M:%S")).total_seconds() / 86400
    except: return None

print("Snapshot %s — jalando funnel..." % HOY, file=sys.stderr)
subs, page = [], 1
while True:
    d = get("/subscribers?page=%d" % page); subs += d["data"]
    last = d.get("meta", {}).get("last_page", 1)
    if page >= last: break
    page += 1; time.sleep(1.2)

funnel, confirmados, pend = [], [], []
for s in subs:
    tags = {t["name"] if isinstance(t, dict) else t for t in s.get("tags", [])}
    if TAG_FUNNEL not in tags: continue
    rec = {"phone": "".join(c for c in str(s.get("user_id") or "") if c.isdigit())[-10:],
           "name": s.get("name", ""), "city": (s.get("city") or "").upper(),
           "valor": num(fval(s, "Valor de la compra")), "edad_d": age_days(s.get("subscribed")),
           "falta_dir": TAG_ADDR in tags}
    funnel.append(rec)
    if tags & TAGS_CONFIRM: confirmados.append(rec)
    else: pend.append(rec)

frescos = [p for p in pend if (p["edad_d"] or 99) < 3]
fd_frescos = [p for p in frescos if p["falta_dir"]]
muertos = [p for p in pend if (p["edad_d"] or 99) >= 7]

snap = {"fecha": HOY, "en_funnel": len(funnel), "confirmados_vivos": len(confirmados),
        "pendientes": len(pend), "frescos_72h": len(frescos),
        "falta_direccion_frescos": len(fd_frescos),
        "valor_rescatable": round(sum(p["valor"] for p in frescos)),
        "muertos_7d": len(muertos), "valor_muerto": round(sum(p["valor"] for p in muertos))}

# acumular en el log (una línea por día; reemplaza si ya existe la fecha)
log_path = os.path.join(HERE, "confirmacion_log.jsonl")
lines = []
if os.path.exists(log_path):
    lines = [l for l in open(log_path) if l.strip() and json.loads(l).get("fecha") != HOY]
lines.append(json.dumps(snap, ensure_ascii=False))
open(log_path, "w").write("\n".join(lines) + "\n")

# lista accionable del día
out = {"fecha": HOY, "resumen": snap,
       "accionables": sorted(frescos, key=lambda p: (not p["falta_dir"], -(p["valor"] or 0)))}
json.dump(out, open(os.path.join(HERE, "accionables_hoy.json"), "w"), ensure_ascii=False, indent=1)

print("\n=== SNAPSHOT CONFIRMACIÓN · %s ===" % HOY)
print("Funnel vivo: %d | Confirmados: %d | Pendientes: %d" % (len(funnel), len(confirmados), len(pend)))
print("🟢 RESCATABLES (<72h): %d  ($%s)" % (len(frescos), format(snap["valor_rescatable"], ",")))
print("   ↳ de esos, falta dirección: %d (acción directa hoy)" % len(fd_frescos))
print("⚫ Cola muerta (>7d): %d  ($%s) — fuga, no perseguir" % (len(muertos), format(snap["valor_muerto"], ",")))
print("\n--- LISTA DE HOY (actuar de arriba abajo) ---")
for p in out["accionables"][:15]:
    flag = "📍FALTA DIR" if p["falta_dir"] else "          "
    print("  %s  %-18s %-12s $%-9s  %.1fd" % (flag, p["name"][:18], p["city"][:12], format(round(p["valor"]), ","), p["edad_d"] or 0))
print("\nOK -> accionables_hoy.json + confirmacion_log.jsonl")
