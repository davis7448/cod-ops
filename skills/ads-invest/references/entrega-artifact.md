# Entregable final: INVESTIGACIÓN CREATIVA COMPLETA (Regla 4)

Un solo Artifact por producto, mismo archivo y misma URL en cada ronda. Link en `INICIO.md` y al inicio de `LINKS.md`. Ejemplos: plantilla {ARTIFACT_REFERENCIA} · bicicleta {ARTIFACT_REFERENCIA} · marcadores {ARTIFACT_REFERENCIA}

Cargar la skill `artifact-design` antes de escribir el HTML. Formato de documento de trabajo (una columna, índice con chips, tablas con scroll propio); paleta y tipografía propias de la categoría del producto.

## Secciones obligatorias, en este orden
**A. Para la landing y los creativos**
1. Resumen (producto verificado, presentaciones, precio, costo, target CPA, posicionamiento en 2 frases)
2. Público y avatares (3–4: quién, momento, qué quiere, pack)
3. Dolores, deseos y objeciones (con respuesta)
4. Niveles de conciencia (5 niveles: qué sabe, hook, bloque de entrada, formato; dónde está la competencia y huecos)
5. Ángulos (hook, avatar, conciencia, origen, evidencia)
5b. Gemelos exactos para replicar ya
6. Estructura de la landing (8–10 bloques con copy, foto/video y origen)
7. Titulares para el hero
8. Oferta y precios (escalera de packs con target CPA; nada de "antes" ficticio)
9. Claims ❌ / ✅
10. FAQ propuesta
11. Mapa de fotos y videos del producto
12. Referencias clave
13. Coherencia anuncio ↔ landing

**B. Investigación completa**
14. Ranking · 15. Análisis por competidor (✅ copiar / ❌ ignorar) · 16. Copy textual · 17. Plan de testeo + nombres · 18. Economía unitaria · 19. Todos los anuncios entregados (R1…Rn) · 20. Bibliotecas y links de swipe · 21. Pendientes

## Escotilla SDD (HTML y JSON fuera de repos con arnés)
- El guard mira la **carpeta del archivo que se escribe**. Pide al dueño `/sdd:sdd-bypass` y crea `.sdd/bypass.json` (`reason`, `openedBy`, `expiresAt`) con Write:
  - HTML del Artifact → en el **scratchpad** de la sesión.
  - `tienda.config.json` → en `{CARPETA_TIENDA}/contabilidad/`.
- **Renovar una escotilla vencida:** no se puede sobrescribir `bypass.json`; borra la carpeta entera con `rm -r <dir>/.sdd` y vuelve a crearla con Write (vale para el scratchpad y para contabilidad).
- Si la sesión se reanudó y el scratchpad se limpió, publica con el mismo `file_path`: el tool Artifact restaura la última versión ahí.
