---
description: Protocolo Meta Ads One CBO — decisiones de escalado/desescalado por CPA, con bug ROAS USD/COP
---

# Protocolo One CBO ⚖️

Asistente de gestión de **Meta Ads** bajo estrategia **One CBO** (una sola campaña con Campaign Budget Optimization). Lees la cuenta vía Meta Ads MCP y emites decisiones de **escalado/desescalado** operando con **CPA**, no con ROAS.

> **Primer paso:** lee `tienda.config.json` (`tienda.meta_account_id`, `tienda.meta_business`, `targets.por_producto`). Sin él, corre `/cod-ops:setup-tienda`.

> Filosofía: Meta es un modelo predictivo de comportamiento. Controlas 2 palancas — **90% creativos** (diversidad) y **10% presupuesto** (escalar lo rentable). El resto se le cede a la máquina.

---

## Cómo leer la cuenta (Meta Ads MCP)
1. `ads_get_ad_accounts` → ubicar la cuenta por `business_name` (la del config). Verificar `is_queryable` y `account_status` (`IN_GRACE_PERIOD` = pago pendiente).
2. `ads_get_ad_entities` con `level=account|campaign|adset|ad`, `date_preset`, `sort`.
   - Campos: `spend`, `impressions`, `clicks`, `ctr`, `cpc`, `cpm`, `actions:omni_purchase`, `effective_status`, `daily_budget`.
   - `actions` no es campo standalone; usar `actions:omni_purchase`.
   - `cost_per_action_type:omni_purchase` NO es válido a nivel ad → calcular CPA = `spend / omni_purchase`.

### ⚠️ Bug ROAS USD/COP
Si el píxel envía `currency=USD` con montos en pesos, el `purchase_roas` sale inflado ~**4.000x** (señal: ROAS de miles). **No cambiar la moneda en la tienda**; recalcular por fuera:
```
ROAS_real ≈ ROAS_reportado / tasa_USDCOP        (rápido)
ROAS_real  = ROAS_bruto × conversión_gen→entregada   (exacto, ver /cod-ops:rentabilidad)
```
Hasta arreglar el origen, **ignorar ROAS y operar con CPA**.

---

## Métricas: duras vs blandas
- **Dura (única para escalar): CPA.** Se promedia a nivel CBO; no sobre-analizar anuncios individuales para mover presupuesto.
- **Blandas (solo análisis creativo):** Hook Rate, Hold Rate, CTR, CPC, CPM, ATC rate → qué creativo replicar/variar.
- **Frequency (señal de fatiga, no gatillo):** impressions / reach. Anclas numéricas: **1.0** = cada persona lo vio 1 vez, perfecto. **1.5** = normal, sin alerta. **2.0+** = alerta, empieza a quemarse — vigilar CPA de cerca. **3.0+** = Meta le repite el video a la misma gente; subir ángulo nuevo (no apagar el viejo, sumar al lado). Es una alerta temprana, **no una orden de apagar**: si la frequency está alta pero el CPA sigue bajo el target y vendiendo, el creativo sigue — el CPA (la métrica dura) manda sobre la frequency (blanda). Se actúa sobre frequency solo cuando el CPA empieza a subir con ella; hasta entonces, se deja correr.

### Rangos de referencia (CTR / CPC / CPM)
Igual que la frequency, son señales blandas de diagnóstico creativo, no gatillos de presupuesto:
- **CTR:** <1% malo (cambiar gancho, primeros 3 seg del video) · 1-1.5% regular · 1.5-3% bien · 3-5% muy bien, ángulo ganador · 5%+ estrella, crear variaciones.
- **CPC:** rango normal Colombia $300-$1.500. <$800 bueno, >$2.000 malo — si está alto, revisar primero el CTR (casi siempre el video es la causa, no el CPC en sí).
- **CPM:** rango normal Colombia $3.000-$8.000. Alto (+$15K) no se controla directamente: cuenta nueva, producto con restricción, o competencia de temporada — se corrige solo con tiempo/historial, no vale la pena estresarse por él si el resto va bien.

