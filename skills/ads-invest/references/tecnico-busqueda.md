# Técnica de búsqueda y descarga (Drive, AliExpress, TikTok, Meta)

Detalle operativo de las Reglas 0, 0b y 1. El SKILL.md dice QUÉ hacer; esto dice CÓMO.

## Drive del proveedor
- **Listar** (carpeta compartida por link; la API no lista): Playwright → `drive.google.com/drive/folders/<id>` → `[data-id]` + `innerText` (nombre).
- **Descargar sin navegador:** `curl -sL "https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t" -o archivo`. Funciona con videos grandes.
- **Leer .docx:** `unzip -p archivo.docx word/document.xml | sed -e 's/<\/w:p>/\n/g' -e 's/<[^>]*>//g'`.
- **Miniaturas:** `https://drive.google.com/thumbnail?id=<id>&sz=w400`, o local con ffmpeg (ver abajo).
- Revisa TODOS los videos del proveedor: puede venir uno con otra marca en la caja (marcadores: `prov_v3` traía GENVANA) → no usarlo.

## Hojas de miniaturas (sin Pillow)
- Imágenes: `ffmpeg -i img_%d.jpg -vf "scale=400:400:force_original_aspect_ratio=decrease,pad=400:400:(ow-iw)/2:(oh-ih)/2:white,tile=4x2" -frames:v 1 hoja.jpg`
- Video: extrae N fotogramas con `-ss <t>` y únelos con `tile=6x2`. No uses `fps+tile` para QA (engaña).
- webp: ffmpeg los lee (ignora el aviso de EXIF).

## AliExpress
- `https://www.aliexpress.com/w/wholesale-<terminos>.html?SearchText=<terminos en inglés>` → scroll → `a[href*="/item/"]` + innerText.
- El **nombre exacto del listing** ("DIY Bicycle Model Scale", "Linear Color Pen", "curve highlighter") es la llave para encontrar las redes globales en Meta y TikTok.

## TikTok
- Búsqueda: `https://www.tiktok.com/search/video?q=<termino>`, scroll `mouse.wheel` 700 × 8.
- **Con sesión iniciada** (perfil de Playwright del dueño): los primeros 3–4 `a[href*="/video/"]` son notificaciones de la cuenta (textos "dio me gusta", "le ha gustado tu comentario"). Fíltralos por texto antes de rankear.
- Detalle: `script#__UNIVERSAL_DATA_FOR_REHYDRATION__` → `__DEFAULT_SCOPE__['webapp.video-detail'].itemInfo.itemStruct` → `desc, createTime, stats.playCount/diggCount/shareCount, author.uniqueId, isAd, video.duration, video.playAddr`.
- **Filtrar por país:** `itemStruct.locationCreated` ("CO", "MX", "PE"…) dice desde dónde se publicó el video. Sirve para quedarse solo con creadores colombianos: la búsqueda "colombia" trae también México y Perú.
- Algunas páginas devuelven `Unterminated string in JSON` al parsear la rehidratación (el script viene cortado). Envuelve cada video en `try/catch` y sigue con el resto.
- Búsquedas útiles para encontrar creadores UGC colombianos: `reseña colombia papeleria`, `ugc colombia producto`, `unboxing colombia`, `<categoría> colombia`. Hay perfiles que son anuncios de pago (`isAd: true`, "Colaboración de pago"), por ejemplo @elpaisareviews, con 6,6 M.
- **Descarga:** `playAddr` + cookie `tt_chain_token` (solo esa) → `curl -H "Cookie: tt_chain_token=…" -H "Referer: https://www.tiktok.com/" -A "<UA Chrome>" "<playAddr>" -o archivo.mp4`. URLs en heredoc a `while read`. Nunca fetch + `<a download>` (cierra el navegador). En `run_code` no hay `fs`/`require`/`import`.
- **Anuncios de TikTok Shop:** `playAddr` viene vacío y el `<video>` es `blob:`; tampoco se ven fuera de la app (la captura sale en blanco). No se pueden descargar ni verificar visualmente: márcalos **"probable (TikTok Shop)"** y pídele al dueño que los abra en el celular.
- **Creative Center (Top Ads):** sin sesión ignora `keyword` y solo muestra 4 anuncios genéricos.
  - Login en Playwright que SÍ funcionó: "Log in" → "Log in with TikTok" → "Use QR code" (el usuario escanea) → "Verify identity" con código de 6 dígitos **al correo**, que el usuario escribe. El SMS falla con error de JS. Nunca escribas credenciales ni códigos del usuario. La sesión queda en el perfil de Playwright.
  - API: el `keyword` de la URL NO filtra. Escribe una vez en el buscador para capturar los headers (`page.on('request')` sobre `/top_ads/v2/list`) y llama a `https://ads.tiktok.com/creative_radar_api/v1/top_ads/v2/list?period=180&keyword=<kw>&page=1&limit=20&order_by=like&country_code=<CC>` con `page.request.get(url,{headers})` → `data.materials[]` (`id, ad_title, brand_name, like, ctr, cost, industry_key, video_info.cover`). Rate limit 40100 → 4–6 consultas con 2–3 s de pausa.
  - Link de cada anuncio: `https://ads.tiktok.com/business/creativecenter/topads/<id>/pc/en`. "plantillas" en español trae ruido (Excel): filtra por título o industria.
  - Si el login falla, dale los links al usuario y que te pase screenshots: la búsqueda normal ya marca `isAd`, así que es un complemento.

