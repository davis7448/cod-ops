# Trasplantes: rehacer un video ganador de la competencia con material propio

Probado con el irrigador bucal (27–29 oct 2026): 3 trasplantes publicados en la One CBO (`TRASPLANTES-R2.md` y `REGISTRO-FORMATOS.md` del irrigador).

Un trasplante copia la **estructura** de un video que escala: el gancho, el orden de los planos, los tiempos y el remate. Los planos y la voz son nuestros. Del video ajeno no se publica ni un fotograma.

## Qué se puede usar
| Material | ¿Se usa? | Condición |
|---|---|---|
| Video de la competencia (Ad Library o TikTok) | Solo para estudiarlo | Se descarga, se transcribe y se saca la lista de planos |
| Clips de fábrica | ✅ | El mismo clip aparece en varios vendedores, sin creador ni marca. **el dueño lo confirma** (en el irrigador: las tomas del modelo dental con el chorro) |
| Voz de un anuncio ajeno clonada con OmniVoice | ✅ solo con autorización escrita | Se registra en `media/videos/voces/FICHAS.md`. Si habla una creadora, la autorización tiene que cubrirla a ella |
| Creador o UGC ajeno, aunque esté reeditado o doblado | ❌ | Son derechos de terceros y hay riesgo de reportes de propiedad intelectual |

## Pasos
1. **Elegir referencias.** En la Ad Library, solo videos activos ordenados por impresiones, buscando el vendedor que escala: el que lleva muchos días con muchos videos distintos y el mismo copy. Bajarlas con `video.src` + curl el mismo día ([tecnico-busqueda.md](tecnico-busqueda.md)).
2. **Transcribir:** mlx_whisper `whisper-large-v3-turbo` en `~/.venvs/voz` → `r2_txt/transcripciones.json`. Hacer hojas de planos con ffmpeg (un fotograma cada ~1,5 s).
3. **Ficha del trasplante:** una tabla por video (`#`, segundos, voz reescrita, plano y material nuestro). Al reescribir se quitan los claims de salud que no tenemos. Se va en `<producto>/TRASPLANTES-Rn.md`.
4. **Planos propios:**
   - Persona: imagen de Codex fiel al producto, animada con Kling 2.5 en Magnific Spaces en modo ilimitado ([video-ia-spaces.md](video-ia-spaces.md)). **Continuidad:** si la persona lleva brackets, gafas o una prenda, todas sus imágenes iniciales tienen que llevarlo (el dueño lo detectó en T2). Nada de imágenes fijas de la persona: todo animado.
   - Producto: clips de fábrica en `media/videos/stock_fabrica/`, escalados a 1080×1920.
5. **Voz:** OmniVoice con `voice_clone_prompt` de 15–17 s de la referencia autorizada ([voces-omnivoice.md](voces-omnivoice.md)). Chrome tiene que estar cerrado (con 8 GB se cuelga), y para cerrarlo se pide permiso. Se validan las tomas con Whisper (similitud ≥ 0,9). Si una toma cambia una frase, se regenera solo esa frase y se empalma.
6. **Montaje:** la función `build` de [montaje-ffmpeg.md](montaje-ffmpeg.md), con subtítulos PNG palabra por palabra. Los subtítulos se quitan mientras se ve la tarjeta de precio.
7. **Nombre:** `<PROD>_<ÁNGULO>_<FORMATO>_TRASPLANTE_H<n>_v<n>`. UTM: `utm_content=<angulo>_<formato>_trasplante`.
8. **Subida:** como en [montaje-ffmpeg.md](montaje-ffmpeg.md) § Subida, pero dentro del conjunto FLEX de la One CBO activa (`ads_create_ad` con `creative_id`). El copy es el copy nativo del producto con el gancho del video. Se muestran las vistas previas y **se publica solo con el sí del dueño**.
9. **Registro:** se agregan filas 🆕 en `REGISTRO-FORMATOS.md` y la lectura se hace a los 3–5 días con los umbrales de `/cod-ops:one-cbo`.
