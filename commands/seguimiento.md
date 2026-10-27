---
description: Cadencia operativa COD (diaria/semanal/quincenal/mensual) que orquesta las demás skills cod-ops
---

# Seguimiento Operativo COD 📅

Eres el copiloto de seguimiento de una operación de e-commerce **COD** en Colombia (Meta Ads One CBO + logística Dropi/última milla + contabilidad). Ejecutas la **cadencia de revisión** orquestando `/cod-ops:one-cbo`, `/cod-ops:rentabilidad`, `/cod-ops:ruteo` y `/cod-ops:reportes-logistica`.

> **Primer paso SIEMPRE:** lee `tienda.config.json` del proyecto actual (targets, costos, productos, ruteo). Si no existe, corre `/cod-ops:setup-tienda`. Todos los números viven ahí, no en esta skill.

> Filosofía del mentor: el operador NO vive mirando ventas. **15–20 min diarios en el dashboard, el resto del día pensando en creativos.** El protocolo elimina la emoción de las decisiones.

---

## 🟢 DIARIO (15 min) — presupuesto + creativos
1. **CPA por producto** vs su Target CPA y Break-even (`targets.por_producto` del config).
2. **Aplica el árbol de decisión** (abajo), por producto.
3. **Subir creativos** (a diario): adset nuevo 3:1:1.
4. **Snapshot de confirmación** (`/cod-ops:confirmacion`): correr `snapshot_confirmacion.py` → actuar sobre los frescos (<72h), los `📍FALTA DIR` primero. Acumula la serie en `confirmacion_log.jsonl`. (La routine programada lo hace solo cada mañana.)
5. Decidir el presupuesto con la **ventana que corresponde al volumen** (ver abajo). No forzar gasto. Los anuncios no se apagan antes de 3 días.

Regla de oro: para escalar solo importa el **CPA**. Las métricas blandas son para creativos.

### 🌳 Árbol de decisión: ESCALAR / SOSTENER / CORTAR
Las tres zonas del CPA por producto:
```
        TARGET CPA              BREAK-EVEN CPA
            │                        │
 ESCALAR    │      SOSTENER          │   CORTAR / DESESCALAR
────────────┼────────────────────────┼──────────────────►  CPA
```

Umbrales del escalado vertical (detalle en `/cod-ops:one-cbo`):

**ESCALAR** si se cumplen las tres a la vez:
1. CPA en la ventana **≤ 0,85 × Target**, con ≥ 4–5 compras.
2. **>70 % de compras por atribución de clic.** Si Meta es la única fuente, se cumple solo.
3. **Gate de entrega COD ≥ `gate_entrega_pct`.** Sin esto, escalas pérdidas aunque el CPA sea bello.

Cuánto subir:
- Volumen bajo: **×1,5–2**.
- Volumen alto: **×1,5–5**, hasta 3 veces al día.

**SOSTENER (no tocar el presupuesto)**, cuando:
- El CPA está entre 0,85 y 1,05 × Target, o
- Está bajo el Target pero falta el gate de entrega o hay pocas compras.

> En "sostener" la única palanca es **meter creativos nuevos**.

**DESESCALAR** si el CPA en la ventana es **≥ 1,15 × Target**: bajar 30–60 % + revisar el embudo.
- La campaña madre **no se apaga**: se queda en su piso (presupuesto de arranque o ~30–40 % del pico).
- Ya en el piso → creativos nuevos + auditar el embudo.
- **Apagar un anuncio** solo con gasto bajo + CPA no rentable durante 3–7 días. No apagar anuncios que no gastan: pueden despegar al día 5–7.

**CORTAR duplicados de una ráfaga** (escalado horizontal): a los 3–8 días, si el CPA ≥ 1,2 × Target o hay 0 compras con 1,5 × Target gastado.

### ⏱️ Qué ventana de CPA usar (según el volumen de la campaña)
- **< 20 compras/día:** CPA de las últimas **24–48 h**, revisado **1 vez al día** al mediodía. Con pocas compras, una venta mueve el CPA un 50 % y decidir por horas es decidir sobre ruido.
- **≥ 20–30 compras/día:** CPA **acumulado del día** (desde las 00 h), revisado **2–3 veces al día** entre las 8 h y las 18 h. Nunca antes de las 8–9 h, porque la mañana sale inflada y luego se corrige.
- **Alternativa conservadora** (poca caja): 72 h seguidas bajo el Target → +20 % cada 24 h; 72 h sobre el break-even → −20 %.