## Meta Ad Library en el navegador
- Varias búsquedas en una llamada: `page.goto` en bucle a `…/ads/library/?active_status=active&ad_type=all&country=<CC|ALL>&is_targeted_country=false&media_type=all&search_type=keyword_unordered&q=<q>` + scroll 3–5 veces.
- Parseo: `document.body.innerText.split(/\n(?=Activo\nIdentificador de la biblioteca)/)` → `id`, `En circulación desde el …`, `N anuncios usan`, anunciante (línea antes de "Publicidad"), cuerpo, dominio.
- Miniaturas + `video.src`: TreeWalker; a cada `biblioteca: <id>` le asigna el primer `VIDEO` (poster/src) o `IMG` ≥150 px. Hoja con `page.context().newPage()` + `setContent` + screenshot **en la misma llamada** (las variables no persisten).
- Descarga: `curl -A "Mozilla/5.0" "<video.src>"` el mismo día (caducan). 360p sirve de referencia. **Este es el camino por defecto; ya no se le pide el swipe al dueño** (2026-10-14). Para una lista de `ad_id` concretos: recorre 2–4 búsquedas por término (CO y ALL), guarda `{id: src}` solo de los que están en tu lista y devuelve ese objeto. Abrir `?id=<ad_id>` suelto no sirve, porque Meta redirige a la biblioteca de la página.
- Las URL de video y de TikTok son largas: no las reescribas. Pásalas a curl con un heredoc `while read archivo url` copiando el resultado tal cual.
- `efg=` (base64) en la URL de fbcdn trae `asset_age_days` = edad real del video.
- La API `ads_library_search` con términos genéricos trae ruido (dramas, apps); úsala para marcas y page_ids, no para descubrir.
- El resultado grande de un `run_code` se guarda en archivo: léelo con python sobre `### Result\n"…"` (doble `json.loads`).

## Instagram (reels y posts sin sesión, probado el 2026-10-15)
1. Abrir `https://www.instagram.com/<reel|p>/<shortcode>/embed/captioned/` en Playwright. Se ven, sin login, la cuenta, los seguidores, los likes, el caption y la cantidad de comentarios (`document.body.innerText`).
2. Video: `document.querySelector('video').src` (cdn `fbcdn.net/.../*.mp4`, firmado y temporal). Los carruseles de solo imágenes no traen `<video>`.
3. Descarga: `run_code` no tiene `require` ni `fs`, y `globalThis` no persiste entre llamadas. Hay que devolver `id + url` en el resultado, sacarlos del jsonl de la sesión con `grep -o '[A-Za-z0-9_-]\{11\} https://instagram[^ "\\]*'` y bajarlos con `curl -L -H "Referer: https://www.instagram.com/" -A "Mozilla/5.0"`. Así no se copian a mano las URLs largas.
4. Transcripción: no hay CLI `mlx_whisper`. Se usa `~/.venvs/voz/bin/python -I` con `mlx_whisper.transcribe(f, path_or_hf_repo='mlx-community/whisper-large-v3-turbo')` e impresión en pantalla (detecta ES/EN/PT). Los videos de carrusel pueden venir **sin audio** (ffmpeg sale con error 234): para esos se arma una hoja de fotogramas.
5. Las listas en pantalla (por ejemplo "35 formatos") se leen mejor en el **último fotograma**: `-sseof -1.5`.
6. Cerrar el navegador antes de whisper (Mac de 8 GB).

## Hook SDD (fuera de repos con arnés)
- Bloquea escribir archivos con shell/python (`> log.txt`, `open(...).write`). Usa `>/dev/null` para salidas y Write/Edit para `.md`. curl/ffmpeg/codex escribiendo media sí pasan.
- HTML y JSON necesitan escotilla: ver [[entrega-artifact]].
