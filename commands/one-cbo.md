---
description: Protocolo Meta Ads One CBO — madre + FLEX + laboratorio, escalado vertical por umbrales de CPA, ráfaga y corte, montaje por API, bug ROAS USD/COP
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

**Ticket promedio con el bug activo:** `average_purchases_conversion_value ÷ tasa_USDCOP` (~4.000) da una aproximación del precio de venta promedio en COP. Sirve para fijar la meta de CPA cuando no se conoce el precio, pero hay que confirmarlo con el dueño.

### Meta de CPA rápida
Si el dueño no da otra meta: **CPA objetivo = 20 % del precio de venta** (regla usada en las tiendas del autor desde oct-2026). Siempre se comprueba que quede por debajo del break-even de `/cod-ops:rentabilidad`. Si el break-even es menor, manda el break-even.

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

## Estructura que usan las cuentas que más venden (oct-2026)
Patrón observado en las 3 cuentas COD de Colombia con más gasto entre las revisadas (la mayor: ~$157 M/mes y ~5.300 compras en un solo producto). Detalle y números en `docs/referentes-escalado.md`.
- **Campaña madre permanente (CBO, máximo volumen):** la ganadora no se apaga ni se relanza. Se alimenta con creativos "graduados" de un laboratorio aparte. Hay madres de 6–8 meses con CPA estable.
- **2 conjuntos abiertos por campaña** (país, 21–65, Advantage+ Audience):
  - **FLEX:** formato flexible, un anuncio con varios videos o imágenes, y Meta elige cuál mostrar.
  - **Anuncios normales:** 1–3 anuncios. Opcional: un conjunto "FLEX imágenes" y un LAL 3 %.
- **Laboratorio de creativos:** campañas chicas ("LAB/PRUEBAS DE CREATIVOS", ABO o CBO baja). Lo que gana pasa a la madre.
- **Creativo:** un copy fijo y solo rota el video o la imagen. El copy es un testimonio largo: dolor → lo que ya intentó → beneficios → envío gratis + contraentrega + urgencia. El título es prueba social ("+20.000 unidades vendidas ⭐", "4,5 de 5 ⭐"). Los ganadores son casi siempre video (CTR 4–9 %). Los claims siguen las reglas de cada producto; no se copian promesas de salud.
- **Atribución:** algunas cuentas suman 1 d vista + video con interacción a los 7 d clic, y eso baja el CPA reportado. Antes de comparar CPAs entre cuentas, revisar `attribution_spec` del conjunto.

## Protocolo de ESCALADO VERTICAL (presupuesto de la campaña)
Condiciones previas, siempre:
1. Rentabilidad confirmada: target y break-even vienen de `targets.por_producto` (ver `/cod-ops:rentabilidad`).
2. Gate de entrega COD ≥ `gate_entrega_pct`.
3. **>70 %** de las compras por atribución de clic.

La métrica es el **CPA frente al Target**. El régimen depende del **volumen de la campaña**:

| Volumen de la campaña | Ventana de CPA | Cuándo se revisa |
|---|---|---|
| **< 20 compras/día** (lanzamiento, tienda chica) | CPA de las últimas 24–48 h | 1 vez al día, al mediodía |
| **≥ 20–30 compras/día** (producto estable) | CPA acumulado **del día** (desde las 00 h) | 2–3 veces al día, entre las 8 h y las 18 h. Nunca antes de las 8–9 h: la mañana sale inflada y luego se corrige |

| CPA frente al Target | Acción |
|---|---|
| **≤ 0,85 × Target** con ≥ 4–5 compras en la ventana | **Subir.** Régimen bajo: ×1,5–2. Régimen alto: ×1,5–5 de una vez, hasta 3 subidas el mismo día |
| 0,85 – 1,05 × Target | Mantener |
| **≥ 1,15 × Target** | **Bajar 30–60 %** |
| Día malo en la ganadora | **No apagarla.** Estacionarla en un piso (régimen alto: ~30–40 % de su presupuesto pico; régimen bajo: el presupuesto de arranque) y volver a subirla cuando el CPA se recupere |

