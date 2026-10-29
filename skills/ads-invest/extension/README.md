# Ad Library Toolkit — extensión de navegador (swipe file)

Extensión mínima (Chrome/Edge, Manifest V3) que **captura los anuncios que ves en la Meta Ad Library** y los exporta como `swipe_file.json` con las URLs de media. Es la pieza que le da a la skill `ads-invest` los **archivos** de creativos (la API de la Ad Library solo entrega el link al anuncio, no el video/imagen).

## Cómo funciona (en breve)
1. `inject.js` corre dentro de la página de la Ad Library y "escucha" las respuestas que el navegador **ya recibe** al desplazarte (hookea `fetch`/`XHR`). Solo lee datos **públicos** que la página cargó; no automatiza navegación ni login.
2. Extrae de cada anuncio: marca, copy, landing, link al anuncio y las URLs de **video/imagen**.
3. `content.js` los deduplica y acumula en el almacenamiento local.
4. El popup (`popup.html`) muestra el contador y exporta `swipe_file.json`.

## Archivos
```
extension/
├── manifest.json   ← define la extensión (MV3)
├── inject.js       ← interceptor (MAIN world)
├── content.js      ← dedupe + almacenamiento (ISOLATED world)
├── popup.html      ← panel
└── popup.js        ← exportar / limpiar
```

## Instalar (cargar descomprimida)
**Chrome / Edge / Brave:**
1. Ve a `chrome://extensions` (o `edge://extensions`).
2. Activa **Modo de desarrollador** (arriba a la derecha).
3. Clic en **Cargar descomprimida** (*Load unpacked*) y selecciona esta carpeta `extension/`.
4. Aparece "Ad Library Toolkit". Fíjala a la barra si quieres.

> No necesita compilación ni `npm`: son archivos planos. Manifest V3 funciona en Chrome 111+ / Edge equivalentes.

## Usar
1. Abre **https://www.facebook.com/ads/library/** y busca la marca/categoría.
2. **Desplázate** por los anuncios que te interesen (cada anuncio con media que cargue se captura solo).
3. Abre el popup de la extensión → verás el contador subir → **Exportar swipe_file.json**.
4. Guárdalo en `<DESCARGAS>/ad-library/swipe_file.json` (el popup ya sugiere esa subcarpeta).
5. Descarga la media con el script de la skill:
   ```bash
   python ../scripts/download_swipe_media.py --input "<DESCARGAS>/ad-library/swipe_file.json" --out "<CARPETA_TRABAJO>/<producto>/media" --limit 20
   ```

> ⚠️ Las URLs del CDN de Facebook **caducan en horas**: exporta y corre el script el mismo día.

## Notas / límites
- Meta cambia de tanto en tanto la estructura de sus respuestas. Si un día deja de capturar, revisa la consola de la página (F12) — el interceptor imprime `[ad-library-toolkit] interceptor activo`. El parser de `inject.js` recorre el JSON buscando nodos con `snapshot`; si cambian los nombres de campo (`video_hd_url`, `images[].original_image_url`, etc.), ajústalos ahí.
- Captura **solo lo que tú navegas**: no hace scraping masivo ni paginación automática. Es un *swipe file* asistido.
- Uso previsto: investigación de creativos propios sobre datos públicos. Respeta los Términos de Meta y la normativa aplicable.
