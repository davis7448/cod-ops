#!/usr/bin/env python3
"""Motor de datos del dashboard COD (genérico, plugin cod-ops).
Lee tienda.config.json (mismo directorio) + reportes Dropi -> data.json.
Uso: python3 build_data.py [ruta/al/tienda.config.json]"""
import openpyxl, json, os, sys
from collections import defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "tienda.config.json")
CFG = json.load(open(CFG_PATH, encoding="utf-8"))

COL = CFG["dropi_columnas"]
DEV = set(CFG["estatus"]["devolucion"])
NODESP = set(CFG["estatus"]["no_despachado"])
PRODUCTOS = {k: [s.upper() for s in v] for k, v in CFG["productos"].items() if not k.startswith("_")}
PROD_ORDER = list(PRODUCTOS.keys()) + ["OTRO"]
COSTOS = CFG["costos"]
M = CFG["mensual"]
PAUTA = M.get("pauta", {})
APPS = M.get("apps", {})
SHOPIFY_ORD = M.get("shopify_orders", {})
INFORMATIVO = {k: v for k, v in M.get("informativo", {}).items() if not k.startswith("_")}
PROVISIONAL = set(M.get("provisional", []))
MES_INICIO = M.get("mes_inicio_detalle", "2000-01")
REPORTES = CFG["reportes"]["dropi"]

def fam(p):
    p = str(p or "").upper()
    for nombre, kws in PRODUCTOS.items():
        if any(kw in p for kw in kws):
            return nombre
    return "OTRO"

def num(x):
    try: return float(x or 0)
    except: return 0.0

seen = set()
cells = defaultdict(lambda: defaultdict(float)); cnt = defaultdict(lambda: defaultdict(int))
transp = defaultdict(lambda: defaultdict(float)); depto = defaultdict(lambda: defaultdict(float))
ciudad_tr = defaultdict(lambda: defaultdict(lambda: [0, 0]))
nod_tipo = defaultdict(int); nod_carrier = defaultdict(int); nod_depto = defaultdict(lambda: [0, 0])

for f in REPORTES:
    if not os.path.exists(f): continue
    ws = openpyxl.load_workbook(f, data_only=True).active
    rows = list(ws.iter_rows(values_only=True)); idx = {h: i for i, h in enumerate(rows[0])}
    def g(r, key): return r[idx[COL[key]]]
    for r in rows[1:]:
        oid = g(r, "id")
        if oid in seen: continue
        seen.add(oid)
        try: mk = datetime.strptime(str(g(r, "fecha")), COL["fecha_formato"]).strftime("%Y-%m")
        except: continue
        prod = fam(g(r, "producto")); s = str(g(r, "estatus")); fl = num(g(r, "flete")); k = (mk, prod)
        cnt[k][s] += 1; cnt[k]["_t"] += 1
        dp_all = str(g(r, "departamento") or "N/D").strip().upper()
        nod_depto[dp_all][1] += 1
        if s in NODESP:
            nod_depto[dp_all][0] += 1
            bk = "CANCELADO" if s == "CANCELADO" else ("RECHAZADO" if s == "RECHAZADO" else "PENDIENTE/CONF")
            nod_tipo[bk] += 1
            tr_nd = g(r, "transportadora")
            nod_carrier["con" if tr_nd not in (None, "") else "sin"] += 1
        if s == "ENTREGADO":
            cells[k]["ingreso"] += num(g(r, "total")) - num(g(r, "cogs")) - fl
            cells[k]["cogs"] += num(g(r, "cogs")); cells[k]["flete"] += fl
            cells[k]["tot_ent"] += num(g(r, "total")); cells[k]["ent"] += 1
        elif s in DEV: cells[k]["ingreso"] -= fl; cells[k]["dev"] += 1
        elif s in NODESP: pass
        else: cells[k]["ingreso"] -= fl; cells[k]["tran"] += 1
        if s == "ENTREGADO" or s in DEV:
            t = str(g(r, "transportadora") or "N/D").strip().upper()
            dp = str(g(r, "departamento") or "N/D").strip().upper()
            ci = str(g(r, "ciudad") or "N/D").strip().upper()
            es_ent = 1 if s == "ENTREGADO" else 0
            transp[t]["desp"] += 1; transp[t]["ent"] += es_ent
            if s in DEV: transp[t]["fdev"] += fl + num(g(r, "costo_dev_flete"))
            depto[dp]["desp"] += 1; depto[dp]["ent"] += es_ent
            cc2 = ciudad_tr[ci][t]; cc2[0] += 1; cc2[1] += es_ent

