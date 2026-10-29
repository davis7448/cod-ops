# REGISTRO DE INVESTIGACIÓN — <MARCA> (control de cobertura)

> Propósito: dejar constancia de TODO lo ya investigado para OMITIR en próximas rondas y solo buscar material NUEVO.
> Carpeta base: `<CARPETA_TRABAJO>\` — vault de Obsidian (índice: [[INICIO]]).
> Estructura por producto: `<producto>\` con COPY.md, BANCO-ANGULOS.md, RANKING.md, ANALISIS-BIBLIOTECAS.md, INDEX-CREATIVOS.md, media\.
> Regla de archivos: **un documento por tipo y por producto** — cada ronda se AÑADE, no se crean archivos por ronda.
> Última actualización: AAAA-MM-DD.

Productos cubiertos:
1. **<producto-1>** — <url del producto>

Fuentes usadas: Meta Ad Library API (`ads_library_search`) + WebFetch a landings + `swipe_file.json` (ad-library-toolkit).

---

## ✅ <PRODUCTO> — anunciantes ya analizados (OMITIR en próxima ronda)

| Anunciante | page_id | Biblioteca pulleada | Nota |
|-----------|---------|:---:|------|
| Ejemplo SA 🇨🇴 | 000000000000000 | ✅ (NN ads) | directo |

## 🔗 ANUNCIOS YA ENTREGADOS — <PRODUCTO> (NO volver a reportar estos ad_id)

> Control a nivel de ANUNCIO, no de anunciante. Un competidor ya cubierto puede volver
> a aparecer con creativos NUEVOS: eso sí se reporta. Lo que nunca se repite es un ad_id.
> Evidencia: PROBADO (relanzado o +90d continuos) · INDICIO (volumen sin longevidad) · SIN PROBAR (lanzamiento reciente).

| ad_id | Anunciante | page_id | Gancho | Evidencia | Ronda |
|-------|-----------|---------|--------|-----------|-------|
| 000000000000000 | Ejemplo SA | 000000000000000 | Titular del anuncio | PROBADO 87d | R1 |

### Bibliotecas (`view_all_page_id`) ya entregadas
- `000000000000000` Ejemplo SA — https://www.facebook.com/ads/library/?view_all_page_id=000000000000000

### Creativos descargados (NO volver a traer) — library IDs
- 01 ... — `library_id`

### Landings con copy ya extraído (en COPY.md)
...

### Búsquedas API ya ejecutadas (no repetir)
`término 1` · `término 2` · page_ids: ...

---

## 🔜 PENDIENTE para próximas rondas (material NUEVO a buscar)
- Bibliotecas aún NO pulleadas: ...
- Mercados/idiomas poco explorados: ...
- Términos sugeridos no usados: ...

---

## Regla para la IA en próximas rondas
1. Antes de buscar, leer este registro.
2. **Omitir** todo page_id, library ID y término ya listados.
3. Solo reportar anunciantes/creativos NUEVOS.
4. Al terminar, **actualizar este archivo**.
