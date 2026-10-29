---
name: ads-invest
description: Investiga anuncios de competidores en la Meta Ad Library para productos de e-commerce y produce bancos de creativos, ángulos, ofertas y matrices de testeo listas para cargar en Meta. Úsala SIEMPRE que el usuario pida investigar competidores, buscar anuncios ganadores, analizar la biblioteca de anuncios / Ad Library, traer creativos de referencia, armar inspiración para campañas, decidir qué creativos testear, o continuar/siguiente ronda de investigación de un producto. Actívala aunque no diga "Ad Library" si habla de espiar competencia publicitaria, swipe file, anuncios que escalan, o cargar creativos para testear.
---

# Investigación de creativos y competidores (Meta Ad Library)

Esta skill captura el método para investigar publicidad de competidores y convertirla en material accionable: bancos de creativos de referencia, bancos de ángulos/ganchos, bancos de oferta y matrices de testeo para cargar campañas en Meta. **Toda investigación termina en la INVESTIGACIÓN CREATIVA COMPLETA (Regla 4)**: público, dolores, niveles de conciencia, ángulos, estructura de landing, oferta, claims, competidores, copy, testeo, economía y todos los links, en un solo Artifact.

> **Primer paso:** lee `tienda.config.json` (`tienda` + `creativos`). Los marcadores `{…}` de esta skill salen de ahí:
> - `{CARPETA_CREATIVOS}` = `creativos.carpeta`
> - `{CARPETA_TIENDA}` = la carpeta del proyecto de la tienda
> - `{PIXEL_ID}` = `creativos.pixel_id`
> - `{SHOPIFY_SHOP}` = `tienda.shopify_domain` (sin `.myshopify.com`)
> - `{DOMINIO}` = `tienda.shopify_public`
> - `{ARTIFACT_REFERENCIA}` = `creativos.artifact_referencia`
>
> Si falta la sección `creativos`, corre `/cod-ops:setup-tienda` o pídele los datos al dueño.