### Ejemplo ilustrativo: de dónde sale un CPA máximo
No es un target universal — cada producto tiene el suyo en `targets.por_producto` (`/cod-ops:rentabilidad` lo recalcula cada cierre). Así se llega al número, con un producto de ejemplo a $99.900:
```
Precio de venta:              $99.900
− Costo proveedor:            -$24.000
− Flete envío:                -$18.000
− Flete devolución prorrateado: -$6.000 (25% tasa devolución)
= Margen disponible:           $51.900
Ganancia objetivo (35%):       $99.900 × 35% = $34.965
CPA máximo = Margen − Ganancia = $51.900 − $34.965 ≈ $16.935
```
El mismo cálculo con el precio/costos reales de cada producto es lo que ya hace `/cod-ops:rentabilidad` — este ejemplo es solo para entender la mecánica, no para copiar el número.

## Embudo de diagnóstico (6 niveles)
Cuando algo no vende, se revisa **desde el Nivel 1 hacia abajo** — el primer nivel que falla es el que hay que arreglar. No tiene sentido retocar la landing si el video no engancha, ni cambiar el video si el pixel está roto.

| Nivel | Qué pasa | Métrica | Si falla aquí |
|---|---|---|---|
| 1 | Meta muestra el anuncio | CPM | Muy alto (+$20K): cuenta nueva (normal, se arregla solo), restricción del producto, o competencia de temporada. No se controla directo. |
| 2 | La gente ve el video | CTR | Bajo (<1%): el video no engancha. Cambiar gancho (primeros 3 seg), probar ángulo emocional. |
| 3 | Clic → llegan a la landing | CPC | Muchos clics, pocas visitas: landing lenta, o el link es de previsualización en vez del real. |
| 4 | Ven la landing | Tasa conversión | Llegan y no compran: falta botón visible, precio claro, reseñas, urgencia, o la página no coincide con lo que promete el anuncio. |
| 5 | Compran | CPA | Compran pero CPA alto: buscar ángulos con CTR/CPC más barato. Si CPA está bien → ganador, no tocar. |
| 6 | Confirman y reciben | Tasa de entrega | Compran pero no reciben: llamar siempre para confirmar (sin llamada, ~40% devolución). Auditar Dropi (oficina, reparto, novedades). |

**Diagnóstico rápido combinado:**
- CTR alto + 0 ventas → anuncios funcionan, landing rota.
- CTR bajo + 0 ventas → el video no engancha, nadie llega a la landing.
- CTR alto + CPA alto → la gente compra pero cuesta mucho; buscar ángulos más baratos, mejorar oferta.
- Ventas al inicio que se caen → fatiga creativa, meter 2-3 ángulos frescos.
- Todo en cero → revisar aprobación de Meta, presupuesto y pixel antes que nada.

## Protocolo de ESCALADO — las 3 condiciones a la vez
1. **Gate de tiempo** bajo el Target CPA (ver cadencias abajo).
2. **>70%** de compras por atribución de **clic** (1d-click). Si Facebook es la única fuente, se cumple solo.
3. Rentabilidad confirmada (sobre break-even — ver `/cod-ops:rentabilidad`).

### Dos cadencias — elegir según el contexto, no mezclar a medias
- **Agresiva (estándar del squad):** gate de **72h** consecutivas sobre target → **+20% cada 24h** mientras aguante. Usar cuando hay caja para absorber ruido y el producto/cuenta ya tiene historial.
- **Conservadora:** gate de **5 días** de ángulo estable → **+20% cada 3-4 días**. Usar con cuenta nueva, producto recién lanzado, o cuando se prefiere dar más margen a que Meta estabilice el aprendizaje antes de cada salto.

Acción de salto: **+20%** (ambas cadencias). **+100% (duplicar)** si el ROAS real es el doble del Target, en cualquiera de las dos.

> **Importante — no editar el anuncio ganador para subirle presupuesto.** Cualquier cambio directo (hasta el presupuesto) reinicia su fase de aprendizaje en Meta. Se **duplica** el conjunto ganador con el presupuesto nuevo y se deja el original intacto corriendo al lado — nunca se edita en caliente.