### 🖨️ Checklist imprimible de la revisión diaria
Genera/usa esta versión rellenando las líneas desde `targets.por_producto` del config:

```
✅ REVISIÓN DIARIA (15 min) — <TIENDA>
Una vez al día, mismo horario. No mirar a cada rato (el ruido intradía engaña).

LÍNEAS (recalcular cada cierre):
  PRODUCTO A   🎯 Target <t>   ⚖️ Break-even <be>   💵 Mín diario <md>
  PRODUCTO B   🎯 Target <t>   ⚖️ Break-even <be>   💵 Mín diario <md>
  Gate de entrega COD ≥ <gate_entrega_pct>%

POR CADA PRODUCTO, ubica el CPA de hoy:
        TARGET                 BREAK-EVEN
          │                        │
 ESCALAR  │      SOSTENER          │   CORTAR
──────────┼────────────────────────┼────────────► CPA

VENTANA: <20 compras/día → CPA 24–48 h · ≥20–30/día → CPA del día (después de las 8–9 h)

🟢 ¿ESCALAR? — marca las TRES o no escalas:
  [ ] CPA ≤ 0,85 × Target con ≥ 4–5 compras en la ventana
  [ ] >70% compras por atribución de clic (solo Meta → ✔ auto)
  [ ] Entrega ≥ gate
  → 3 ✔ = ×1,5–2 (volumen bajo) · ×1,5–5 (volumen alto, hasta 3 veces/día)
  → ¿se toca el techo de saturación 2 veces? → escalado horizontal (ráfaga)

🟡 ¿SOSTENER (no tocar)?
  - CPA entre 0,85 y 1,05 × Target, o entrega < gate
  → única palanca hoy: creativos nuevos. NO subir presupuesto.

🔴 ¿DESESCALAR?
  [ ] CPA ≥ 1,15 × Target → −30 a −60% + revisar embudo
  - madre: nunca apagar, dejar en su piso
  - duplicados de ráfaga: cortar a los 3–8 días si CPA ≥ 1,2 × Target
  - apagar anuncio: solo con bajo gasto + CPA no rentable 3–7 días
    (NO apagar anuncios que no gastan — pueden despegar al día 5–7)

ANTES DE CERRAR:
  [ ] Subí ≥1 creativo nuevo al laboratorio
  [ ] No forcé gasto ni decidí antes de las 8–9 h
```

## 🔵 SEMANAL — volumen creativo + higiene
- **Exploración:** ≥15 conceptos **nuevos** (15 ángulos distintos, cada uno 1 adset 3:1:1), ~30% imágenes. Un concepto = un ángulo nuevo, NO un video con ediciones menores.
- **Explotación (aparte):** por ganador, 6 variaciones de hook + 6 de formato.
- **Identificar ganadores** (gasto + CPA < target ≥72h): entregar **Ad ID + Creative ID + link de biblioteca** (`facebook.com/ads/library/?id=<AD_ID>`).
- **Productos huérfanos:** pauta sin entregas → pausar.
- **Métricas blandas** (hook rate, CTR, CPC, CPM) → reporte creativo.

## 🟣 QUINCENAL — optimización de entrega
- Revisar el piloto de ruteo (`/cod-ops:ruteo`): tasa de entrega por zona/transportadora.
- **Si hay cambio de ruteo implementado** (`ruteo.fecha_implementacion` en el config): cada vez que se actualiza el master/`data.json`, analizar las órdenes **creadas desde esa fecha** y comparar su % de entrega por zona contra el baseline de `ruteo.plan_zonas`. Concluir solo con cohorte **madura (<5% en tránsito)**. Registrar en `ruteo.semanas`. Zona ≥ gate sostenido → permanente; si no → revertir/probar otra.
- Evaluar nuevas excepciones por ciudad en zonas calientes (devoluciones × volumen).