> ⚙️ **CONFIGURACIÓN ACTIVA:**
> - Carpeta de trabajo: `{CARPETA_CREATIVOS}`
> - Marca: `tienda.nombre`
> - País principal: `Colombia` (también investigar global cuando sea relevante — pago contra entrega es la palanca #1 en Colombia)
> - Descargas de creativos: las hace Claude directo a `<producto>/media/` (ya no se pide el swipe). Carpeta del swipe, solo si se usa: `~/Downloads/ad-library`

## Carpeta de trabajo POR DEFECTO: `{CARPETA_CREATIVOS}`

Todo el output va aquí salvo que el usuario indique otra ruta. Estructura recomendada (un documento por tipo y por producto; cada ronda se AÑADE, no se crean archivos por ronda):
```
{CARPETA_CREATIVOS}/
├── INICIO.md                       ← índice maestro del vault (Obsidian)
├── REGISTRO-INVESTIGACION.md       ← índice maestro de cobertura (leer SIEMPRE primero)
├── <producto-1>\
│   ├── PRODUCTO.md                 ← ⭐ ficha VERIFICADA del producto (specs, mecanismo, claims sí/no, precio, economía)
│   ├── COPY.md                     ← copy completo de cada anuncio
│   ├── BANCO-ANGULOS.md            ← ⭐ ángulos + ofertas + plan de testeo
│   ├── RANKING.md                  ← competidores ordenados mejor→peor
│   ├── ANALISIS-BIBLIOTECAS.md     ← por competidor: qué copiar / qué ignorar
│   ├── INDEX-CREATIVOS.md          ← ficha de cada creativo descargado
│   └── media\                      ← archivos .mp4 / .jpg descargados
└── <producto-2>\ ...
```
Si la carpeta no existe, créala. No pidas confirmación de la ruta; es la predeterminada.
Conecta los documentos con wikilinks `[[ ]]` de Obsidian y enlázalos desde `INICIO.md`.

## ⭐ REGLA 0 — Verificar el producto REAL antes de buscar (no negociable)

Nunca investigues sobre un producto supuesto. En la primera ronda se perdió una investigación entera por asumir "plantilla de comodidad" cuando el producto real era una plantilla correctora de 3/4 en TPR.

1. Consigue la fuente del producto: link de Shopify, carpeta de Drive o fotos del usuario.
2. **Si es una carpeta de Drive y la API no lista archivos**, lístala en el navegador y descarga sin navegador (`drive.usercontent.google.com/download?id=<id>&export=download&confirm=t`); los .docx se leen con `unzip -p f.docx word/document.xml`. Detalle: [references/tecnico-busqueda.md](references/tecnico-busqueda.md). Revisa todos los videos del proveedor: alguno puede traer otra marca en la caja.
2b. **¿El nombre comercial ya está tomado?** Antes de bautizar el producto, busca el nombre en Meta/TikTok/Google: si en el mercado ya significa otro producto, el anuncio y la landing confunden (marcadores: "marcadores mágicos" en LATAM = los que cambian de color, Kiut/Bloopys → se usó "Marcadores Mágicos **de Figuras**"). Anótalo en `PRODUCTO.md`.
3. Escribe `PRODUCTO.md` con: formato, material, tallas o presentaciones, mecanismo, lo que promete el proveedor, la tabla de **claims ❌ no / ✅ sí**, el lenguaje visual del proveedor (qué foto sirve para qué) y el precio y costo si se conocen.
4. **No marques a nadie como "gemelo" sin verificarlo visualmente** (miniatura del creativo contra las fotos del producto). Si no hay gemelo, dilo explícitamente.
5. Si no puedes ver el producto, **pregunta antes de buscar**. No supongas.

## ⭐ REGLA 0d — Mercado local: ¿quién lo vende ya en Colombia y a qué precio? (siempre, antes de fijar la oferta)

La escalera de packs se decide contra lo que el cliente puede encontrar en su país. En la crema masmelo, la oferta se iba a fijar en $46.600 por unidad sin saber que Mercado Libre la vende a $29.500–$49.900.

1. **Mercado Libre Colombia** (Playwright): `https://listado.mercadolibre.com.co/<terminos-con-guiones>` con el nombre del producto, el nombre del listing y el nombre local ("crema masmelo"). Extrae `li.ui-search-layout__item, div.poly-card` → título, precio (`.andes-money-amount__fraction`), vendedor y si es envío del exterior. Ignora los `click1.mercadolibre.com.co` (son publicidad de otros productos).
2. **Lo que le llega desde el exterior** (lo que el cliente colombiano compara de verdad):
   - **Amazon con envío a Colombia**: busca en amazon.com con la ubicación fijada en Colombia y anota el precio en USD + envío + depósito de importación, y el total en COP. Si sale "no se envía a Colombia", anótalo: es una ventaja.
   - **AliExpress, Temu y Shein** con destino Colombia: precio en COP y días de entrega.
   - **Mercado Libre "envío del exterior"**: suele ser el piso de precio.
3. **Retail local:** Falabella, Éxito, Farmatodo y Cruz Verde (si es salud o belleza), y **TikTok CO** (mayoristas y tiendas, con `locationCreated:"CO"`).
4. **Meta Ad Library CO** (Regla 1b): quién lo pauta y con qué oferta.
5. Escribe en `PRODUCTO.md` una tabla **"Mercado local"**: canal · vendedor · precio por unidad · packs · envío (días, desde dónde) · link. Anota el precio mínimo, el típico y el máximo **puesto en Colombia** (con envío e impuestos).
6. **Regla de precio:** si el precio por unidad del pack principal queda más de un 30–40 % por encima del típico de Mercado Libre, la landing tiene que justificarlo (experiencia, pago contra entrega, envío gratis, regalo, bundle). Si no, baja el precio o cambia el producto. Dilo en la sección "Oferta" del Artifact.
7. La economía se calcula con el costo que da el usuario. **Nunca propongas un pack sin costo real**; si no lo hay, pregúntalo antes de cerrar la oferta.

## ⭐ REGLA 0e — Landings que venden el producto en EE. UU. y el extranjero (siempre)

Además de los anuncios, **analiza las páginas de producto** de las tiendas extranjeras que venden el mismo formato (Amazon, Shopify DTC, Ulta, Superdrug, TikTok Shop). Son la referencia de landing, no Mercado Libre.
1. Encuéntralas con WebSearch (indexa EE. UU.): `"<nombre del listing>" shop`, `<formato> body lotion buy`, y con los dominios de los anuncios de Meta ALL.
2. Ábrelas en Playwright a 390 px, toma una captura de página completa y extrae: titular, subtítulo, orden de los bloques, precio y packs, prueba social (reseñas y estrellas), garantía, FAQ, uso de GIF o video, y CTA.
3. Escribe `LANDINGS.md`: una ficha por tienda (✅ copiar / ❌ ignorar) y una **estructura recomendada** que mezcle lo mejor de todas. Esa estructura alimenta la sección 6 del Artifact y la skill `landing-cod`.

## ⭐ REGLA 0b — Cazar GEMELOS EXACTOS fuera de Meta (AliExpress → TikTok), siempre

El usuario quiere **replicar creativos ya mismo**, y eso solo sirve con el producto idéntico. Meta muchas veces no tiene gemelos activos; TikTok y AliExpress sí. Hazlo en toda investigación, después de la Regla 0:

1. **AliExpress primero (identificar el SKU white-label):** en el navegador, `https://www.aliexpress.com/w/wholesale-<terminos>.html?SearchText=<terminos en inglés>`. Haz scroll y extrae `a[href*="/item/"]` con su imagen. Arma la hoja de miniaturas y compárala con las fotos del producto. Abre la ficha del candidato y **confirma material, tallas y forma** (el texto de la ficha + una screenshot). Anota en `PRODUCTO.md`: nombre exacto del listing, vendedor, link, precio y la fábrica si aparece. **Ese nombre exacto es la llave para buscar gemelos.**
2. **TikTok (sin login):** `https://www.tiktok.com/search/video?q=<termino>`. Haz scroll lento (`mouse.wheel` 700 px × 8) para que carguen las miniaturas. Extrae `a[href*="/video/"]` + img + likes. Usa el nombre del listing de AliExpress, sus variantes en inglés y los términos del problema en ES/EN/PT. Arma la hoja de miniaturas → verificación visual.
3. **Detalle de cada gemelo:** abre el video y lee `script#__UNIVERSAL_DATA_FOR_REHYDRATION__` → `__DEFAULT_SCOPE__['webapp.video-detail'].itemInfo.itemStruct`: `desc`, `createTime`, `stats.playCount/diggCount/shareCount`, `author.uniqueId`, **`isAd`** (true = anuncio pagado = señal de que vende).
   - **Anuncios de TikTok Shop:** no traen `playAddr` (el video es `blob:`) y no se ven fuera de la app → márcalos **"probable (TikTok Shop)"** y pide al usuario verificarlos en el celular.
4. **TikTok Creative Center (Top Ads)** como complemento (login por QR + código al correo, API `top_ads/v2/list`): ver [references/tecnico-busqueda.md](references/tecnico-busqueda.md).
5. **Entrega** en el chat y en `LINKS.md` (sección "GEMELOS EXACTOS"): cuenta, si es orgánico o anuncio, video, reproducciones/likes/compartidos/fecha y link. Más el link del listing de AliExpress (su galería son creativos del proveedor reutilizables). Lista también los descartados por visual.
6. Si tampoco hay gemelos en TikTok, dilo, y recomienda los creativos del proveedor (Drive o AliExpress) como la vía más rápida para replicar.
7. **Descarga SIEMPRE los videos** de gemelos y referencias top a `<producto>/media/ref_<plataforma>_<cuenta>_<tipo>.mp4`. No esperes a que el usuario lo pida. Y **verifica el producto viendo fotogramas del video descargado**: la descripción engaña (un "heel cup" resultó ser otra plantilla).
   - **TikTok:** `playAddr` + cookie `tt_chain_token` → curl. **Meta:** `video.src` vía TreeWalker → curl el mismo día (caduca). Comandos exactos en [references/tecnico-busqueda.md](references/tecnico-busqueda.md). Nunca fetch + `<a download>` (cierra el navegador).
   - ⚠️ Deja claro al usuario que los videos de terceros son **referencia**, no para pautar tal cual (derechos de autor y rechazo). Excepción: los de la fábrica o el proveedor.
   - **Material de fábrica para el b-roll:** el video de la galería del listing de AliExpress del SKU exacto suele traer tomas limpias (niños usando el producto, detalles, macro). Ábrelo en Playwright y lee `document.querySelectorAll('video')` → `src` → curl. **Verifica la versión con fotogramas**: en el taladro, 7 de 9 listings "iguales" eran otra versión (otro maletín, otro taladro) y uno traía la marca HAPTIME estampada. Recórtalo a 9:16 por fuera del texto chino. Si el mismo plano aparece en cuentas de creadores o de competidores (con su marca de agua o subtítulos), no es material de fábrica.
   - Documenta cada archivo en `INDEX-CREATIVOS.md` (qué es, si es gemelo o similar, qué tomar).

## ⭐ REGLA 4b — Elegir FORMATOS con el catálogo del dueño (siempre, al cerrar la investigación)

**El formato lo elige la investigación, no la costumbre.** el dueño lo corrigió el 2026-10-19: Postura360 y el irrigador salieron con la misma parrilla de 16 estáticos aunque la investigación mostraba otros ganadores (primera vez, reverso, unboxing y disculpa). Procedimiento obligatorio en [references/seleccion-formatos.md](references/seleccion-formatos.md):
0. **Descubrir formatos nuevos** (radar en cada ronda): los 10 anuncios más longevos de la categoría, los 5 TikTok top y 5 anuncios PROBADOS de otras categorías COD. Lo que no encaje en el catálogo y sea repetible se agrega a `FORMATOS.md` → "🆕 Formatos descubiertos", con referencia y muestra, y se le avisa al dueño.
1. **Etiquetar el formato** de cada referencia en `LINKS.md` (columna Formato) → tabla "Formatos del mercado" con puntos de evidencia.
2. **Puntuar el catálogo** para este producto: evidencia + encaje + nivel de conciencia + material − rotación ± historial de `ads-invest/REGISTRO-FORMATOS.md`.
3. **Reglas duras:** ≥ 50 % de los formatos con referencia real de la investigación · máximo 4 repetidos del producto anterior · un formato por ángulo · ≥ 3 familias por ángulo · el formato más fuerte del mercado va siempre · 1 comodín nuevo por ronda.
4. **`MATRIZ.md` con la columna "Por qué este formato"** (referencia y puntos) y la lista de descartados. Se le muestra al dueño antes de producir.
5. **Registrar** en `REGISTRO-FORMATOS.md` al publicar y completar el resultado en la lectura RECON.

Lee `{CARPETA_CREATIVOS}/FORMATOS.md` (el dueño lo va entrenando: formatos, etapa del embudo, cómo se producen y sus ⚠️). El plan de testeo del Artifact sale como **matriz ángulo × formato**: cada anuncio lleva un solo ángulo, y cada ángulo va en varios formatos (mínimo 3 ángulos × 4 formatos: video con voz, video sin voz, estático nativo y estático de argumento), con al menos una pieza TOFU que no se apaga aunque venda caro. Por cada celda: ángulo, formato, etapa, gancho y el material con el que se produce (fábrica, stock, voz, HTML). Cada guion sigue la estructura **gancho (0–3 s, en 3 capas: imagen, texto y voz; se rota el tipo de gancho) → cuerpo (agitar, mecanismo, prueba, objeción) → CTA (oferta real, riesgo cero, instrucción y tarjeta)**. Los anuncios se nombran `PRODUCTO_ANGULO_FORMATO_GANCHO_v`. El catálogo completo de formatos y la tabla "qué cambiar según la métrica" están en `FORMATOS.md`. La primera prueba sigue la **metodología RECON** de `FORMATOS.md`: 4 ángulos base (dolor, identidad, oportunidad y autoridad) × ganchos, con la misma audiencia, de 5 a 7 días y con gasto parejo (entrega push o ABO). Al ganador se lo pasa a la One CBO. Descarta los formatos que piden algo prohibido (video generado, reseñas que no existen, stock falso o cifras sin fuente) y dilo.

## ⭐ REGLA 5 — Si el usuario pide videos o imágenes propias para testear

**Material permitido (no negociable):** fotos y videos del proveedor + escenas generadas con Codex + **stock de Magnific** (ilimitado con el plan del dueño; solo para escenas de contexto, nunca donde la voz nombra el producto) + material grabado por el usuario + **video generado con IA** cuando haya herramienta conectada (aprobado por el dueño el 2026-10-15: claymation, esqueleto, 3D, avatar; ver `FORMATOS.md`; mientras no esté conectada, la celda va como "⏳ pendiente"). **Nunca** pautar ni usar como b-roll videos de competidores o creadores, aunque el usuario lo pida: son referencia de estructura. Alternativas: videos del proveedor con el guion de la referencia, grabar una unidad, o licenciar al creador.

Pipeline probado (Postura360, 2026-10-08): guion por referencia → voz OmniVoice → tiempos por palabra (whisper) → música propia → HyperFrames con estilo por video → escenas Codex fieles a la foto real → oferta en PNG → QA (incluido el **uso correcto** del producto en la escena) → entrega en `media/ronda-a-<marca>/` y subida por API con `/cod-ops:one-cbo`. Comandos, presets y plantillas: [references/produccion-creativos.md](references/produccion-creativos.md).

**Voces (desde 2026-10-23): un avatar, una voz.** Cada guion define su avatar (edad, región, personalidad, dónde se graba) y se escribe en estilo UGC de corrido; la voz se diseña en VoxCPM2 con acento y personalidad del avatar y se actúa frase por frase clonando esa voz base (el dueño: "muchísimo mejor"). OmniVoice queda de respaldo. Método completo: [references/voces-voxcpm2.md](references/voces-voxcpm2.md).

Pipeline sin escotilla (Marcadores, 2026-10-13): voz (hoy VoxCPM2 por avatar) → subtítulos PNG → b-roll de stock de Magnific + clips del proveedor + imágenes Codex → función `build` de ffmpeg → mostrar al dueño → Shopify Files → Meta por API. Función lista para copiar, QA y subida paso a paso: [references/montaje-ffmpeg.md](references/montaje-ffmpeg.md).

**Trasplantes (2026-10-29):** cuando un video de la competencia escala, se rehace plano por plano con material propio. Se pueden usar los clips de fábrica que confirme el dueño y la voz clonada solo con autorización escrita, que queda en `FICHAS.md`. Nunca se usa el creador ajeno. Pasos en [references/trasplantes.md](references/trasplantes.md).

**Clips con IA vía Magnific Spaces (2026-10-23):** el dueño tiene modelos ilimitados en la app, pero no por el MCP. Claude arma el Space (imagen inicial de Codex fiel al producto + prompt + Kling 2.5 9:16 + conexión al primer fotograma) y **el dueño genera a mano**. Pasos en [references/video-ia-spaces.md](references/video-ia-spaces.md). Primer Space: "Masajeador de cabeza · videos RECON".

**⭐ Todo anuncio explica el producto (el dueño, 2026-10-23: "hay varios anuncios que son 0 explicativos").** En la RECON del masajeador solo se salvaron la demostración en video y unos 3 estáticos. Cada pieza lleva:
- el producto visible;
- una línea de mecanismo;
- el beneficio.

En video, la demostración va en los primeros 3–5 s. Antes de mostrar, haz la prueba de los 2 segundos: ¿se entiende qué vende y qué hace? Estáticos compuestos en Playwright con `document.write` + servidor local: ver [references/produccion-creativos.md](references/produccion-creativos.md) § 8b (incluye las correcciones del dueño a los formatos nativos y al encuadre). Publicación de la RECON por API (presupuesto por conjunto, estáticos 4:5 + 9:16 en un anuncio): [references/montaje-ffmpeg.md](references/montaje-ffmpeg.md) § Subida.

La **landing** del producto (packshot, 7 piezas, GIFs, Shopify, packs Releasit) es otra skill: `landing-cod`.

## ⭐ REGLA 1 — SIEMPRE entregar los links (no negociable)

**Toda ronda termina con links clicables en el chat, no solo en archivo.** El usuario los necesita para abrir los anuncios y ver los creativos. Nunca entregues solo nombres de marca, ganchos o análisis: sin link no sirve.

Se entregan **tres tipos de link, siempre los tres**:

1. **Anuncio individual** → `https://www.facebook.com/ads/library/?id=<ad_id>`
   Es el `ad_snapshot_url`. ⚠️ Meta ya NO aísla un anuncio con `?id=` solo: reescribe la URL a la biblioteca de la página. Para abrir un anuncio concreto, usa el link filtrado por frase (ver más abajo).
2. **Biblioteca completa del anunciante** → formato con TODOS los parámetros:
   `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=ALL&is_targeted_country=false&media_type=all&search_type=page&view_all_page_id=<page_id>`
   ⚠️ `view_all_page_id` funciona para páginas de MARCA/tienda, pero NO para páginas de PERSONA/advertorial (usan un ID de anunciante interno → devuelve "No hay ningún anuncio"). Para esas, usa el link filtrado por frase.
3. **Los videos descargados por ti** (ya no se pide el swipe, decisión del dueño del 2026-10-14). Bájalos tú mismo en la misma ronda, sin que el usuario exporte nada: Meta con el `video.src` de la Ad Library y TikTok con `playAddr` (ver "Descarga de creativos" más abajo y [references/tecnico-busqueda.md](references/tecnico-busqueda.md)). El link de exportar swipe solo se ofrece si hay que bajar una biblioteca entera de decenas de anuncios.

**Link filtrado por frase (abre un anuncio o grupo concreto):**
`https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=<CO|ALL>&is_targeted_country=false&media_type=<all|video|image>&search_type=keyword_unordered&q=<frase única del anuncio, sin tildes>`
El buscador de Meta ignora tildes. Una frase única del copy suele reducir de miles a 1–5 resultados.

Formato de entrega en el chat: agrupa por anunciante o por bloque (propios / directos / similares-por-ingrediente / referencia internacional), y para cada anuncio da **gancho + señal de longevidad + link individual**, y la ruta del video ya descargado. Si la lista pasa de ~25 links, además publica un Artifact con todo clicable y deja en el chat solo el top.

**Etiqueta siempre el nivel de evidencia.** No todos los "que funcionan" tienen la misma prueba:
- `PROBADO` — relanzado tras pausa, o +90 días entregando continuo.
- `INDICIO` — biblioteca grande o muchos ángulos, pero pocos días de vida.
- `SIN PROBAR` — lanzamiento reciente; se reporta para vigilar, no para copiar.

Nunca presentes un `INDICIO` como si fuera `PROBADO`.

## ⭐ REGLA 2 — NO repetir lo ya entregado

**Antes de cualquier búsqueda, lee `{CARPETA_CREATIVOS}/REGISTRO-INVESTIGACION.md`** y la sección `## 🔗 ANUNCIOS YA ENTREGADOS` del producto correspondiente.

El control es **a nivel de anuncio individual (`ad_id`)**, no solo de anunciante. Un mismo competidor puede volver a aparecer en rondas futuras con creativos nuevos: eso sí se reporta. Lo que nunca se repite es un `ad_id` ya entregado.

En cada ronda:
1. Omite todo `ad_id` que ya esté en el registro. Si el mejor anuncio de un competidor ya se entregó, busca el siguiente, no lo repitas.
2. Si un anunciante ya está cubierto pero tiene creativos nuevos desde la última ronda, repórtalos marcando el anunciante como "ya en registro, creativos nuevos".
3. Si una búsqueda entera solo devuelve material ya entregado, **dilo explícitamente** ("esta ronda no encontró nada nuevo en X") en vez de rellenar repitiendo.
4. Al terminar, **actualiza el registro** con: `ad_id`s entregados, page_ids, términos usados y pendientes.

Esto existe porque la investigación es incremental: cada ronda debe ampliar cobertura, no recalentar lo mismo.

### Formato obligatorio del registro de anuncios entregados

En `REGISTRO-INVESTIGACION.md`, bajo el producto, mantener esta tabla y **añadir una fila por cada anuncio entregado**:

```markdown
## 🔗 ANUNCIOS YA ENTREGADOS — <producto> (NO volver a reportar estos ad_id)

| ad_id | Anunciante | page_id | Gancho | Evidencia | Ronda |
|-------|-----------|---------|--------|-----------|-------|
| 2185579072255550 | EjemploCompetidor | 677045318828393 | COMIENZA HOY A CUIDAR TUS ARTICULACIONES | PROBADO 87d | R1 |
```

Y la lista de bibliotecas ya entregadas:

```markdown
### Bibliotecas (view_all_page_id) ya entregadas
- 677045318828393 EjemploCompetidor · 971140376079650 EjemploGlobalUS · ...
```

## ⭐ REGLA 0c — Si el producto YA está pautado, empieza por los datos propios

Antes de buscar fuera (mini bicicleta, 2026-10-09):
1. Saca de Meta la campaña activa: copy y título de cada creativo (`ads_get_creatives` con `creative_ids`), CPA por anuncio, y los cortes **edad×género** y **plataforma×ubicación** con `date_preset=maximum` y desde la última reactivación. Eso define el avatar real (ej. bicicleta: compra 35+, la mejor franja es 65+, la de 25–34 es la peor).
2. Saca de Shopify precio, compare_at y descripción (`graphql_query` con `title:*X*`). Si hay un **compare_at ficticio**, márcalo como riesgo SIC en `PRODUCTO.md`.
3. Saca la economía real de `{CARPETA_TIENDA}/contabilidad/data.json` → `meses.*.productos.<FAMILIA>` (ingreso, despacho, entrega, utilidad) para el break-even y el target CPA.
4. Lista qué **no** dicen los anuncios actuales: ahí suelen estar los ángulos nuevos (ej. la bicicleta es un **kit para armar** y ningún anuncio lo decía).

**Producto nuevo (sin historial):** estima el break-even por pedido con
`0,8 × [0,9 × (precio − costo − flete) − 0,1 × (flete + flete_devolución)]`
(80 % despacho, 90 % entrega; ajusta las tasas si la familia tiene datos). Marcadores pack ×2 ($89.900, costo $24.000, flete $15.500) ≈ $33.800. Target CPA ≈ 55–60 % del break-even. Al lanzar, la familia se da de alta en `tienda.config.json` con `/cod-ops:setup-tienda`.

## Lecciones de campo (rondas reales)
- **El nombre en inglés del listing de AliExpress destapa las redes globales:** "bicicleta decorativa" en CO solo devolvió a la propia tienda; "DIY Bicycle Model Scale" devolvió ~460 anuncios del mismo SKU. Busca siempre en ES **y** con el nombre del listing en inglés.
- **"N anuncios usan este contenido"** en la Ad Library = la red de dropshippers reusa ese corte. Muchas tiendas con el mismo copy + mismo video = INDICIO masivo (no PROBADO si todos tienen <60 días).
- **Edad real del creativo** (`efg=` → `asset_age_days`), **notificaciones de TikTok** colándose en la búsqueda con sesión, **ruido de `ads_library_search`** con términos genéricos y **hojas de miniaturas sin Pillow**: ver [references/tecnico-busqueda.md](references/tecnico-busqueda.md).
- **Hook SDD:** bloquea escribir archivos con python/shell (`open(...).write`, `> log`). Usa `>/dev/null` para salidas; los `.md` con Write/Edit; curl/ffmpeg/codex escribiendo media sí pasan. HTML/JSON → escotilla en la carpeta del archivo; para renovarla, `rm -r <carpeta>/.sdd` y crearla de nuevo (vale para cualquier carpeta). Detalle: [references/entrega-artifact.md](references/entrega-artifact.md).
- **Nombres ya tomados** (marcadores mágicos = los que cambian de color) → ver Regla 0, paso 2b.
- **Patrones de producto de regalo/coleccionable** (bicicleta): ASMR de armado (bandeja → destornillador → terminado), "mi nueva terapia" (desconexión), nostalgia "la bici de mi papá/abuelo", Navidad "regalo para el que tiene todo", colección por colores. La red global arranca la temporada navideña en **agosto–septiembre**.

## Fuentes de datos (en orden de preferencia)

1. **Meta Ad Library API** — tool `ads_library_search` (MCP de Meta Ads). Es la vía principal, sin navegador.
   - Buscar por `search_terms` (texto del creativo) o por `page_ids` (todos los anuncios de una página).
   - Flujo típico: `search_terms` con el nombre de marca → saca el `page_id` del primer resultado → re-consulta con `page_ids` para traer toda su biblioteca.
   - `estimated_total_count` = volumen de anuncios de esa marca (señal de cuánto invierte / qué escala).
   - **Limitación clave:** la API NO devuelve el archivo de video/imagen, solo `ad_snapshot_url` (link al anuncio). Para descargar los archivos, ver punto 3.
   - El campo `ad_creative_link_title` suele revelar el ÁNGULO (oferta, promesa, gancho). Es oro para el banco de ángulos.
   - Ojo con nombres de marca ambiguos (p.ej. una marca que también es un topónimo → ruido de agencias de viaje). Filtra por `page_name`/`page_id` real.

1b. **Ad Library en el navegador (Playwright, `browser_run_code_unsafe`)**: es la vía que trae el **copy completo del anuncio, la fecha "En circulación desde" y el orden por impresiones** (`sort_data[mode]=total_impressions`, que es el orden por defecto al abrir). La API ordena por fecha de creación y entierra a los longevos.
   - Varias búsquedas por llamada, parseo de `innerText` y verificación visual con TreeWalker + hoja de miniaturas: ver [references/tecnico-busqueda.md](references/tecnico-busqueda.md).
   - Las búsquedas por frase larga a veces devuelven otro anuncio ("000 resultados"); verifica que el `id` coincida.
   - WebFetch a `facebook.com/ads/library` falla (socket hang up); usa siempre el navegador.

2. **WebFetch a las landing pages** — la API y la Ad Library no exponen el cuerpo del anuncio en video. Las landings sí repiten el copy (titular, beneficios, dosis, oferta, garantía). Úsalo para extraer copy completo de cada competidor. (Algunos dominios bloquean WebFetch con 403; en ese caso usa navegador o el swipe.)

3. **Descarga de creativos (sin swipe, probado el 2026-10-14 con 14 videos del taladro).** Tú los descargas en la misma ronda:
   - **Meta:** en Playwright abre la búsqueda por frase o término (CO y ALL), haz scroll y recorre el DOM con TreeWalker: cada texto `biblioteca: <id>` abre un anuncio y el primer `VIDEO` con `src` que aparece después es su video. Filtra por los `ad_id` que te interesan y baja cada uno con `curl -A "Mozilla/5.0" -o <producto>/media/ref_meta_<anunciante>_<angulo>.mp4 "<src>"` **el mismo día** (caducan en horas). El parámetro `efg` de la URL, en base64, trae `asset_age_days` (la edad real del video, que suele ser mayor que la fecha del anuncio) y `duration_s`: anótalos.
   - **TikTok:** `playAddr` de la rehidratación + cookie `tt_chain_token` → curl.
   - Las URL son largas: pásalas a curl con un heredoc `while read archivo url`, sin reescribirlas a mano.
   - **Verifica cada gemelo con fotogramas al 20, 50 y 80 %** antes de llamarlo gemelo. En el taladro, MM Toys y @samvende parecían gemelos y tenían otro tablero.
   - Ficha de cada archivo en `INDEX-CREATIVOS.md` (fuente, duración, edad, si es gemelo, qué tomar). Después, fotogramas con `ffmpeg` para leer los subtítulos quemados y reconstruir el guion.
   - El `swipe_file.json` de la extensión ad-library-toolkit (en `~/Downloads/ad-library/`, procesado con `scripts/download_swipe_media.py`) queda solo como opción para bajar una biblioteca entera de decenas de anuncios.

## Cómo decidir qué es "competidor compatible"

Define el producto primero (WebFetch a la página del producto). **Extrae y anota sus INGREDIENTES/ACTIVOS y su MECANISMO** (ej. dental: nano-hidroxiapatita 7,5%, sin flúor · articular: glucosamina + condroitina + MSM + cúrcuma). Esos ingredientes son la llave para encontrar productos similares. Luego clasifica en 4 niveles:

- **Gemelo (white-label):** el MISMO producto físico que revende otra marca/dropshipper (mismo nombre de fórmula o mismo empaque). Suelen reciclar un kit de creativos compartido. Es la mina para copiar/traducir directo — el creativo ya está probado y es idéntico a lo que vendes.
- **Directo:** mismo producto/categoría y mismo público, otra marca.
- **Similar por ingrediente/mecanismo:** distinto producto pero con **el mismo activo o el mismo mecanismo** (ej. dental: otra crema con hidroxiapatita aunque sea 10% o 30%; articular: otro suplemento con glucosamina/condroitina). Aquí está el oro para **VARIACIONES**: ángulos y ganchos que puedes adaptar porque el argumento científico/beneficio se sostiene igual.
- **Adyacente:** mismo público pero distinto ángulo (ej. para articular: colágeno belleza, crema de calor, rodilleras).
- **Excluir:** otra categoría, mascotas, y **falsos positivos por keyword**. Límpialos siempre.

Ordena de mejor a peor con una puntuación: **longevidad (días activo = señal de rentabilidad) + cercanía al producto + mercado objetivo/idioma + tiene copy real**. Lo que lleva +300 días corriendo casi siempre es rentable.

## ⭐ REGLA 3 — SIEMPRE buscar productos similares por ingrediente (para variaciones)

En toda investigación, además de revisar los creativos de la marca del usuario y de los competidores directos, **busca activamente productos SIMILARES por ingrediente/activo/mecanismo** — aunque sean otra marca, otro país o distinta concentración. El objetivo es traer **material para hacer variaciones**: ganchos, ángulos y estructuras que funcionan sobre el mismo argumento y que se pueden adaptar al producto del usuario.

Cómo ejecutarla:
1. Del producto del usuario, lista sus **activos principales** y su **mecanismo/beneficio central**.
2. Busca en la Ad Library por cada activo y por el mecanismo, no solo por el nombre de marca. Ejemplos de términos: el nombre del ingrediente (`hidroxiapatita`, `glucosamina condroitina MSM`, `cúrcuma articulaciones`), el beneficio (`remineraliza esmalte`, `dolor de rodilla sin cirugía`), y en varios idiomas/mercados.
3. Detecta **gemelos white-label**: si muchos anunciantes distintos corren el mismo copy/creativo, es el mismo producto reempacado → márcalo y prioriza (es lo más directamente reutilizable).
4. De los similares, extrae lo accionable para variar: **gancho, ángulo, formato, oferta**. Anota de dónde salió cada uno.
5. Vuélcalos al `BANCO-ANGULOS.md` en una sección **"Variaciones desde productos similares"**, marcando el origen (marca + ingrediente en común) y qué habría que adaptar para el producto del usuario.

Regla de claims al variar: nunca copies claims prohibidos (curar, regenerar, reemplazar medicación). Reencuadra al claim defendible del activo (ej. hidroxiapatita → remineraliza el esmalte; glucosamina → apoya el cartílago). Ver también los entregables de guiones.

## ⭐ REGLA 4 — Entregable final: INVESTIGACIÓN CREATIVA COMPLETA (siempre, en toda investigación)

Toda investigación termina en **un solo Artifact publicado** que reúne TODO ads-invest del producto (todas las rondas), listo para construir la landing y los anuncios. Se publica siempre en el mismo archivo y la misma URL, y se actualiza en cada ronda. Su link se guarda en `INICIO.md` y al inicio de `LINKS.md`. Referencia de formato: {ARTIFACT_REFERENCIA} (plantilla correctora, la tienda).

Son **21 secciones en orden fijo**: primero lo de la landing (A: resumen, avatares, dolores, conciencia, ángulos, gemelos, estructura de landing, titulares, oferta sin "antes" ficticio, claims, FAQ, mapa de media, referencias, coherencia) y después la investigación (B: ranking, análisis, copy, testeo, economía, anuncios entregados, bibliotecas, pendientes). Lista completa, ejemplos y la **escotilla SDD** para escribir el HTML: [references/entrega-artifact.md](references/entrega-artifact.md).

Además, guarda en el vault el `PRODUCTO.md` y el resto de entregables. El Artifact es la vista consolidada; los `.md` son la fuente.

## Entregables (genera los que pida el usuario; usa las plantillas de `templates/`)

- **PRODUCTO.md** — ⭐ SIEMPRE (Regla 0). Ficha verificada del producto, claims sí/no, precio y economía.
- **INVESTIGACIÓN CREATIVA COMPLETA (Artifact)** — ⭐ SIEMPRE (Regla 4).

- **LINKS.md** — ⭐ SIEMPRE, aunque el usuario no lo pida. Lista maestra de anuncios entregados agrupados por bloque, cada uno con gancho, evidencia (PROBADO/INDICIO/SIN PROBAR) y link individual; más la tabla de bibliotecas completas por `view_all_page_id`. Es el espejo en archivo de lo que se entregó en el chat.
- **RANKING.md** — competidores ordenados mejor→peor, con país, formato, días activo, page_id.
- **COPY.md** — copy de cada anuncio (titular, beneficios, dosis, oferta, garantía, CTA).
- **ANALISIS-BIBLIOTECAS.md** — por competidor: nº de anuncios, qué hacen, ✅ qué copiar / ❌ qué ignorar.
- **BANCO-ANGULOS.md** — ⭐ el más accionable: matriz por producto de ~12 ángulos (gancho + origen) × banco de ofertas × formatos + plan de testeo de 3 rondas. **Incluye una sección "Variaciones desde productos similares"** (Regla 3): ganchos/ángulos tomados de productos con el mismo ingrediente/mecanismo, con su origen y qué adaptar.
- **INDEX-CREATIVOS.md** — ficha de cada creativo descargado (archivo, copy, landing, días activo, link Ad Library).

## Patrones ganadores recurrentes (búscalos y replícalos)

- **Vender la OFERTA y la LOGÍSTICA, no el feature**: "pago contra entrega", "envío 24/48h", "-30% 2ª unidad", BOGO/2×1. (Adapta a `Colombia`: en mercados con desconfianza al pago online, contra entrega es la palanca #1.)
- **Dato + plazo en el titular**: "80% mejoró en 30 días", "resultados en 14 días".
- **Numerología en el titular**: `Nº ingredientes + Nº tomas + Nº días` (ej. "9 nutrientes · 1 cápsula · 4 semanas").
- **Banco de muchos ángulos sobre un mismo producto**: dato, edad/miedo ("después de los 45…"), dolor específico, objeción, "el único con…", prueba social masiva.
- **Autoridad/médico con rostro y nombre** que recomienda.
- **Embudo advertorial**: anuncio con página de "persona" → artículo/listicle ("5 razones…", "Top 5…") → producto. Es el desbloqueo de escala.
- **Sistema multi-página** (marca + "Reviews" + "Health/Blog") para envolver al comprador.
- **Escalera de packs + bonus de regalo** (30/60/90 unidades, el de en medio marcado como ahorro; regalo de alto valor en vez de % para proteger margen).
- **LTV / marca**: el cliente de una categoría recompra. Visión de marca, no de un solo SKU.

## Flujo de una ronda de investigación

1. Leer `REGISTRO-INVESTIGACION.md`, **incluida la tabla `🔗 ANUNCIOS YA ENTREGADOS`** (omitir esos `ad_id`).
2. **(Regla 0) Verificar el producto REAL** (Shopify, Drive en el navegador si la API no lista, fotos y docx) y escribir o actualizar `PRODUCTO.md`: formato, material, **ingredientes/activos o mecanismo** (se usan en el paso 3b) y claims sí/no. Sin producto verificado no se busca.
2b. **(Regla 0b) Cazar gemelos exactos fuera de Meta**: AliExpress (identificar el SKU y su nombre exacto) → TikTok (videos y anuncios del mismo producto), con verificación visual.
2c. **(Regla 0d) Mercado local**: Mercado Libre CO + retail + TikTok CO → tabla de precios en `PRODUCTO.md`. Pedir el costo real antes de proponer packs.
2d. **(Regla 0e) Landings extranjeras**: Amazon, Shopify DTC, retail de EE. UU./Reino Unido y TikTok Shop → `LANDINGS.md` con la estructura recomendada.
3. Buscar competidores NUEVOS con `ads_library_search` (marcas, términos en inglés y en el **idioma/mercado** de `Colombia` que suele estar sin explorar; también investigar global cuando sea relevante). Sacar page_ids y volúmenes.
3a. **(Regla 4b, Paso 0) Radar de formatos:** además de la categoría, 5 anuncios PROBADOS de otras categorías COD (hogar, belleza, mascotas, juguetes), buscados por "pago contra entrega" y ordenados por días activos. Solo interesa su **formato**, no el producto.
3b. **(Regla 3) Buscar productos SIMILARES por ingrediente/mecanismo** — además de la marca del usuario y los directos. Buscar por cada activo y por el beneficio central, en varios mercados/idiomas. Detectar gemelos white-label (mismo copy repetido = mismo producto reempacado). Objetivo: traer ganchos/ángulos para hacer VARIACIONES.
4. **Filtrar contra el registro**: descartar todo `ad_id` ya entregado antes de rankear.
5. Clasificar (gemelo/directo/similar-por-ingrediente/adyacente/excluir) y rankear por longevidad + relevancia. Asignar evidencia PROBADO / INDICIO / SIN PROBAR a cada uno **y su FORMATO** con el nombre del catálogo de `FORMATOS.md` (Regla 4b, Paso 1).
6. Extraer copy de los mejores vía WebFetch a sus landings.
7. **Descargar tú mismo los videos** de los gemelos y de las referencias top (Meta con `video.src`, TikTok con `playAddr`), verificarlos con fotogramas y fichar cada uno en `INDEX-CREATIVOS.md`. No le pidas el swipe al usuario.
8. **Entregar los links en el chat** (Regla 1): anuncios individuales + bibliotecas, con gancho y evidencia, y dónde quedó cada video. Si son >25, publicar Artifact y dejar el top en el chat.
9. Generar/actualizar los entregables, **siempre incluido `LINKS.md`** (AÑADIR al doc existente del producto, no crear archivos por ronda).
10. **Actualizar `REGISTRO-INVESTIGACION.md`**: añadir una fila por cada `ad_id` entregado, las bibliotecas nuevas, los términos usados y los pendientes.
11. **(Regla 4) Publicar o actualizar la INVESTIGACIÓN CREATIVA COMPLETA**: un Artifact con las 21 secciones e integrando todas las rondas. Mismo archivo y misma URL en cada ronda. Link en el chat, en `INICIO.md` y en `LINKS.md`.

> ⚠️ Una ronda NO está terminada si: no hay tabla de mercado local con precios (Regla 0d), no se analizaron las landings extranjeras (Regla 0e), el producto no está verificado (Regla 0), el usuario no recibió links clicables, el registro no tiene los `ad_id`, la investigación creativa completa (Regla 4) no está publicada y actualizada, **o la matriz no tiene la tabla "Formatos del mercado" y la columna "Por qué este formato", o repite más de 4 formatos del producto anterior, o no se corrió el radar de formatos y no se reportaron al dueño los formatos nuevos (aunque sean cero: se dice "radar sin formatos nuevos") (Regla 4b)**.

## Reglas de costo y estilo

- Aplica "documentar primero": prioriza API + WebFetch + scripts. Para la Ad Library, el navegador (Playwright) con varias búsquedas por llamada es la vía buena (copy, fechas, impresiones); evita clics manuales.
- No vuelques miles de anuncios crudos en el chat; el valor está en los ÁNGULOS y el sistema, no en el volumen. Sintetiza y guarda en archivo.
- Responde en el idioma del usuario (código y nombres de archivo/variable en inglés).
- Cambia 1 variable por ronda de test (ángulo → oferta → formato); explícalo al usuario en el plan.
