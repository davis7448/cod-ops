# Clips con IA en Magnific Spaces (el usuario genera, Claude prepara)

Probado el 2026-10-23 con un masajeador de cabeza: 9 clips 9:16 de 5 s para una RECON. Sirve cuando el material del proveedor no alcanza para mostrar el producto en uso (falta la toma de la persona poniéndoselo, la reacción, el unboxing o el primer plano del mecanismo).

**Por qué así:** el plan del usuario puede tener generación **ilimitada en la app de Magnific**, pero esa ventaja no aplica a las llamadas del MCP (`account_balance` → `unlimitedAppliesHere: false`). Si Claude genera, gasta créditos. Por eso Claude **arma el Space** (imágenes, prompts, modelo, conexiones) y **el usuario le da generar** en la app.

## Pasos
1. **Imágenes iniciales fieles al producto (Codex).** Una por clip, 1080×1920, **sin texto**, con las fotos reales del producto como referencia (`-i packshot.png -i foto_real.jpg`). Describe el producto con sus rasgos concretos (color, piezas, botones) y termina con "No logos, no text". Revisa una hoja lado a lado contra la foto real: si el producto cambia, regenera. Las imágenes de la landing **no sirven** como imagen inicial si traen texto quemado.
2. **Subirlas a Magnific:** `creations_request_upload` (mimeType y `count`) → `curl -X PUT -H "Content-Type: image/png" --data-binary @archivo "<proxyUploadUrl>"` por archivo (200) → `creations_finalize_upload` con `uploads:[{path,fileName}]` → identificadores.
3. **Crear el Space:** `spaces_create` (una vez) → link `webUrl` para el usuario.
4. **Nodos en una sola llamada** (`spaces_create_node`, hasta 20): por clip, un nodo `creation` (`data.creationIdentifier`) y un `video-generator` a su derecha con `data.slug`, `data.duration`, `data.aspectRatio: "9:16"`, `data.resolution` y `data.prompt`. Nombres: `"N — <escena> (inicio)"` y `"Scene N — <acción>"`.
5. **Conexiones** (`spaces_add_connection`, una llamada): `creation.output` → `video-generator.first-frame`. **No** uses `references` a la vez que `first-frame` (son excluyentes en la mayoría de modelos).
6. **Verificar** un nodo con `spaces_get_nodes` (modelo, duración, prompt y la conexión).
7. **No correr nada.** Dale al usuario el link y la tabla de clips. Si el modelo elegido no está entre sus ilimitados, que lo cambie en cada nodo.
8. Cuando el usuario avise, descarga los clips, haz QA con fotogramas (el producto no se deforma, no aparece texto inventado) y móntalos. **Revisa también el último segundo de cada clip**, no solo el centro: Kling tiende a deformar el producto al final (masajeador, 24-oct: en el clip de abrir la caja el producto terminó convertido en un masajeador de cuello; se usaron solo los primeros 2,5 s). Hoja de QA: `fps=2,scale=180:320,tile=10x1` sobre el clip entero. Anota en `GUIONES.md` qué tramo sirve de cada clip. Después móntalos con la función `build` ([montaje-ffmpeg.md](montaje-ffmpeg.md)) como escenas `f` (pantalla completa).

## Modelo
- Elegir con `spaces_node_types_search` (`video-generator`) y leer duraciones con `video_models_list`. Para clips mudos con primer fotograma, Kling 2.5 (5 o 10 s, 720p/1080p) funcionó bien de base. Con 720p, Kling 2.5 exige primer fotograma.
- El audio va aparte (voz OmniVoice + música propia): pide clips **sin sonido**.

## Prompt de cada clip (en inglés)
Una sola acción, corta y física, que **explique el producto**:
> "The woman places the light-blue band around her forehead with both hands, presses the velcro closed at the side, then lowers her hands, closes her eyes and smiles as she leans back into the sofa. The band, the tube and the controller keep exactly the same shape and color. Static camera. Realistic, natural motion. No text."

Reglas: el sujeto descrito igual que en la imagen inicial · "keep exactly the same shape and color" para el producto · cámara estática o empuje lento · "No text" (y "no letters on the screen" si hay una pantalla) · nada de claims en la escena.

## Qué clips pedir (lista de chequeo)
- Gancho de dolor sin producto (la persona con la molestia).
- **Cómo se pone o cómo se usa** (obligatorio: es lo que hace que el anuncio explique).
- **Primer plano del mecanismo** (lo que hace el producto).
- Reacción o disfrute (primera vez).
- Uso por otra persona o regalo, si hay ángulo de identidad.
- Unboxing (caja real), si hay formato de unboxing.
- Primer plano del control o las piezas (tutorial).

## Lanzar nodos en el navegador (28-oct-2026)
- Si el clic por coordenadas no selecciona el nodo (pasa después de cambiar el tamaño del viewport), usar `browser_snapshot` → `browser_click` con el `ref` del grupo del nodo (su nombre) → `browser_press_key Control+Enter`. Verificar con `spaces_get_nodes` que `workflowStatus=running`.
- Antes de usar Magnific, devolver el viewport a 1280×980: si quedó en 1080×1920 (por los subtítulos), el login queda fuera de la pantalla y el usuario no puede escribir.
- Parchear el `creationIdentifier` de un nodo de imagen ya conectado no siempre refresca el lienzo; es más seguro crear un par nuevo (imagen → video).