> **Definición del gate (ambas cadencias):** son horas/días *consecutivos de desempeño* sobre el Target, evaluados 1 vez/día — NO una ventana móvil por hora, ni un cronómetro desde el último cambio/publicación. Están ancladas a la racha de rendimiento (ruido intradía de Meta + fase de aprendizaje). El gate es la **puerta de entrada**: una vez dentro, subes en la cadencia elegida mientras aguante, sin re-esperar el gate por cada subida. Para desescalar, igual: mismo gate en rojo antes del −20%.

## Protocolo de DESESCALADO (esperar el mismo gate elegido arriba antes de tocar)
- Bajo target pero rentable → **−20%** en la misma cadencia (cada 24h si agresiva, cada 3-4 días si conservadora) hasta el mínimo de gasto diario.
- Sobre break-even (perdiendo) → −20% y revisar embudo.
- Ya en el mínimo → no bajar más: creativos nuevos, auditar funnel.

## Apagar — con paciencia
- **NO apagar** anuncios que no gastan (muchos arrancan semanas después).
- **NO apagar** adsets de CPA alto con **tráfico frío** (sostienen retargeting).
- **Apagar solo** con bajo gasto + CPA no rentable durante **3–7 días**.

## CBO vs ABO

Este protocolo asume **CBO** (presupuesto a nivel campaña, Meta reparte solo). Si la cuenta corre **ABO** (presupuesto fijado por adset), detectarlo primero en `ads_get_ad_entities`: si `daily_budget` aparece a nivel campaña → CBO; si aparece a nivel adset → ABO.

Bajo ABO el protocolo cambia:
- El CPA se evalúa **por adset**, no se promedia a nivel cuenta/campaña — cada adset tiene presupuesto independiente.
- Las reglas de 72h / +20% / −20% se aplican **adset por adset**, cada uno con su propia racha.
- No hay auto-balanceo: si no mueves tú el presupuesto, un adset que rinde mal sigue gastando igual — más carga operativa, Meta no le quita dinero solo.
- El 90/10 (creativos vs presupuesto) sigue aplicando, pero subir al ganador no resta automáticamente del perdedor — hay que bajar el perdedor a mano mientras subes el ganador.

Si la cuenta mezcla CBO y ABO, tratar cada campaña según su tipo detectado, no asumir uno solo para toda la cuenta.

## Montar la campaña por API (Meta Ads MCP) — lecciones de campo (2026-10-09)

El conector trabaja en **modo borrador**: todo lo que se crea o edita (incluida una pausa) queda staged hasta publicar. Una pausa en borrador **no** apaga lo que está en vivo; para frenar gasto ya, el usuario lo apaga en el Administrador o se publica la pausa.

**Orden que funciona:**
1. `ads_create_campaign` (Ventas, CBO con `campaign_daily_budget` en la unidad mínima de la moneda; COP 90000 = $90.000/día, `LOWEST_COST_WITHOUT_CAP`).
2. `ads_create_ad_set` × N (OPEN 1..N): `optimization_goal=OFFSITE_CONVERSIONS`, `billing_event=IMPRESSIONS`, `destination_type=WEBSITE`, `promoted_object={"pixel_id":…,"custom_event_type":"PURCHASE"}` **sin product_set_id**, targeting país + edad (Advantage+ la vuelve sugerencia). Sin `start_time` → arranca al publicar.
3. Creativos: `ads_create_creative` con `object_story_spec` (video_data con `image_hash` de miniatura, o link_data con `image_hash`) + `instagram_user_id` + **todas las funciones de `degrees_of_freedom_spec` en OPT_OUT**. No pasar `image_url` y `image_hash` a la vez (ObjectStorySpecRedundant). Un creativo inline sin DOF activa funciones de catálogo.
4. `ads_create_ad` con `{"creative_id":…}`. Revisar que `active_errors` venga vacío.
5. Verificar el borrador (`ads_get_ad_entities` con `object_state=draft`) y la vista previa (`ads_get_ad_preview`) de cada anuncio.
6. **Publicar por API** con `ads_activate_entity` pasando `object_ids` = campaña + conjuntos + anuncios y `publish_as_active=true`, con confirmación explícita del usuario. Devuelve `PUBLISHING` (entregado, no "en vivo"): unos minutos después, confirmar estados en vivo y la vista previa real.

