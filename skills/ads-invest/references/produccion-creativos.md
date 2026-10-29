# Producción de creativos propios (Regla 5)

**Material permitido (no negociable):** fotos y videos del proveedor (Drive, Shopify, galería de AliExpress) + escenas generadas con Codex + **videos de stock de Magnific** + material grabado por el usuario. **Nunca** pautar ni usar como b-roll videos de competidores o creadores, aunque el usuario lo pida. Alternativas: (1) videos del proveedor con el guion de la referencia, (2) que el usuario grabe una unidad con guion toma por toma, (3) licenciar al creador (los de "colaboración pagada" suelen aceptar).

## 1. Guion
- Cada video copia la **estructura** de UNA referencia (gemelo o top): transcribe con whisper → adapta a los claims ✅ de `PRODUCTO.md`.
- Léxico colombiano natural (ustedes/usted, diminutivos, "pillen", "vea"), números escritos con letras y precios reales. Sin "antes" ficticio.
- Guiones y escenas por video en `<producto>/media/ronda-a-<marca>/GUIONES-RONDA-A.md` (plantilla: marcadores).

## 2. Voz — estándar aprobado por el dueño (2026-10-09)
- **OmniVoice** (venv `~/.venvs/voz`): `OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="mps", dtype=torch.float32)`, `num_step=32`, 24 kHz.
- **Guion completo en UNA sola llamada** con `instruct` + `speed`. Así la voz no cambia a mitad del video.
- `instruct` solo acepta estas etiquetas: `male/female` · `child/teenager/young adult/middle-aged/elderly` · `very low/low/moderate/high/very high pitch` · `whisper` · acentos en inglés. **No hay emociones ni acento latino**: la energía sale del guion (puntuación, frases cortas).
- **Nunca `teenager`**: sale vacío o con un pito. Para una voz juvenil: `female, young adult, moderate pitch`, `speed` 1,1–1,15.
- Perfiles aprobados (marcadores, `media/voces-prueba/`): A curiosidad (young adult, high pitch, 1,12–1,15) · B presentadora (young adult, moderate, 1,0) · C estudiante (young adult, moderate, 1,12) · D mamá (middle-aged, moderate, 1,0) · E profe (young adult, low, 1,02) · F hombre (male, young adult, moderate, 1,05).
- **Validación obligatoria:** whisper transcribe la toma y se compara con el guion (difflib sobre texto normalizado). Si la similitud es < 0,9, se regenera (hasta 4 intentos). OmniVoice a veces se come frases.
- ❌ **Rechazado por el dueño:**
  - Generar frase por frase. Con `instruct` crea un hablante nuevo en cada llamada, y si se trocea hay que fijar la voz con `voice_clone_prompt` de una toma ancla.
  - Los "formatos colombianos" forzados de `voces-colombia/GUIA-VOCES-COLOMBIA.md`.
  - Las voces es-CO de Microsoft (Salomé y Gonzalo).
- **No se clona la voz de ningún creador.** Para clonar hace falta una muestra de 15–30 s de alguien que lo autorice por escrito.

## 3. Tiempos por palabra
`mlx_whisper.transcribe(wav, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', word_timestamps=True, language='es')` → lista `(palabra, inicio, fin)`. Los cortes de escena van al inicio de cada frase y los subtítulos en bloques de 3–4 palabras.

## 4. Música propia
`~/.venvs/voz/bin/python -I ads-invest/plantilla-ortopedica/media/_gen_music.py <preset> <seg> <salida.wav>` (presets: energetic, energetic108, ugc, ambient, warm, driving, tense, cinematic). Va a un volumen de 0,10–0,20 bajo la voz.

## 5. Material del proveedor (recortes)
- Hoja de miniaturas por video: `fps=12/<dur>,scale=240:-2,tile=6x2` → descartar tomas con letras chinas, otra marca o un producto distinto.
- Recortar la franja con texto quemado (marcadores `prov_v1`: `crop=720:500:0:0`) y escalar a 1080 de ancho: `-vf "<crop>,scale=1080:-2,fps=30" -an -c:v libx264 -crf 18 -pix_fmt yuv420p`.
- Clips cortos (2–5 s) con nombre descriptivo en `ronda-a-<marca>/clips/` (`v1_macro_rodillo`, `v2_cartelera_borde`…).

## 6. Edición
- **Con escotilla SDD:** HyperFrames, `_gen_hf.py <clave> <carpeta>` (plantilla Postura360: STYLES/SCENES/marca fijos, hay que adaptarlo por producto). Render a 1080×1920.
- **Sin escotilla (no se escribe código):** solo ffmpeg + PNG renderizados en Playwright (`page.context().newPage()` + `setContent` + `screenshot`, fondo transparente con `omitBackground`): subtítulos por bloque, gancho y **tarjeta final de oferta 1080×1920** (plantilla `marcadores-magicos/media/ronda-a-marcadores/clips/card_oferta.png`). ffmpeg: fondo difuminado + clip encima → concat por escena → `overlay=enable='between(t,a,b)'` por subtítulo → mezcla voz + música. **La función `build` completa, lista para copiar, está en `montaje-ffmpeg.md`** (tipos de escena: `v` clip del proveedor con fondo difuminado, `f` stock a pantalla completa, `i` imagen con zoom).
- Edición por guion: mide la referencia (cortes con umbral 0,32, tempo, fotogramas). UGC = cortes secos; explicativos = flechas y círculos.
- En títulos dentro del PNG: verifica que no se partan en dos líneas encima de la foto (`white-space:nowrap` + tamaño ajustado).

