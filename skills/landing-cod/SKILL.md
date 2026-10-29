---
name: landing-cod
description: Monta la landing de un producto COD en Shopify (tienda COD) de punta a punta — packshot fiel con Codex, 7 piezas 1080×1920 por estilo de categoría, GIFs del video del proveedor, subida al CDN, producto con precio/costo, packs en Releasit, activación, publicación y revisión en celular. Úsala SIEMPRE que el usuario pida crear o rehacer la landing, la página de producto, las imágenes de la landing, los packs/ofertas de cantidad de Releasit, o "subir el producto a la tienda".
---

# Landing COD en Shopify (tienda COD)

Pipeline probado con **Postura360** (2026-10-08, estilo clínico) y **Marcadores Mágicos de Figuras** (2026-10-09, kawaii pastel). Entrada: la investigación de `ads-invest` (`<producto>/PRODUCTO.md` + Artifact, sección "Estructura de la landing" y "Claims"). Sin producto verificado no se monta landing.

> **Primer paso:** lee `tienda.config.json`:
> - `{SHOPIFY_SHOP}` = `tienda.shopify_domain` (sin `.myshopify.com`)
> - `{DOMINIO}` = `tienda.shopify_public`
> - `{SHOPIFY_PUBLICATION_ID}` = `creativos.shopify_publication_id`
> - `{PLANTILLA_CLINICA_GID}` = `creativos.plantillas.clinica`
> - `{PLANTILLA_KAWAII_GID}` = `creativos.plantillas.kawaii`
> - `{CARPETA_CREATIVOS}` = `creativos.carpeta`
>
> Tienda `{SHOPIFY_SHOP}` · dominio {DOMINIO} · COP · venta contra entrega con Releasit.
> Tienda online: `{SHOPIFY_PUBLICATION_ID}`.
> Archivos en `{CARPETA_CREATIVOS}/<producto>/media/landing/`.

## Reglas no negociables
1. **Producto fiel a la foto real.** Codex recibe SOLO fotos reales del producto como referencia (nunca renders de competidores). Toda pieza se compara contra la foto: forma, color, piezas, proporciones.
2. **Estilo según la categoría**, no uno fijo: salud/ortopedia → clínico (blanco, navy, diagramas, sin caricatura); papelería/regalo → kawaii pastel; hogar/decoración → cálido lifestyle. Decide y anótalo en `PRODUCTO.md` antes de generar.
3. **Sin precio "antes" ficticio** (riesgo SIC): `compareAtPrice: null`. El único tachado permitido es el de Releasit (suma real de unidades).
4. **Claims:** solo los ✅ de `PRODUCTO.md`. Nada de curar/corregir/garantizar.
5. **Hook SDD:** las salidas de codex/ffmpeg a `>/dev/null 2>&1`, nunca a archivos de log. El HTML de la descripción se escribe en el scratchpad (con escotilla; ver `ads-invest/references/entrega-artifact.md`).

## Pipeline

### 1. Packshot
- `codex exec --skip-git-repo-check -s workspace-write -C <dir> -i foto1.jpg -i foto2.jpg -- "Use your image generation tool to create a clean e-commerce packshot of EXACTLY this product (same shape, colors, parts)… copy the generated image into the current working directory as packshot.png"` (`-i` es variádico: el prompt va después de `--`).
- Valídalo contra la foto real (hoja lado a lado con ffmpeg `hstack`). Si cambia algo, regenera.

### 2. Las 7 piezas (1080×1920, en paralelo)
Estructura base (adáptala a la sección "Estructura de la landing" del Artifact): 01 hero/gancho · 02 problema o momento · 03 cómo funciona/qué incluye · 04 beneficios/zonas · 05 uso en la vida real · 06 para quién/regalo · 07 cómo se usa o tallas/medidas.
```bash
cd <dir>/media/landing
for i in 01 02 03 04 05 06 07; do
  codex exec --skip-git-repo-check -s workspace-write -C "$PWD" -i packshot.png -i ref_real.jpg -- \
    "Use your image generation tool… vertical 1080x1920, <estilo>, Spanish text: '<copy de la pieza $i>'… copy the generated image into the current working directory as mm-$i.png" >/dev/null 2>&1 &
done; wait
```
Escribe un prompt distinto por pieza (copy exacto en español, entre comillas, corto).

### 3. Control de calidad (pieza por pieza, con Read de la imagen)
- Producto idéntico al packshot (sin piezas inventadas ni deformes).
- Ortografía y tildes del texto en español (Codex se equivoca: corrige y regenera).
- **Uso correcto del producto** (marcadores: salió una profe escribiendo en un tablero blanco → falso, son marcadores de papel → regenerar).
- Ningún claim ❌, ningún precio inventado, ningún logo ajeno.

