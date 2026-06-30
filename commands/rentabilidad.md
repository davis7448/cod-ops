---
description: Economía unitaria COD — break-even CPA, target CPA, ROAS real y cierre contable
---

# Rentabilidad COD 🧮

Calculas la economía unitaria real de una operación COD a partir de Meta Ads, Shopify y logística (Dropi + última milla), y emites veredicto de **escalado/desescalado** alineado con `/cod-ops:one-cbo`.

> **Primer paso:** lee `tienda.config.json` (`costos`, `targets`, `productos`). Los costos del modelo (confirmación, comisión, impuesto, flete) salen de ahí.

> Regla de oro: en COD **el ROAS de plataforma miente**; manda el **CPA** contra el **break-even CPA real**, que depende críticamente de la **tasa de entrega**.

---

## Datos de entrada
| Dato | Fuente | Notas |
|------|--------|-------|
| Gasto y nº de compras | Meta Ads MCP (`ads_get_ad_entities`, level=account) | `actions:omni_purchase` |
| AOV real | Shopify (`run-analytics-query`: `average_order_value`) | NUNCA asumir el precio de oferta; hay upsells |
| COGS | reporte Dropi (`PRECIO PROVEEDOR X CANTIDAD`) | por orden entregada |
| Flete y costo devolución | reportes (`/cod-ops:reportes-logistica`) | flete ida; en devolución ida+vuelta |
| Tasa de entrega | reportes | entregadas / **despachadas** (KPI operativo) |
| Conversión gen→entregada | reportes | entregadas / **generadas** (la del break-even) |

---

## Fórmulas

**Margen de contribución por orden ENTREGADA:**
```
MC_entregada = Precio_oferta − COGS_oferta − Flete  (− comisión plataforma si aplica)
```
> ⚠️ NUNCA promediar precio/COGS entre ofertas distintas. Segmentar por **oferta = (precio × nº de combos)** y, si se necesita un solo número, ponderar por el **mix real**. El **flete es fijo por envío**, no por unidad → bundles ×2/×3 lo amortizan (+37–100% margen/envío). **Subir el mix de bundles es palanca de margen sin costo de ads.**

**Break-even CPA por orden GENERADA:**
```
Por cada N generadas (resueltas):
  ingreso_neto = (entregadas × MC_entregada) − (devueltas × flete_ida_vuelta) − provisión_tránsito
  costos_op    = confirmaciones + comisión_ventas + apps_fijas
                 · confirmaciones  = costos.confirmacion_por_despachada × DESPACHADAS (entregadas+devueltas+tránsito)
                 · comisión_ventas = costos.comision_ventas_pct × Σ(total orden ENTREGADA)
                 · apps_fijas      = mensual, prorratear
  Break-even_CPA = (ingreso_neto − costos_op) / N_generadas
```
> NO olvidar los costos operativos: bajan el break-even sustancialmente. El modelo "solo COGS+flete" sobreestima la rentabilidad y contradice la contabilidad.
> Solo lo **despachado** cobra flete (entregadas+devueltas). CANCELADO, PENDIENTE CONFIRMACIÓN y RECHAZADO **no cobran flete**. Última milla solo cobra devolución **si hubo visita** (`fallido_cobrable`). Producto recuperable ⇒ solo se pierde el flete.
> No confundir **tasa de entrega** (entregadas/despachadas) con **conversión generada→entregada** (entregadas/generadas, la del break-even).

**Target CPA** (con profit objetivo, p.ej. 20–25%):
```
Target_CPA = Break-even_CPA − (AOV × %profit × conversión_gen→entregada)
```

**ROAS real** (deflactado):
```
ROAS_bruto = (compras × AOV) / gasto
ROAS_real  = ROAS_bruto × conversión_gen→entregada     ← el que cuenta
```

---

## Veredicto
```
CPA_actual  <  Break-even_CPA   → rentable
CPA_actual  ≈  Break-even_CPA   → al filo, NO escalar sin mejorar entrega
CPA_actual  >  Break-even_CPA   → perdiendo, desescalar / arreglar logística
```

## Palancas (orden de impacto típico)
1. **Tasa de entrega** — cada ~6 pts suben el break-even varios miles/venta.
2. **Migrar volumen a última milla** donde haya cobertura — menor flete + red de rescate.
3. **Reducir devoluciones** — cada una quema flete ida+vuelta.
4. **Subir AOV** — upsells/bundles.
5. **Bajar CPA** — volumen creativo (One CBO).

> SIEMPRE deduplicar recreaciones antes de calcular (`/cod-ops:reportes-logistica`): sin limpiar, las cancelaciones se sobrecuentan y el break-even sale subestimado.

## Cierre contable (sistema de contabilidad del proyecto)
Flujo bajo demanda (el usuario pide, Claude actualiza):
1. Usuario exporta Dropi (+ última milla) del mes maduro.
2. Claude jala pauta (Meta MCP) + ventas (Shopify MCP).
3. Calcula el cierre, actualiza el master y regenera el dashboard (`build_data.py` → `build_dashboard.py`).

**Cierre = INGRESO NETO − Pauta − Confirmaciones − Comisión − Impuesto − Apps.** Validar el ingreso cruzando contra el Sheet del usuario (un mes maduro debe cuadrar; si no, está subregistrado). Marcar provisional si >5% en tránsito.

**Rentabilidad por producto:** usar la **pauta TOTAL del producto** (todas sus campañas), no el CPA del ganador. Vigilar **pauta huérfana** (pauta sin entregas) — cuenta en el P&G del mes.