def prod_metrics(mk, prod):
    c = cells[(mk, prod)]; cc = cnt[(mk, prod)]
    ent = int(c.get("ent", 0)); dev = int(c.get("dev", 0)); tran = int(c.get("tran", 0))
    canc = cc.get("CANCELADO", 0); rech = cc.get("RECHAZADO", 0)
    pend = cc.get("PENDIENTE CONFIRMACION", 0) + cc.get("PENDIENTE", 0)
    desp = ent + dev + tran; resu = ent + dev + rech + canc + pend
    ingreso = round(c.get("ingreso", 0)); tot_ent = c.get("tot_ent", 0)
    pauta = PAUTA.get(mk, {}).get(prod, 0)
    conf = COSTOS["confirmacion_por_despachada"] * desp
    com = round(COSTOS["comision_ventas_pct"] * tot_ent)
    imp = round(COSTOS["impuesto_pct"] * ingreso)
    return dict(ordenes=int(cc["_t"]), entregadas=ent, devueltas=dev, transito=tran, canceladas=canc,
        rechazadas=rech, pend_conf=pend, despachadas=desp,
        tasa_despacho=round(desp / resu * 100, 1) if resu else 0,
        tasa_entrega=round(ent / desp * 100, 1) if desp else 0,
        tasa_devolucion=round(dev / desp * 100, 1) if desp else 0,
        ingreso=ingreso, cogs=round(c.get("cogs", 0)), flete=round(c.get("flete", 0)),
        total_entregado=round(tot_ent), pauta=pauta, confirmaciones=conf, comision=com, impuesto=imp,
        cpa=round(pauta / cc["_t"]) if cc["_t"] else 0)

meses = {}
for mk in sorted(set(k[0] for k in cells)):
    if mk < MES_INICIO: continue
    prods = {}; tot = defaultdict(float)
    for prod in PROD_ORDER:
        if (mk, prod) not in cells: continue
        m = prod_metrics(mk, prod); prods[prod] = m
        for kk in ["ordenes", "entregadas", "devueltas", "transito", "despachadas", "ingreso",
                   "cogs", "flete", "pauta", "confirmaciones", "comision", "impuesto", "total_entregado",
                   "canceladas", "rechazadas", "pend_conf"]:
            tot[kk] += m[kk]
    apps = APPS.get(mk, 0)
    pauta_total = sum(PAUTA.get(mk, {}).values())
    pauta_huerfana = round(pauta_total - tot["pauta"])
    tot["pauta"] = pauta_total
    util_total = tot["ingreso"] - tot["pauta"] - tot["confirmaciones"] - tot["comision"] - tot["impuesto"] - apps
    for prod, m in prods.items():
        share = m["ingreso"] / tot["ingreso"] if tot["ingreso"] else 0
        m["apps"] = round(apps * share)
        m["utilidad"] = m["ingreso"] - m["pauta"] - m["confirmaciones"] - m["comision"] - m["impuesto"] - m["apps"]
        m["margen"] = round(m["utilidad"] / m["ingreso"] * 100, 1) if m["ingreso"] else 0
    sh = SHOPIFY_ORD.get(mk, 0)
    no_desp = sum(prods[p]["canceladas"] + prods[p]["rechazadas"] + prods[p]["pend_conf"] for p in prods)
    resuelt = tot["despachadas"] + tot["canceladas"] + tot["rechazadas"] + tot["pend_conf"]
    confirmacion = {"resueltas": int(resuelt), "despachadas": int(tot["despachadas"]),
        "canceladas": int(tot["canceladas"]), "rechazadas": int(tot["rechazadas"]),
        "pend_conf": int(tot["pend_conf"]), "generadas_shopify": sh,
        "tasa": round(tot["despachadas"] / resuelt * 100, 1) if resuelt else 0,
        "tasa_vs_generadas": round(tot["despachadas"] / sh * 100, 1) if sh else None}
    meses[mk] = {"shopify_orders": sh, "provisional": mk in PROVISIONAL, "confirmacion": confirmacion,
        "sincronizacion": round(tot["ordenes"] / sh * 100, 1) if sh else None,
        "tasa_despacho": round(tot["despachadas"] / resuelt * 100, 1) if resuelt else 0,
        "tasa_entrega": round(tot["entregadas"] / tot["despachadas"] * 100, 1) if tot["despachadas"] else 0,
        "productos": prods,
        "pyg": {"ingreso": round(tot["ingreso"]), "cogs": round(tot["cogs"]), "flete": round(tot["flete"]),
                "pauta": round(tot["pauta"]), "confirmaciones": round(tot["confirmaciones"]),
                "comision": round(tot["comision"]), "impuesto": round(tot["impuesto"]), "apps": apps,
                "pauta_huerfana": pauta_huerfana, "utilidad": round(util_total),
                "margen": round(util_total / tot["ingreso"] * 100, 1) if tot["ingreso"] else 0}}