## 7. B-roll de stock con Magnific (escenas de contexto)
- **Magnific se usa para bajar stock, NO para generar video** (corrección del dueño, 2026-10-13). Con su plan Premium+ el stock **no gasta créditos** aunque la búsqueda diga `creditCost: 600` (verificado: el saldo no cambió tras 5 descargas premium). Generar con Kling o Seedance sí cobra, así que no se usa salvo que el dueño lo pida.
- Buscar: `stock_search` con `content_type: video`, `orientation: portrait`, `ai_generated: excluded` y la consulta en inglés ("bored student studying notebook", "girl opening christmas gift").
- Elegir: bajar las miniaturas (`…/vertical/thumbnails/small.jpg`) a una carpeta propia y armar una hoja con `xstack` (en zsh se escribe `${i}` y no `$i:` dentro del filtro, porque `:l` se lee como modificador). Después, 8 fotogramas por clip (`fps=1/(dur/8),scale=180:320,tile=8x1`) para escoger el tramo.
- Descargar: `stock_download` (`type: video`, `max_bytes: 20000000`) → `curl` a `<ronda>/stock/sXX_<escena>.mp4`. Recortar a `clips/stk_<escena>.mp4` con `-ss <inicio> -t 4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1" -an`.
- **Regla de oro:** el stock no trae el producto. Solo va en escenas de contexto (problema, persona, emoción, regalo). Si en esa frase la voz nombra el producto ("con estos marcadores…", "con uno hacemos el borde…"), la escena lleva material del proveedor o una imagen de Codex. Errores reales: un esfero normal bajo "CON ESTOS MARCADORES" y acuarelas bajo "el borde de corazones".
- En el montaje entra con el tipo `f` (pantalla completa, ver `montaje-ffmpeg.md`).

## 8. Escenas con Codex (si falta material)
`codex exec --skip-git-repo-check -s workspace-write -C <dir> -i ref1 -i ref2 -- "Use your image generation tool… copy the generated image into the current working directory as X.png" >/dev/null 2>&1`. El producto SIEMPRE fiel a la foto real. Varias en paralelo con `&` + `wait`.
- Si el video tiene que mostrar el producto **en movimiento** (cómo se pone, cómo funciona) y el proveedor no trae esa toma, las imágenes de Codex sirven de primer fotograma para clips con IA en Magnific Spaces: [video-ia-spaces.md](video-ia-spaces.md).

## 8b. Estáticos (sin escribir HTML a disco)
- Se componen en el navegador: un servidor local de la carpeta de medios (`npx -y http-server <media> -p <puerto> -s` en segundo plano) y, en Playwright, `document.open(); document.write(html); document.close()` con las imágenes por ruta relativa → `page.screenshot` a 1080×1350 (4:5) y 1080×1920 (9:16, con los 340 px de abajo libres). Así no hace falta guardar archivos HTML (que el hook bloquea).
- **Cada estático sale en las dos medidas** y van juntos en un solo anuncio (4:5 al feed, 9:16 a historias y reels): ver `montaje-ffmpeg.md` § Subida.
- Subtítulos de video transparentes con el mismo truco y `omitBackground: true`.
- **Los formatos nativos tienen que parecer la interfaz real** (el dueño, 24-oct: "el de noticia no parece noticiero"). Noticia = nota de portal: cabecera con nombre de portal **inventado** (nunca un medio real), menú y lupa, barra de secciones, titular en letra de periódico (serif), autor y "2 min de lectura", foto con pie de foto que explique el mecanismo, un párrafo y el precio con "Ver más →". Lo mismo para historia de IG, WhatsApp, Google: si no se confunde con la app de verdad, no sirve.
- **Encuadre de las fotos** (el dueño, 24-oct: "las fotos están mal encuadradas"): en cada recuadro tiene que verse completo lo que el texto nombra (la cara entera con las manos poniéndose el producto, el control completo con su pantalla). Ajusta `object-position` por foto y revisa que el precio o la píldora no tapen el último paso en la versión 9:16.
- Antes de mostrarlos: una hoja con todos en miniatura (`hstack`/`vstack`) y la **prueba de los 2 segundos**: producto visible + línea de mecanismo + beneficio en cada pieza. Errores vistos: la tarjeta del producto tapando la píldora de envío, texto quemado de otra imagen asomándose en un recorte y espacio en blanco al final de una tabla.

## 9. QA y entrega
- Fotogramas en segundos exactos, producto sin deformar, voz sin claims ❌, **uso correcto** del producto (la IA puso a una profe escribiendo con marcadores de papel en un tablero → falso).
- Entrega: `<producto>/media/ronda-a-<marca>/<MARCA>_VN0X_<angulo>.mp4` + `INDEX-CREATIVOS.md`. Antes de subir, **mostrarle los videos al dueño** (`open <mp4>`) y esperar su ok. Subida a Meta por API: `montaje-ffmpeg.md` § Subida + `/cod-ops:one-cbo` → "Montar la campaña por API" (nunca abrir el borrador en el editor: se convierte a catálogo).

## 10. Procesos largos (OmniVoice + whisper)
- Correr en segundo plano con `python -u` y una línea `LISTO <clave>` por pieza; vigilarlo con Monitor (`grep --line-buffered "LISTO|Error|Traceback"`).
- Para validar, `whisper-small-mlx` (rápido); `large-v3-turbo` solo para los tiempos finales. Un bucle con large por frase se atascó más de 25 minutos.
