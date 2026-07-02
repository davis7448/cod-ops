#!/usr/bin/env python3
"""Actualiza los datos mensuales (pauta por producto + órdenes Shopify) en
tienda.config.json. Lo usa la rutina automática con los valores que jala de
Meta Ads MCP y Shopify MCP. NO toca apps ni reportes de plataformas (manuales).

Uso:
  python3 update_config_mensual.py <YYYY-MM> --pauta '{"CEELIKE":123,"JOINT":456,"OTRO":0}' --shopify 300 [--apps 400000] [--config ruta]

Marca el mes como provisional (mes en curso, aún inmaduro) salvo --final.
"""
import json, os, sys, argparse

MESES_ES = {"01":"Enero","02":"Febrero","03":"Marzo","04":"Abril","05":"Mayo","06":"Junio",
            "07":"Julio","08":"Agosto","09":"Septiembre","10":"Octubre","11":"Noviembre","12":"Diciembre"}

ap = argparse.ArgumentParser()
ap.add_argument("month")
ap.add_argument("--pauta", required=True, help='JSON: {"CEELIKE":..,"JOINT":..,"OTRO":..}')
ap.add_argument("--shopify", type=int, required=True)
ap.add_argument("--apps", type=int, default=None)
ap.add_argument("--final", action="store_true", help="marca el mes como cerrado (no provisional)")
ap.add_argument("--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "tienda.config.json"))
a = ap.parse_args()

cfg = json.load(open(a.config, encoding="utf-8"))
m = cfg["mensual"]
pauta = json.loads(a.pauta)
m.setdefault("pauta", {})[a.month] = pauta
m.setdefault("shopify_orders", {})[a.month] = a.shopify
if a.apps is not None:
    m.setdefault("apps", {})[a.month] = a.apps
prov = set(m.get("provisional", []))
if a.final: prov.discard(a.month)
else: prov.add(a.month)
m["provisional"] = sorted(prov)
# nombre del mes en el dashboard
nm = cfg.setdefault("dashboard", {}).setdefault("meses_nombre", {})
if a.month not in nm:
    nm[a.month] = MESES_ES.get(a.month[5:7], a.month) + (" " + a.month[:4] if a.month[:4] != "2026" else "")
json.dump(cfg, open(a.config, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK — %s: pauta=%s shopify=%s%s%s" % (a.month, pauta, a.shopify,
      (" apps=%d" % a.apps) if a.apps is not None else "",
      " [provisional]" if not a.final else " [cerrado]"))