def tasas(d):
    desp = int(d["desp"]); ent = int(d["ent"])
    return dict(despachadas=desp, entregadas=ent, devueltas=desp - ent,
        tasa_entrega=round(ent / desp * 100, 1) if desp else 0,
        tasa_devolucion=round((desp - ent) / desp * 100, 1) if desp else 0,
        costo_devoluciones=round(d.get("fdev", 0)))

transportadoras = {t: tasas(d) for t, d in transp.items() if d["desp"] >= 10}
departamentos = {dp: tasas(d) for dp, d in depto.items() if d["desp"] >= 15}
matriz = {}
for ci, trs in ciudad_tr.items():
    if sum(v[0] for v in trs.values()) < 12: continue
    matriz[ci] = {t: {"desp": v[0], "entrega": round(v[1] / v[0] * 100, 1) if v[0] >= 4 else None}
                  for t, v in trs.items() if v[0] >= 4}

nod_total = sum(nod_tipo.values())
no_despacho = {"total": nod_total, "tipo": dict(nod_tipo),
   "con_transportadora_pct": round(nod_carrier.get("con", 0) / nod_total * 100, 1) if nod_total else 0,
   "sin_transportadora": nod_carrier.get("sin", 0),
   "top_departamentos": [{"depto": d, "nod": v[0], "total": v[1], "tasa": round(v[0] / v[1] * 100, 1)}
       for d, v in sorted(nod_depto.items(), key=lambda x: -(x[1][0] / x[1][1] if x[1][1] else 0))
       if v[1] >= 15][:10]}
logistica = {"transportadoras": transportadoras, "departamentos": departamentos,
             "matriz_ciudad_transp": matriz, "ruteo": CFG["ruteo"], "no_despacho": no_despacho}

data = {"tienda": CFG["tienda"]["nombre"], "meses_nombre": CFG.get("dashboard", {}).get("meses_nombre", {}),
        "productos": list(PRODUCTOS.keys()), "meses": meses,
        "informativo": INFORMATIVO, "logistica": logistica}
out = os.path.join(os.path.dirname(CFG_PATH), "data.json")
json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK ->", out)
for mk in sorted(meses):
    p = meses[mk]; pg = p["pyg"]
    print(f"{mk}{' (prov)' if p['provisional'] else ''}: sync={p['sincronizacion']}% "
          f"despacho={p['tasa_despacho']}% entrega={p['tasa_entrega']}% | "
          f"ingreso={pg['ingreso']:,} util={pg['utilidad']:,} margen={pg['margen']}%")
