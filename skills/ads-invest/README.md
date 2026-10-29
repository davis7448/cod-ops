# ads-invest — Skill de investigación de competidores (Meta Ad Library)

Skill para **Claude Code** que automatiza la investigación de publicidad de competidores en la **Meta Ad Library** y la convierte en material accionable: bancos de creativos, ángulos/ganchos, ofertas y matrices de testeo listas para cargar en Meta.

Esta es la **versión genérica** (sin marca ni rutas fijas). Personalízala en 2 minutos con la sección [Configuración](#3-configuración).

---

## 1. Requisitos

| Requisito | Para qué | Obligatorio |
|---|---|---|
| **Claude Code** (CLI, desktop o IDE) | Ejecutar la skill | ✅ |
| **MCP de Meta Ads** con la tool `ads_library_search` | Buscar anuncios por marca/término o por `page_id`. **Requiere una cuenta de anuncios de Meta activa** (si no, la API responde error). | ✅ (vía principal) |
| **WebFetch / WebSearch** (built-in de Claude Code) | Extraer copy de las landing pages de los competidores | ✅ |
| **Python 3.8+** | Ejecutar `scripts/download_swipe_media.py` para descargar los archivos de creativos | ⬜ Solo si quieres bajar media |
| **Extensión "ad-library-toolkit"** (👉 incluida en `extension/`) | Exporta `swipe_file.json`, la **única** fuente con URLs de media descargables (la API solo da el link al anuncio, no el archivo). Ver `extension/README.md` | ⬜ Solo si quieres bajar media |
| **Obsidian** (opcional) | Navegar los entregables como un vault con grafo de enlaces | ⬜ Recomendado |

> **Nota sobre el MCP de Meta Ads:** la skill asume que tu Claude Code ya tiene conectado un MCP server que expone `ads_library_search` (y opcionalmente las demás tools de Meta Marketing API). Sin una cuenta de anuncios activa, la Ad Library API devuelve error en lugar de resultados.

---

## 2. Instalación

1. Copia la carpeta **completa** a tu directorio de skills de Claude Code:
   - **Global (todas las sesiones):** `~/.claude/skills/ads-invest/`
     - Windows: `C:\Users\<TU_USUARIO>\.claude\skills\ads-invest\`
     - macOS/Linux: `~/.claude/skills/ads-invest/`
   - **Por proyecto:** `<proyecto>/.claude/skills/ads-invest/`
2. Asegúrate de que `SKILL.md` quede directamente dentro de `ads-invest/` (no en una subcarpeta).
3. Reinicia/abre Claude Code. La skill se activará sola cuando pidas investigar competencia, o invócala con `/ads-invest`.

Estructura del paquete:
```
ads-invest/
├── SKILL.md                       ← la skill (cópiala a ~/.claude/skills/ads-invest/)
├── README.md                      ← este archivo
├── scripts/
│   └── download_swipe_media.py    ← descarga media desde swipe_file.json
├── extension/                     ← extensión de navegador para exportar swipe_file.json
│   ├── manifest.json, inject.js, content.js, popup.html, popup.js
│   └── README.md                  ← cómo crearla, cargarla y usarla
└── templates/
    ├── REGISTRO-INVESTIGACION.md
    ├── COPY.md
    ├── BANCO-ANGULOS.md
    └── RANKING.md
```

---

## 3. Configuración

Abre `SKILL.md` y reemplaza estos marcadores por tus valores (o díselos a Claude en la primera sesión):

| Marcador | Significado | Ejemplo |
|---|---|---|
| `<CARPETA_TRABAJO>` | Carpeta raíz donde va todo el output | `D:\ADS INVEST` · `~/ads-invest` |
| `<MARCA>` | Tu marca / e-commerce | `Acme` |
| `<PAIS>` | Tu mercado principal (ajusta las palancas) | `Colombia`, `México`, `España` |
| `<DESCARGAS>` | Donde la extensión exporta `swipe_file.json` | `C:\Users\<TU_USUARIO>\Downloads` |

**Palanca por mercado:** la skill prioriza la oferta y la logística. En mercados con desconfianza al pago online (gran parte de LATAM), el **pago contra entrega** suele ser la palanca #1; ajústalo a tu `<PAIS>`.

---

## 4. Uso

- Pídelo en lenguaje natural: *"investiga competidores de mi producto X en la Ad Library"*, *"arma el banco de ángulos"*, *"siguiente ronda"*.
- O invoca `/ads-invest`.

**Flujo de una ronda:**
1. Claude lee `REGISTRO-INVESTIGACION.md` y omite lo ya cubierto.
2. Busca competidores nuevos con `ads_library_search` (saca page_ids y volúmenes).
3. Clasifica (directo / adyacente / excluir) y rankea por longevidad + relevancia.
4. Extrae copy de los mejores vía WebFetch.
5. (Opcional) Descarga media con el script Python.
6. Genera/actualiza los entregables y el registro.

**Regla de oro:** la investigación es incremental. Cada ronda AÑADE cobertura; nunca se recalienta lo ya investigado ni se crean archivos por ronda (un documento por tipo y por producto).

---

## 5. Descargar los archivos de creativos (opcional)

La Ad Library API **no** entrega el video/imagen, solo el link al anuncio. Para bajar los archivos:

1. Carga la extensión incluida en `extension/` (Chrome/Edge → `chrome://extensions` → Modo desarrollador → *Cargar descomprimida*). Pasos detallados en `extension/README.md`. Navega la Ad Library, desplázate por los anuncios y exporta el `swipe_file.json` (queda en `<DESCARGAS>\ad-library\`).
2. Ejecuta:
   ```bash
   python scripts/download_swipe_media.py --input "<DESCARGAS>/ad-library/swipe_file.json" --out "<CARPETA_TRABAJO>/<producto>/media" --limit 20
   ```
3. El script descarga la media y genera un `INDEX-CREATIVOS.md` con la ficha de cada creativo.

> ⚠️ Las URLs del CDN de Facebook **caducan en horas**: exporta y descarga el mismo día.

---

## 6. Privacidad / alcance

- La skill solo consulta datos **públicos** de la Meta Ad Library y landing pages públicas.
- No publica ni modifica campañas por sí sola; produce documentos de investigación.
- Si tu MCP de Meta Ads incluye tools de escritura (crear campañas, etc.), esos son ajenos a esta skill.