- **El presupuesto es un techo:** Meta gasta el 60–80 % de lo asignado. Se pone alto para que pueda gastar si encuentra compradores.
- **Punto de saturación:** cada campaña tiene un gasto/día a partir del cual el CPA se dispara. En el referente: sostenible a 1,2–1,6 M/día; a 3,66 M el CPA subió +20 %. Cuando se toca dos veces, no se sigue subiendo esa campaña: se escala en horizontal (abajo).
- **Editar o duplicar:** con volumen alto los referentes editan el presupuesto de la CBO en caliente, varias veces al día, sin perder la entrega. Con volumen bajo (< 50 compras/semana) un cambio grande puede devolver la campaña a aprendizaje; ahí se prefiere un salto moderado (×1,5) o duplicar.
- **Tope de puja (bid cap):** solo con CPA estable. Tope ≈ Target, presupuesto alto como techo y unos 10 videos. En el referente dio el mejor CPA de la cuenta. El cost cap fracasó (CPA 2,6–4 × Target).

## Protocolo de ESCALADO HORIZONTAL (ráfaga de duplicados)
Para crecer más allá del punto de saturación de una campaña. **Solo con un producto probado:** la madre lleva 3 días seguidos con CPA ≤ Target.
- **Por qué funciona:** cada duplicado entra a la subasta con usuarios y aprendizaje distintos. Rinden muy diferente aunque sean iguales. Lanzar varios es comprar boletos para encontrar 1 o 2 que aguanten mucho presupuesto.
- **Referente:** ~30 duplicados a $60k/día en 5 días (mismo copy, distinto video o combinación). Corte masivo a los 6–8 días. Sobrevivieron 2–3 (≈ 7 %). Después no lanzaron más y solo escalaron las sobrevivientes.
- **Versión estándar (caja limitada):**
  - Ráfaga: 3 duplicados al día durante 2 días, a 2–3 × Target cada uno.
  - Reserva: un "presupuesto de boletos" de unos 30 × Target.
  - Nombres: `DD-MM-AAAA PRODUCTO (variante) N`.
- **Corte, a los 3–8 días:**
  - Apagar si el CPA ≥ 1,2 × Target, **aunque ya haya gastado mucho** (el referente apagó una campaña con 190 × Target gastado y CPA de 1,2 × Target).
  - Apagar si lleva 0 compras con 1,5 × Target gastado.
- **Sobreviven** las que quedan con CPA ≤ Target. Entran al escalado vertical y se suman a la madre.

## Protocolo anterior (+20 %) — solo como alternativa conservadora
Si no hay caja para absorber variación, se puede usar la regla clásica en vez del vertical por umbrales.

### Dos cadencias — elegir según el contexto, no mezclar a medias
- **Agresiva (estándar del squad):** gate de **72h** consecutivas sobre target → **+20% cada 24h** mientras aguante. Usar cuando hay caja para absorber ruido y el producto/cuenta ya tiene historial.
- **Conservadora:** gate de **5 días** de ángulo estable → **+20% cada 3-4 días**. Usar con cuenta nueva, producto recién lanzado, o cuando se prefiere dar más margen a que Meta estabilice el aprendizaje antes de cada salto.

Acción de salto: **+20%** (ambas cadencias). **+100% (duplicar)** si el ROAS real es el doble del Target, en cualquiera de las dos.

> **Con volumen bajo, no editar el conjunto ganador para subirle presupuesto.** Un cambio grande puede reiniciar su fase de aprendizaje. Se **duplica** el conjunto ganador con el presupuesto nuevo y el original sigue corriendo intacto al lado. Con volumen alto (≥ 20–30 compras/día) aplica el escalado vertical de arriba: se edita la CBO en caliente.

> **Definición del gate (ambas cadencias):** son horas/días *consecutivos de desempeño* sobre el Target, evaluados 1 vez/día — NO una ventana móvil por hora, ni un cronómetro desde el último cambio/publicación. Están ancladas a la racha de rendimiento (ruido intradía de Meta + fase de aprendizaje). El gate es la **puerta de entrada**: una vez dentro, subes en la cadencia elegida mientras aguante, sin re-esperar el gate por cada subida. Para desescalar, igual: mismo gate en rojo antes del −20%.

## Protocolo de DESESCALADO (esperar el mismo gate elegido arriba antes de tocar)
- Bajo target pero rentable → **−20%** en la misma cadencia (cada 24h si agresiva, cada 3-4 días si conservadora) hasta el mínimo de gasto diario.
- Sobre break-even (perdiendo) → −20% y revisar embudo.
- Ya en el mínimo → no bajar más: creativos nuevos, auditar funnel.