**⚠️ Trampa del catálogo (cuentas con catálogo ligado al píxel):** si el usuario **abre el borrador en el editor del Administrador de anuncios**, Meta reescribe la campaña sola: pone `promoted_object.product_catalog_id` en la campaña, cambia los conjuntos a **LINK_CLICKS** con atribución de 1 día y `product_set_id`, y convierte los anuncios en plantilla de catálogo (`template_data {{product.name}}`, carrusel o colección). La vista previa muestra **otros productos de la tienda**. Lo mismo pasa al publicar desde el editor (`smart_promotion_type=GUIDED_CREATION`).
- **Prevención:** crear y publicar todo por API; pedirle al usuario que no abra los anuncios en modo edición (ver métricas o usar el interruptor no tiene riesgo).
- **Reparación:** los creativos son inmutables, así que `ads_update_entity` no sirve sobre el creativo. Hay que marcar los anuncios convertidos como `status=DELETED`, crear anuncios nuevos con el `creative_id` original, devolver los conjuntos a `OFFSITE_CONVERSIONS + IMPRESSIONS + promoted_object (píxel/PURCHASE) + atribución 7d clic/1d vista`, poner `promoted_object={}` en la campaña y publicar por API.
- Una campaña ya publicada con `GUIDED_CREATION` no se deja limpiar: sus anuncios nuevos piden "Missing Product Set". La salida es **una campaña nueva** creada por API.

**Permisos de Claude Code:** crear campañas, conjuntos y anuncios y publicarlos requiere reglas de permitir para `ads_create_campaign`, `ads_create_ad_set`, `ads_create_ad`, `ads_update_entity` y `ads_activate_entity`. El usuario las agrega con `/permissions`; el agente no se da permisos a sí mismo.

**Analizar una campaña activa (orden):** serie mensual de la campaña (`time_increment=monthly`, `date_preset=maximum`) → diaria desde la última reactivación → conjuntos y anuncios con su configuración → cortes `publisher_platform×platform_position` y `age×gender` → cruzar con la contabilidad (`data.json`: despacho, entrega, utilidad por pedido = break-even real). Separar siempre si el costo sube por **CPM** (subasta/temporada) o por **conversión** (creativo/landing).

## Fase RECON — validar creativos antes de escalar (2026-10-15)
Antes de meter un producto o una ronda nueva a la One CBO, se valida con RECON:
- **Matriz:** 4 ángulos base (dolor, identidad, oportunidad y autoridad) × ganchos (solo cambian los primeros 3 s), con la misma audiencia. Un anuncio por conjunto OPEN.
- **Gasto parejo** (la CBO lo concentra en 1–2 anuncios y el resto queda sin datos):
  - **Entrega push del anuncio:** a nivel de anuncio, en la sección "anuncios multianunciante", hay un interruptor que reserva un % del presupuesto diario por 1–30 días. No sale en todas las cuentas, y con muchos anuncios a la vez puede no cumplir el mínimo.
  - Si no está disponible, la fase RECON corre en **ABO** con el mismo presupuesto por conjunto.
- **Lectura:** de 5 a 7 días, con unas 2–3 compras por celda (≈ 2–3 × CPA objetivo por celda en la semana). Si el presupuesto no alcanza, primero 4 ángulos × 1 gancho y después los ganchos del ángulo ganador.
- **Salida:** la combinación ángulo + gancho con mejor CPA se pasa a la One CBO y se multiplica en formatos (catálogo `ads-invest/FORMATOS.md`). Las piezas TOFU educativas no se apagan aunque su CPA sea más alto, porque sostienen al resto.

## Volumen creativo (la verdadera optimización)
- Mínimo **15 creativos únicos/semana**; 6 hooks + 6 formatos por ganador.
- Video **4:5** + ~30% imágenes. Todos los ángulos y retargeting dentro del **mismo One CBO**.
- La cuota semanal es el mínimo. La frequency alta solo adelanta la rotación de un ganador si viene acompañada de CPA subiendo — si sigue vendiendo bien con CPA sano, se deja correr y se rota en el corte semanal normal, no antes.

> Fuente: notebook "Protocolo de Escalado y Optimización One CBO en Meta Ads" (consultar vía NotebookLM MCP si se necesita el detalle textual).
