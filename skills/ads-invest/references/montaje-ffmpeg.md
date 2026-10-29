# Montaje con ffmpeg y subida a Meta

Se usa cuando no hay escotilla SDD (sin escribir código: bash + ffmpeg). Se probó con los 4 videos de Marcadores Mágicos (Ronda A, 2026-10-13). Los planes de escenas reales están en el handoff `ads-invest/HANDOFF-2026-10-13.md` y en la carpeta `marcadores-magicos/media/ronda-a-marcadores/`.

## Insumos por video
- Voz validada: `voz/vo_XX.wav` · música: `musica/music_XX.wav` (al 0,15) · subtítulos PNG 1080×1920 transparentes: `caps/XX_NN.png` · tarjeta final: `clips/card_oferta.png`.
- `SC=("tipo|archivo|inicio|fin" …)` con un corte al inicio de cada frase de la voz:
  - `v`: clip del proveedor (horizontal o cuadrado) → fondo difuminado + clip encima, subido 80 px.
  - `f`: clip ya preparado a 1080×1920 → pantalla completa (stock vertical, clip de Kling o clip de fábrica ya compuesto, ver abajo).
  - `i`: imagen 1080×1920 (Codex, landing, tarjeta) → zoompan suave hasta 1,12.
- **Clips de fábrica horizontales (720p): NO recortarlos a 9:16.** Recortar una franja vertical de un video de 1280×720 lo amplía ~2,7× y se ve borroso y demasiado cerrado (el dueño, 14-oct: "tienen mucho zoom"). Lo que funcionó: un **cuadrado** de 640–720 px alrededor de la acción, escalado a 1080×1080 (1,5×) sobre la misma toma difuminada, y tratarlo como `f`:
  ```bash
  sq(){ ffmpeg -nostdin -v error -y -ss $3 -t $4 -i $2 -filter_complex "[0:v]crop=$5,scale=1080:1080,setsar=1,split[s][b];[b]scale=1920:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.05[bg];[bg][s]overlay=0:380,fps=30,format=yuv420p" -an -c:v libx264 -crf 18 clips/$1.mp4; }
  sq fa_nino_taladro fabrica.mp4 11.35 2.8 720:720:150:0   # nombre fuente inicio duración crop(w:h:x:y)
  ```
  Con texto chino quemado abajo, sube el cuadrado (`crop=590:590:x:0`) para dejarlo fuera.
- **Menos imágenes fijas:** el dueño rechazó videos "con muchas fotos" y stock fuera de contexto. Prioridad: tomas en movimiento (fábrica o Kling) > stock que coincide con la frase > imágenes de la landing (solo la tarjeta final).
- `CP=("inicio|fin[|índice]" …)`: un subtítulo por bloque. El índice es opcional y sirve cuando el PNG no sigue el orden (por ejemplo MM04 18–21).

## Función build (copiar tal cual dentro de `bash <<'EOF' … EOF`, desde la carpeta de la ronda)
```bash
L=../landing; R=broll
build(){ out=$1; vo=$2; mu=$3; name=$4; ins=""; fc=""; n=0; cat=""
 for s in "${SC[@]}"; do IFS='|' read -r t f a b <<<"$s"; d=$(printf "%.3f" $(echo "$b-$a"|bc))
  if [ "$t" = v ]; then ins="$ins -stream_loop -1 -t $d -i $f"
   fc="$fc[${n}:v]split[a${n}][b${n}];[a${n}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2[bg${n}];[b${n}]scale=1080:-2[fg${n}];[bg${n}][fg${n}]overlay=(W-w)/2:(H-h)/2-80,setsar=1,fps=30,trim=0:${d},setpts=PTS-STARTPTS,format=yuv420p[v${n}];"
  elif [ "$t" = f ]; then ins="$ins -stream_loop -1 -t $d -i $f"
   fc="$fc[${n}:v]scale=1080:1920,setsar=1,fps=30,trim=0:${d},setpts=PTS-STARTPTS,format=yuv420p[v${n}];"
  else ins="$ins -loop 1 -t $d -i $f"
   fc="$fc[${n}:v]scale=1080:1920,setsar=1,fps=30,trim=0:${d},setpts=PTS-STARTPTS,zoompan=z='min(zoom+0.0012,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p[v${n}];"
  fi; cat="$cat[v${n}]"; n=$((n+1)); total=$b; done
 fc="$fc${cat}concat=n=${n}:v=1:a=0[base];"; prev=base; i=0
 for c in "${CP[@]}"; do IFS='|' read -r a b k <<<"$c"; b2=$(printf "%.3f" $(echo "$b-0.04"|bc)); idx=$((n+i)); f=$(printf "caps/%s_%02d.png" $out ${k:-$i}); ins="$ins -i $f"
  fc="$fc[$prev][${idx}:v]overlay=0:0:enable='between(t,${a},${b2})'[c${i}];"; prev=c${i}; i=$((i+1)); done
 vi=$((n+i)); mi=$((vi+1)); ins="$ins -i $vo -i $mu"
 fc="$fc[${vi}:a]apad,atrim=0:${total}[vo];[${mi}:a]atrim=0:${total},volume=0.15,afade=t=out:st=$(echo "$total-1"|bc):d=1[mu];[vo][mu]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]"
 ffmpeg -nostdin -v error -y $ins -filter_complex "$fc" -map "[$prev]" -map "[aout]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ac 2 -ar 48000 -t $total -movflags +faststart "final/con_voz/$name.mp4" && echo "LISTO $name"
}
# Ejemplo (MM04, con stock):
SC=("f|clips/stk_nina_regalo.mp4|0|2.68" "f|clips/stk_mujer_sorpresa.mp4|2.68|4.24" "v|clips/v1_set6.mp4|4.24|5.36" "i|$R/b01_mano_corazones.png|5.36|7.18" … "i|clips/card_oferta.png|17.46|19.5")
CP=("0|.82" ".82|1.7" … "13.0|13.72|18" …)
build MM04 voz/vo_MM04.wav musica/music_MM04.wav MM_VN04_regalo_navidad_CON_VOZ
```
- `-nostdin` es obligatorio (sin él, ffmpeg se come el heredoc). `printf "%.3f"` evita decimales como `.96` que ffmpeg no lee.
- Antes de rearmar: respaldar la versión anterior en `final/con_voz/v1_<origen>/`.