## Apagar — con paciencia (anuncios dentro de la madre)
> Las **campañas duplicadas de una ráfaga** se cortan con su propia regla, más dura: CPA ≥ 1,2 × Target a los 3–8 días (ver escalado horizontal). La **madre** nunca se apaga; se deja en un piso.
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

El conector trabaja en **modo borrador**. Lo que se crea y casi todo lo que se edita queda en borrador hasta publicarlo (actualizado el 27-oct-2026):
- **Pausa sola** (`ads_update_entity` con `fields={"status":"PAUSED"}` y nada más) sobre algo ya publicado: se aplica **en vivo** y devuelve `is_draft=false`. Después **no** llamar a `ads_activate_entity`, porque puede deshacer la pausa. Se verifica con `ads_get_ad_entities`.
- **Cambio de presupuesto** (o una pausa junto con otros campos): queda en borrador (`is_draft=true`). Se publica con `ads_activate_entity` pasando solo ese objeto en `object_ids` y `publish_as_active=false`.
- **Presupuestos en COP:** van en pesos enteros (`daily_budget=60000` = $60.000/día).
- ⚠️ **No todas las cuentas tienen el modo borrador.** Si la respuesta trae `is_draft=false` junto con `status_forced_to_paused=true` en un cambio de presupuesto, Meta **pausó la campaña en vivo**. Hay que reactivarla en el mismo turno con `ads_activate_entity` y verificar con `ads_get_ad_entities` (29-oct-2026).
- **Arranque programado:** poner `start_time` en el conjunto (p. ej. `2026-10-28T05:00:00-0500`). Así se publica de noche y empieza a gastar a las 5 am.

**Orden que funciona:**
1. `ads_create_campaign` (Ventas, CBO con `campaign_daily_budget` en la unidad mínima de la moneda; COP 90000 = $90.000/día, `LOWEST_COST_WITHOUT_CAP`).
2. `ads_create_ad_set` × N (OPEN 1..N): `optimization_goal=OFFSITE_CONVERSIONS`, `billing_event=IMPRESSIONS`, `destination_type=WEBSITE`, `promoted_object={"pixel_id":…,"custom_event_type":"PURCHASE"}` **sin product_set_id**, targeting país + edad (Advantage+ la vuelve sugerencia). Sin `start_time` → arranca al publicar.
3. Creativos: `ads_create_creative` con `object_story_spec` (video_data con `image_hash` de miniatura, o link_data con `image_hash`) + `instagram_user_id` + **todas las funciones de `degrees_of_freedom_spec` en OPT_OUT**. No pasar `image_url` y `image_hash` a la vez (ObjectStorySpecRedundant). Un creativo inline sin DOF activa funciones de catálogo.
   - **Estáticos con 2 tamaños:** usar `placement_customizations`. La imagen 4:5 es la base (feed). La 9:16 va en historias y reels de Facebook e Instagram (`facebook_positions: story, facebook_reels`; `instagram_positions: story, reels`).
   - **Imágenes desde el CDN de Shopify:** a veces Meta no logra descargarlas (`ads_creative_upload_media` falla). Reintentar con y sin el parámetro `?v=` de la URL.
   - **Videos desde Shopify Files:** después de `stagedUploadsCreate` (resource FILE), el `fileCreate` de un mp4 va con `contentType: FILE`. Con `VIDEO`, Shopify responde "Invalid video url". La URL del `GenericFile` (cdn.shopify.com) sirve directo para `ads_creative_upload_media` con `media_type=VIDEO`.
   - **Lista de funciones DOF en OPT_OUT:** `image_touchups`, `text_optimizations`, `adapt_to_placement`, `image_templates`, `image_uncrop`, `enhance_cta`, `product_extensions`, `site_extensions`, `video_auto_crop`.
4. `ads_create_ad` con `{"creative_id":…}`. Revisar que `active_errors` venga vacío.
   - **Pasar un ganador a la madre:** crear un anuncio nuevo en la madre con el **mismo `creative_id`** del ganador. Se conservan el contenido y el UTM originales; las métricas del anuncio nuevo arrancan en cero.
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