### 4. GIFs del video del proveedor
```bash
ffmpeg -y -ss <ini> -t <dur> -i prov_v1.mp4 -vf "delogo=x=..:y=..:w=..:h=..,crop=W:H:X:Y,fps=12,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer" gif_01.gif
```
fps 10–12, 2,5–3,5 s, ≤ ~3 MB. Recorta (o `delogo`) el texto chino y cualquier marca ajena. No uses videos del proveedor con otra marca en la caja.

### 5. Conversión a JPG
`ffmpeg -y -i mm-01.png -q:v 3 producto-01-hero.jpg` (nombres descriptivos: también son el alt y el SEO).

### 6. Subida al CDN de Shopify
1. `stagedUploadsCreate` (resource `IMAGE`, `httpMethod: POST`, filename, mimeType, fileSize) → por archivo: `url`, `resourceUrl` y `parameters`.
2. Sube cada archivo con curl multipart (los `parameters` van como `-F` **en orden**, el archivo al final). Pasa los parámetros con un heredoc JSON por stdin a `python3 -I`, que arma y ejecuta el curl (no escribir archivos):
   ```bash
   python3 -I - <<'EOF'
   import json,subprocess
   cfg=json.loads('''<JSON con [{file, url, params:[{name,value}]}]>''')
   for f in cfg:
       cmd=['curl','-s','-o','/dev/null','-w','%{http_code}',f['url']]
       for p in f['params']: cmd+=['-F',f"{p['name']}={p['value']}"]
       cmd+=['-F',f"file=@{f['file']}"]
       print(f['file'],subprocess.run(cmd,capture_output=True,text=True).stdout)
   EOF
   ```
   Debe responder **201**.
3. `fileCreate` con `originalSource = resourceUrl`, `contentType: IMAGE` y `alt` → espera `fileStatus: READY` → saca las URLs `cdn.shopify.com/s/files/...` (query `files(query:"filename:…")` → `image.url`).

### 7. Producto
- `productCreate` en **DRAFT** con `title`, `handle`, `descriptionHtml` y `media`.
- ⚠️ **Galería = SOLO imágenes cuadradas (1:1)** (packshot cuadrado; si es 4:5, se pasa a cuadrado con un fondo difuminado: `[0]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,boxblur=30:2[bg];[0]scale=-1:1080[fg];[bg][fg]overlay=(W-w)/2:0`). Las piezas 9:16 van **solo en la descripción**. El tema ajusta la caja de la galería a la imagen más alta: con una 9:16 adentro, el título, el precio y el botón quedan por debajo del primer pantallazo (marcadores, 2026-10-09). Para sacar media de la galería sin borrarla: `fileUpdate(files:[{id, referencesToRemove:[productId]}])`. Meta a 390×844: el título, el botón y el precio quedan antes de 844 px.
- ⚠️ **Portada = titular + precios dentro de la imagen** (pedido del dueño, 2026-10-09). El precio suelto del tema "queda al aire", así que se oculta solo en esa página desde el `<style>` de la descripción (`.product__info-container .price{display:none!important}`). La portada 1080×1080 se compone en HTML con Playwright (`setContent` + screenshot) y no con Codex, para que los precios y la ortografía salgan exactos. Arriba, una franja clara con el kicker, el titular y 3 tarjetas de pack (el del medio resaltado como "MÁS ELEGIDO"). Debajo, el **producto grande** ocupando unos 2/3 del lienzo, con el mecanismo visible (marcadores: las puntas y las líneas con figuras), y abajo la píldora "Envío gratis · Pagas al recibir". Los errores que ya pasaron: producto pequeño en una tarjeta central (se ve chiquito en el celular) y zoom excesivo que corta lo que vende. Plantilla: `marcadores-magicos/media/landing/marcadores-portada-precios-v3.png`.
  - **Margen de seguridad:** el tema recorta unos píxeles de cada borde en la galería del celular. El titular y las tarjetas deben dejar **al menos 120 px libres a cada lado** del lienzo de 1080 (en el taladro, un titular de 72 px de ancho completo perdió la "S" de "Su"; con 60 px quedó bien). Mídelo antes de la captura: `document.querySelector('h1').scrollWidth` contra el ancho del texto real, o mira la captura a 390 px.
  - **Para 2 packs** (taladro, 2026-10-14) se usan 2 tarjetas de unos 370 px; el de 2 unidades va resaltado con "MÁS ELEGIDO · PARA HERMANOS". Plantilla: `juguete-taladro/media/landing/taladro-portada-precios-v2.png`.
  - Para reemplazar la portada de un producto ya creado: `stagedUploadsCreate` → curl → `productCreateMedia` con la nueva → `fileUpdate(referencesToRemove)` de la vieja → `productReorderMedia` con la nueva en la posición `"0"`.