### Lecciones de la Ronda B de Postura360 (2026-10-15)
- **Siempre correr dentro de `bash <<'EOF'`.** En zsh, `[$j:v]` revienta ("bad math expression"), porque `:v` se lee como un modificador.
- **Ninguna escena puede durar más que su clip.** La función usa `-stream_loop -1`, así que un clip de fábrica de 1–2,5 s se repite y se nota. Hay dos salidas: partir la frase en dos clips, o cortar subclips del stock con su propio inicio: `ffmpeg -ss <ini> -t <dur> -i stock/x.mp4 -an -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" clips/stk_x_a.mp4`. Así una toma larga de stock da 2–3 escenas distintas en vez de repetir el arranque.
- **Video sin voz (macro):** voz `anullsrc` → `voz/silencio.wav` y música al 0,9 (la función lee `MV`, que vale 0,15 por defecto; se pone `MV=0.9` antes del `build`).
- **Tarjeta final** = portada 1:1 de la landing (con los 3 packs) sobre un lienzo 1080×1920, más un overlay PNG transparente con el botón "Pídela aquí abajo 👇". Si la portada ya trae el nombre, se recorta el overlay para no repetir el título.
- **La build de ffmpeg no trae `drawtext`.** Los rótulos de las hojas de QA van sin texto, o se generan en PNG con Playwright.
- **`-ss` necesita un cero adelante:** `$(echo "$d/2"|bc -l)` da `.76`, que ffmpeg rechaza. Se envuelve en `printf "%.2f"`.
- **Hoja de inventario antes de armar listas:** un fotograma central de cada clip (`tile=10x2`) para saber qué muestra cada archivo antes de asignarlo a una frase.

## QA
- Duración de cada mp4 = fin de la última escena.
- Un fotograma en el centro de cada escena nueva (`-ss t -frames:v 1 -vf scale=216:384` → `hstack`): revisar que **la imagen coincida con el subtítulo** y que el producto no esté deformado.
- **La imagen no puede contradecir el mensaje.** En la Ronda B, la plantilla aparecía doblándose con la mano justo cuando el texto decía "arco firme", "TPR firme" o "ya están aplastadas". Las tomas de flexibilidad no van con frases de firmeza ni en el gancho de "se aplastan": ahí van presión, copa de talón o una persona con molestia.
- Si se cambió la voz: transcribir con whisper y comparar con el guion. Si solo cambió la imagen, el audio queda igual.

## Subida a Meta (después del ok del dueño)
1. **Miniatura propia por video:** `ffmpeg -ss 0.5 -i X.mp4 -frames:v 1 -q:v 2 thumb_X.jpg` (el gancho con su subtítulo).
2. **URL pública vía Shopify Files:** `stagedUploadsCreate` (resource FILE, mp4 y jpg en una sola llamada, con `fileSize`) → POST multipart con `curl -F` por cada destino (los parámetros en el orden recibido y `file=@…` al final; esperar 201) → `fileCreate` con los `resourceUrl` (**los mp4 con `contentType: FILE`**: con `VIDEO` Shopify responde "Invalid video url" porque el destino se pidió como FILE; los jpg sí van con `IMAGE`) → `nodes(ids)` hasta `READY` para leer `url` (cdn.shopify.com). Para no copiar firmas a mano: leer la respuesta desde el jsonl de la sesión (`~/.claude/projects/<proyecto>/<sesión>.jsonl`), filtrando las líneas con `x-goog-signature` que no contengan `python3`. **Máximo 20 MB por archivo** (resource FILE): mide con `stat -f%z` antes; si un mp4 pasa, re-codifícalo subiendo el `-crf` (23–26, misma resolución) y vuelve a medir.
3. `ads_creative_upload_media` (URL, VIDEO para el mp4 · IMAGE para la miniatura → `hash`) → `ads_get_ad_videos` con `video_ids` hasta `status` listo.
4. `ads_create_ad_set` (un conjunto OPEN por video): `OFFSITE_CONVERSIONS`, `IMPRESSIONS`, `WEBSITE`, `promoted_object={"pixel_id":"{PIXEL_ID}","custom_event_type":"PURCHASE"}`, `targeting={"geo_locations":{"countries":["CO"]},"age_min":18,"age_max":65}`, sin presupuesto (la campaña es CBO).
5. `ads_create_creative`: `video_id` + `image_hash` de su miniatura + `instagram_user_id` + `SHOP_NOW` + `link_url` con `utm_content=vn0X` + DOF con estas 9 funciones en OPT_OUT: `image_touchups, text_optimizations, adapt_to_placement, image_templates, image_uncrop, enhance_cta, product_extensions, site_extensions, video_auto_crop`. (`standard_enhancements` ya no se acepta).
6. `ads_create_ad` con `{"creative_id":…}` → `ads_get_ad_entities` con `object_state=draft` → `ads_activate_entity` con `object_ids` (conjuntos + anuncios) y `publish_as_active=true` → verificar estados en vivo y la vista previa.