## 🟠 MENSUAL — cierre + recálculo + gate
1. **Cierre contable** (`/cod-ops:rentabilidad` + `/cod-ops:reportes-logistica`): exportar Dropi maduro (<5% tránsito) + última milla, actualizar `mensual.pauta/apps/shopify_orders` en el config (pauta de Meta MCP, ventas de Shopify MCP), y **regenerar el dashboard** (`build_data.py` → `build_dashboard.py`). El dashboard ya recalcula solo: tasa de confirmación neta, motivos de no-despacho y re-ruteos.
2. **Validar** ingreso cruzando contra el Sheet de contabilidad.
3. **Recalcular** break-even y Target CPA **por producto** → actualizar `targets` en el config.
4. **Gate de entrega:** ¿entrega del mes maduro ≥ `gate_entrega_pct`? → habilitar escalado; si no, foco logística.
5. **Rentabilidad por producto:** ¿alguno al filo del break-even? → bajar CPA o recortar.
6. **Reclamos de rechazados:** generar el reporte de `RECHAZADO` (lo pone el proveedor, no tú) → Excel por transportadora para disputar. Vigilar guías faltantes y picos por transportadora.

---

## 🔧 Runbook — qué se actualiza, cuándo y cómo

| Artefacto | Cadencia | Cómo se actualiza |
|-----------|----------|-------------------|
| **Lista accionable de confirmación** (`accionables_hoy.json`) + serie (`confirmacion_log.jsonl`) | Diaria | `snapshot_confirmacion.py` (la routine programada lo corre cada mañana). Actuar sobre frescos <72h. |
| **Targets/CPA por producto** (`targets` en config) | Mensual (cierre) | Recalcular con `/cod-ops:rentabilidad` (dependen de la entrega del mes). |
| **Pauta (Meta) + órdenes Shopify del mes en curso** (`mensual` en config) | **Automático (rutina diaria)** | La rutina jala spend por producto de Meta MCP + conteo de órdenes de Shopify MCP y los escribe con `update_config_mensual.py` (marca el mes provisional). Regenera el dashboard. |
| **Costos de apps** (`mensual.apps`) | Mensual (manual) | Los confirma el operador; la rutina NO los toca. |
| **Dashboard** (`data.json` → `dashboard.html`): P&G, confirmación neta, no-despacho, rentabilidad x producto | Mensual o bajo demanda | Editar reportes/config → `python3 build_data.py` → `python3 build_dashboard.py`. |
| **Reporte de reclamos de rechazados** (`RECLAMO_rechazados_AAAA-MM.xlsx`) | Mensual o ante pico | `python3 gen_reclamo_rechazados.py` → Excel formateado (encabezado + resumen + detalle por pedido con motivo probable), listo para enviar al proveedor. RECHAZADO lo pone el proveedor (sin stock / guía con error) → reclamable. |
| **Seguimiento de resolución de reclamos** (`reclamos_estado.csv`) | Cuando el proveedor responde | `seguimiento_reclamos.py` siembra/sincroniza el CSV (preserva ediciones). El operador marca `estado` (aprobado/rechazado), `valor_reconocido`, `nota` (o se lo dice a Claude). El dashboard muestra pendiente/aprobado/rechazado + recuperado. |
| **Estado del piloto de ruteo** (`ruteo` en config) | Quincenal | Tras cohorte madura (<5% tránsito): comparar entrega por zona vs baseline; registrar en `ruteo.semanas`. |
| **API key de Chatea Pro** (`.env`) | Al rotarla | Reemplazar `CHATEAPRO_API_KEY` en `.env` (nunca en el chat ni en el config). |

> **Definiciones clave que el runbook asume** (ver `/cod-ops:reportes-logistica` y `/cod-ops:rentabilidad`):
> - **Confirmación = despacho** (misma puerta): `despachadas / resueltas_netas`. La tasa **neta** descuenta los **re-ruteos** (un cancelado recreado con otra transportadora o pasado a última milla NO es pérdida).
> - **No-despacho ≠ cobertura:** si el pedido tenía transportadora asignada, la caída es de confirmación, no de cobertura.
> - **Tasa de confirmación histórica:** del dato duro Dropi (Shopify→despacho), NUNCA de los tags efímeros de Chatea.

---

## Principios transversales
- **Opera con CPA, no con ROAS** (si el píxel tiene el bug USD/COP, el ROAS está inflado).
- **La entrega es el gate del escalado** — el break-even depende de ella.
- **Una sola campaña One CBO.**
- **Paciencia de 72h** en toda decisión de presupuesto/apagado.
- Los números viven en `tienda.config.json` y se recalculan cada cierre.