- ⚠️ **Tipografía:** la fuente del tema (Assistant de 15 px en gris) se ve plana y pequeña. La `descriptionHtml` arranca con un bloque `<style>` que importa Google Fonts según el estilo (kawaii: `Baloo 2` 800 para los títulos y `Nunito` para el cuerpo; clínico: algo sobrio como `Manrope`). Ese bloque fija el cuerpo en 17,5 px con color oscuro y line-height 1,6, h2 en 27 px, el precio h1 en 36 px, `.product__title h1` en 28 px, `.price-item` en 24 px y en negrita, imágenes con `border-radius:18px` y el botón de Releasit en 19 px. Todo con `!important`, porque el tema y los estilos en línea mandan. Shopify conserva el `<style>`. Plantilla: la descripción de Marcadores (gid {PLANTILLA_KAWAII_GID}).
- `descriptionHtml`: copia la estructura de la plantilla de Postura360 (gid {PLANTILLA_CLINICA_GID}) o de Marcadores (gid {PLANTILLA_KAWAII_GID}): banda "ENVÍO GRATIS Y PAGO CONTRA ENTREGA", cada pieza `<img>` centrada con su `<h2>` y párrafo, precio en `<h1>`, y el botón de Releasit **varias veces** (después del hero, a mitad y al cierre):
  ```html
  <div class="_rsi-buy-now-button _rsi-buy-now-button-shaker _rsi-buy-now-button-with-subtitle _rsi-buy-now-button-product _rsi-buy-now-button-shaker-enabled" id="_rsi-buy-now-button" data-animation-type="pulse" style="...">
    <span>Comprar ahora<span class="_rsi-buy-now-button-subtitle">🚚 Pagas al recibir · Envío gratis</span></span></div>
  ```
- `productVariantsBulkUpdate`: `price`, `compareAtPrice: null`, `inventoryPolicy: CONTINUE`, `inventoryItem: {cost, tracked: false}`.

### 8. Packs en Releasit (navegador)
Shopify admin → Apps → **Releasit COD Form** → Impulsor de Ventas → Ofertas de Cantidad → "Añadir oferta". El selector acepta productos en borrador.
- Cierra primero el aviso "Actualización disponible" con la X (tapa los clics). No actualices de versión.
- Cada tier: lápiz → Título, Cantidad, Tipo de descuento **"Valor fijo"**, Valor (**descuento TOTAL** del tier, no por unidad), etiqueta, "Preseleccionar" en el pack principal → ✓.
- **Bug:** al cambiar a "Valor fijo" el valor se resetea a 0. Reabre el tier → clic en "Valor del descuento" → Cmd+A → escribe tecla por tecla → Tab → ✓. Verifica en la vista previa el tachado + el nuevo precio.
- Tier 1: título claro y etiqueta vacía (quita el "Ahorra 0%").
- "Guardar" arriba → "Ajustes guardados".
- Ejemplo marcadores: 1 = $59.900 · 2 = $89.900 (descuento $29.900, preseleccionado) · 3 = $119.900 (descuento $59.800).

### 9. Activar y publicar (con el visto bueno del usuario)
```graphql
mutation{ productUpdate(product:{id:"<gid>",status:ACTIVE}){product{status} userErrors{message}}
  publishablePublish(id:"<gid>",input:[{publicationId:"{SHOPIFY_PUBLICATION_ID}"}]){userErrors{message}} }
```
Sin `publishablePublish` el producto ACTIVO no aparece en la tienda.

### 10. Revisión en celular
Playwright a **390 px** de ancho sobre `https://{DOMINIO}/products/<handle>`: screenshots de toda la página. Revisa que carguen las imágenes, que el botón de Releasit abra el formulario con los packs y el preseleccionado correcto, y que no haya precio "antes".

### 11. Cierre
- Si es familia nueva: alta en `tienda.config.json` con `/cod-ops:setup-tienda` (metas estimadas).
- Anota en `ads-invest/INICIO.md` el link de la landing, el gid, el handle, los packs y la carpeta de imágenes.
- Siguiente paso: creativos (`ads-invest` Regla 5) y campaña por API (`/cod-ops:one-cbo`).
