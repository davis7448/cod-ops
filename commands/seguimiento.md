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
4. **No** tocar presupuesto ni apagar antes de **72h**. **No** forzar gasto.

Regla de oro: para escalar solo importa el **CPA**. Las métricas blandas son para creativos.

### 🌳 Árbol de decisión: ESCALAR / SOSTENER / CORTAR
Las tres zonas del CPA por producto:
```
        TARGET CPA              BREAK-EVEN CPA
            │                        │
 ESCALAR    │      SOSTENER          │   CORTAR / DESESCALAR
────────────┼────────────────────────┼──────────────────►  CPA
```

**ESCALAR (+20% de presupuesto)** — solo si se cumplen las TRES a la vez:
1. **72h consecutivas** con CPA bajo el Target (ver definición de 72h abajo).
2. **>70% de compras por atribución de clic** (1d-click). Si Meta es la única fuente, se cumple solo.
3. **Gate de entrega COD ≥ `gate_entrega_pct`** (sin esto, escalas pérdidas aunque el CPA sea bello).
> Si el ROAS real duplica el Target → **+100% (duplicar)** en vez de +20%.

**SOSTENER (no tocar el presupuesto)** — el caso por defecto:
- CPA rentable pero **por encima del Target** (entre las dos líneas), o
- CPA bajo el Target pero **aún no cumple las 72h** o el gate de entrega.
> En "sostener" tu única palanca es **meter creativos nuevos** para bajar el CPA y empujar la campaña hacia la zona de escalar. NO subas presupuesto.

**CORTAR / DESESCALAR (−20%)**:
- CPA **sobre el Break-even** (perdiendo) durante 72h → −20% + revisar embudo.
- Si ya estás en el mínimo de gasto diario → no bajes más: creativos nuevos + auditar funnel.
- **Apagar un anuncio** solo con **bajo gasto + CPA no rentable durante 3–7 días** (no apagar anuncios que no gastan: pueden despegar al día 5–7).

### ⏱️ Cómo se cuentan las 72h (clave — no confundir)
- Son **72h consecutivas de desempeño** (3 días seguidos) respecto al Target CPA, evaluadas en la **revisión diaria (1 vez/día)**, NO una ventana móvil que chequeas cada hora ni un cronómetro desde el último cambio o la publicación.
- Están ancladas a la **racha de rendimiento**, no a un hito técnico. Razón: Meta tiene ruido intradía (un día un "bolsillo de audiencia" no compra y el CPA sube); decidir en <72h es decidir sobre ruido, no tendencia. Ligado a la fase de aprendizaje (~10 eventos en 3 días con la actualización nueva).
- **Las 72h son la puerta de ENTRADA al escalado. Una vez dentro, subes +20% CADA 24h** mientras el rendimiento aguante — NO vuelves a esperar 72h tras cada subida.
- **Para desescalar es igual de paciente:** necesitas 72h (3 días) seguidos por debajo del Target antes de bajar −20%. "Un mal día es un mal día."

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
1. **Cierre contable** (`/cod-ops:rentabilidad` + `/cod-ops:reportes-logistica`): exportar Dropi maduro (<5% tránsito), jalar pauta (Meta MCP) y ventas (Shopify MCP), generar cierre y regenerar dashboard.
2. **Validar** ingreso cruzando contra el Sheet de contabilidad.
3. **Recalcular** break-even y Target CPA **por producto** (dependen de la entrega del mes) → actualizar `targets` en el config.
4. **Gate de entrega:** ¿entrega del mes maduro ≥ `gate_entrega_pct`? → habilitar escalado; si no, foco logística.
5. **Rentabilidad por producto:** ¿alguno al filo del break-even? → bajar CPA o recortar.

---

## Principios transversales
- **Opera con CPA, no con ROAS** (si el píxel tiene el bug USD/COP, el ROAS está inflado).
- **La entrega es el gate del escalado** — el break-even depende de ella.
- **Una sola campaña One CBO.**
- **Paciencia de 72h** en toda decisión de presupuesto/apagado.
- Los números viven en `tienda.config.json` y se recalculan cada cierre.