**Campaña CBO ya publicada:** `ads_create_ad_set` responde "the parent campaign does not use CBO" aunque la campaña sí tenga presupuesto, porque valida contra el borrador. Arreglo probado: `ads_update_entity` en la campaña con el **mismo** `daily_budget` (no pausa nada) → crear conjuntos, creativos y anuncios → `ads_get_ad_entities` con `object_state=draft` → `ads_activate_entity` con la campaña, los conjuntos y los anuncios en `object_ids` y `publish_as_active=true`. Los anuncios pasan a ACTIVE / IN_PROCESS (revisión de Meta).

### Estáticos: 4:5 + 9:16 en un solo anuncio (masajeador, 24-oct)
Sube las dos imágenes con `ads_creative_upload_media` (IMAGE → `hash`) y crea el creativo con `placement_customizations` (sin `image_hash` suelto). La primera entrada, sin ubicaciones, es la de respaldo (feed); la segunda manda a historias y reels:
```json
"placement_customizations": [
  {"image_hash": "<hash_4x5>"},
  {"image_hash": "<hash_9x16>", "publisher_platforms": ["facebook","instagram"],
   "facebook_positions": ["story","facebook_reels"], "instagram_positions": ["story","reels"]}]
```
Más `page_id`, `instagram_user_id`, `link_url`, `message`, `headline`, `description`, `SHOP_NOW` y el mismo DOF con las 9 funciones en OPT_OUT. Verifica con `ads_get_ad_preview` en un formato de feed y uno de historias.

### RECON con presupuesto por conjunto (ABO) por API
1. `ads_create_campaign` OUTCOME_SALES **sin** presupuesto ni `bid_strategy` de campaña. Meta le pone sola un `promoted_object` de catálogo a la campaña: no estorba si los conjuntos van con píxel/PURCHASE y los creativos son video o imagen propios (confírmalo con la vista previa).
2. Un `ads_create_ad_set` por ángulo con la misma audiencia: `daily_budget`, `bid_strategy: LOWEST_COST_WITHOUT_CAP`, `attribution_spec=[{"event_type":"CLICK_THROUGH","window_days":7}]`, el píxel/PURCHASE, `targeting` del país 18–65 (Advantage+) y, si se programa, `start_time` con zona (`2026-10-25T05:00:00-0500`).
3. ⚠️ **Presupuesto en COP = pesos enteros**, aunque la herramienta diga "cents": $20.000/día = `20000`. Se puso `2000000` y quedaron 4 conjuntos a $2.000.000/día (se corrigió antes del arranque). **Antes de publicar, compara con el `daily_budget` de un conjunto que ya esté corriendo** (`ads_get_ad_entities`) y vuelve a leerlo después.
4. Creativos → anuncios → `ads_get_ad_entities` con `object_state=draft` → `ads_activate_entity` con campaña + conjuntos + anuncios en `object_ids` y `publish_as_active=true`.
5. **Editar algo ya publicado** (presupuesto, nombre): `ads_update_entity` queda en borrador (`is_draft=true`) → `ads_activate_entity` con esos `object_ids` y `publish_as_active=false` → leer de vuelta. Pausar (`{"status":"PAUSED"}` solo) se aplica directo: no actives después.
6. UTM por anuncio: `utm_campaign=<prod>_recon1&utm_content=<angulo>_<formato>`. Registra cada anuncio en `REGISTRO-FORMATOS.md`.

**Permisos:** el clasificador del modo automático puede bloquear `ads_creative_upload_media` y las llamadas que crean o activan objetos en Meta. En ese caso, parar y pedirle al dueño que agregue las reglas de permitir con `/permissions` (`mcp__claude_ai_Facebook__ads_creative_upload_media`, `ads_create_ad_set`, `ads_create_creative`, `ads_create_ad`, `ads_activate_entity`). No reintentar en bucle.
