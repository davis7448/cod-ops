---
description: Parser y análisis de reportes logísticos COD (Dropi + última milla), con dedup de recreaciones
---

# Reportes de Logística (Dropi + Última Milla) 📦

Parseas y analizas los reportes logísticos de una operación COD en dos plataformas: **Dropi** (fulfillment) y **última milla propia**. Tu salida alimenta `/cod-ops:rentabilidad`.

> **Primer paso:** lee `tienda.config.json` (`dropi_columnas`, `estatus`, `reportes.dropi`, `costos.flete_ultima_milla`). El mapeo de columnas y los estatus salen de ahí.

> Por tiempos de entrega COD, pedir los reportes desde un periodo **ya maduro** para que la tasa de entrega no se ensucie con órdenes en tránsito.

---

## 1. Reporte DROPI — `ordenes_productos_*.xlsx`
Una fila por producto de orden. Columnas (mapeadas en `dropi_columnas` del config):

| Concepto | Columna por defecto |
|----------|---------------------|
| desenlace | `ESTATUS` |
| recaudo / AOV | `TOTAL DE LA ORDEN` |
| flete ida | `PRECIO FLETE` |
| flete retorno | `COSTO DEVOLUCION FLETE` |
| COGS | `PRECIO PROVEEDOR X CANTIDAD` |
| mix | `PRODUCTO`, `CANTIDAD` |
| zona | `DEPARTAMENTO DESTINO`, `CIUDAD DESTINO`, `TRANSPORTADORA` |

**Clasificación de ESTATUS:**
- Entregadas: `ENTREGADO`
- Devueltas (`estatus.devolucion`): cuestan flete **ida + vuelta**
- No despachadas (`estatus.no_despachado`): CANCELADO/RECHAZADO/PENDIENTE → **no cobran flete**
- En proceso (excluir de tasas): EN TRANSITO, EN RUTA, DESPACHADA, GUIA_GENERADA, NOVEDAD*, EN BODEGA*

**Costo por devolución** = `PRECIO FLETE` + `COSTO DEVOLUCION FLETE` (promedio sobre devueltas).

## 2. Reporte ÚLTIMA MILLA — `pedidos-vendedor-seller-*.xlsx`
Hoja `Pedidos`. Columnas: `estado`, `valor_total_cop`/`valor_cod_cop`, `categoria_fallido`/`fallido_cobrable`/`motivo_fallido`, `producto`/`cantidad`/`ciudad`.
**Flete última milla:** fijo (`costos.flete_ultima_milla`). **Devolución NO se cobra** salvo `fallido_cobrable`=true. Estructuralmente más rentable que Dropi.

## 3. Embudo y tasas (modelo correcto)
**CANCELADO, PENDIENTE CONFIRMACIÓN y RECHAZADO NO cobran flete** → no son despacho.
```
Sincronización = órdenes en plataformas / pedidos Shopify
Tasa despacho  = despachadas / generadas-resueltas      [despachadas = entregadas+devueltas]
Tasa ENTREGA   = entregadas / despachadas               ← KPI operativo (transportadora)
Conversión total = entregadas / generadas               ← la que mueve el break-even del ad
```
> Distinguir SIEMPRE "tasa de entrega" (sobre despachadas) de "conversión generada→entregada" (sobre todas). Trabajar a **nivel de orden única** (dedup por ID), no por línea.

### ⚠️ Recreación entre plataformas
Una orden cancelada/devuelta en Dropi se **recrea** en última milla con la misma referencia Shopify. Hay que:
1. **Deduplicar por referencia Shopify** cruzando ambas plataformas (normalizar a dígitos: `#2581`→`2581`).
2. Tomar el **desenlace final** (prioridad: Entregado > en proceso > Devolución > Rechazado > Cancelado).
Si no, se **subcuentan entregas y sobrecuentan cancelaciones**. La última milla actúa como **red de rescate** + más barata.

**Recreación intra-Dropi (sin referencia Shopify):** una cancelada se recrea como guía nueva sin número Shopify (transportadora la canceló / cliente cambió cantidad / recompra). Identificar por **teléfono + familia de producto + ventana ≤21 días**; colapsar reintentos a 1 venta (mejor desenlace), respetando recompras reales (múltiples ENTREGADO = ventas distintas). En cambios de cantidad, usar SIEMPRE los valores de la orden **final/entregada**. Es estimación con incertidumbre — idealmente pedir al operador que la guía recreada herede la referencia Shopify.

## 3b. Cálculo del INGRESO (concilia con contabilidad)
```
INGRESO = Σ(TOTAL − COGS − PRECIO_FLETE)  de ENTREGADAS
        − Σ(PRECIO_FLETE)                 de DEVOLUCIONES   ← SOLO flete de salida
        − Σ(PRECIO_FLETE)                 de FLETES ABIERTOS (tránsito, provisión)
```
Reglas críticas:
- **NO usar la columna `GANANCIA`** → reconstruir con columnas crudas por orden (sin promediar).
- En devoluciones se resta **solo `PRECIO FLETE`**, NO `COSTO DEVOLUCION FLETE`.
- Fletes abiertos (tránsito) = **provisión temporal**.
- Atribución por **fecha de creación** (`FECHA`).
- Incluir última milla deduplicando recreaciones.

**Validación cruzada (siempre):** comparar este INGRESO mes a mes contra la hoja INGRESOS de la contabilidad. Si un mes maduro (≤5% tránsito) NO cuadra, la contabilidad está subregistrada para ese mes.

## 4. Comparativa de canales
| Concepto | Dropi | Última milla |
|----------|-------|--------------|
| Flete/entrega | ~$18k | `flete_ultima_milla` |
| Costo devolución | flete ida+vuelta | $0 salvo visita |
| MC/entrega | AOV−COGS−flete | mayor (flete menor) |

**Recomendación recurrente:** migrar el máximo volumen a última milla donde haya cobertura.

## Notas de procesamiento
- Leer `.xlsx` con `openpyxl` (`data_only=True`). El motor `build_data.py` (en la carpeta de contabilidad del proyecto) ya implementa este parseo desde el config.
- Declarar supuestos. Segmentar devoluciones por ciudad/transportadora/producto.
