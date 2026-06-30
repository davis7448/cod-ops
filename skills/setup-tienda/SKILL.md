---
name: setup-tienda
description: Configura una tienda COD nueva en el proyecto actual — crea tienda.config.json, copia el motor del dashboard y deja todo listo para las skills cod-ops. Úsala al abrir una tienda nueva o al instalar el plugin en un proyecto.
---

# Setup de Tienda COD 🏪

Onboarda una tienda nueva para el sistema `cod-ops`. Al terminar, el proyecto tiene su `tienda.config.json`, el motor del dashboard y todo listo para `/cod-ops:seguimiento`.

## Cuándo usar
- Primera vez que se instala `cod-ops` en un proyecto/tienda.
- Cuando el usuario quiere "ver otra tienda" con el mismo sistema.

## Pasos

1. **Ubicar la carpeta de contabilidad** del proyecto (crear `contabilidad/` si no existe).

2. **Copiar los templates del plugin** a esa carpeta:
   - `templates/tienda.config.json` → `contabilidad/tienda.config.json`
   - `templates/build_data.py` → `contabilidad/build_data.py`
   - `templates/build_dashboard.py` → `contabilidad/build_dashboard.py`
   Los templates están en la raíz del plugin (`${CLAUDE_PLUGIN_ROOT}/templates/`). Si no resuelves la ruta, búscalos en el repo del plugin instalado.

3. **Entrevistar al usuario** para llenar `tienda.config.json` (pregunta solo lo que no puedas inferir; usa MCPs para autocompletar):
   - **Tienda:** nombre, Shopify domain, Meta business + account_id → confirma con `ads_get_ad_accounts` (Meta MCP) y `get-shop-info` (Shopify MCP).
   - **Productos:** familias y sus keywords (substrings que aparecen en la columna PRODUCTO de Dropi).
   - **Costos:** confirmación por despachada, comisión %, impuesto %, flete última milla.
   - **Columnas Dropi:** confirmar que los encabezados del export coinciden con `dropi_columnas` (pedir un reporte de muestra y leer la fila de encabezados).
   - **Reportes:** rutas de los xlsx de Dropi.

4. **Cargar datos mensuales iniciales:**
   - Pauta por producto: jalar de Meta MCP (`ads_get_ad_entities`, mapear campañas a productos por nombre).
   - APPS y SHOPIFY_ORD: pedirlos al usuario o jalar órdenes de Shopify MCP.
   - Marcar `provisional` los meses con >5% en tránsito.

5. **Generar el dashboard:**
   ```bash
   cd contabilidad
   python3 build_data.py        # lee tienda.config.json → data.json
   python3 build_dashboard.py   # data.json → dashboard.html
   ```
   Validar que el INGRESO calculado cuadre contra el Sheet de contabilidad del usuario (mes maduro). Si no cuadra, el mes está subregistrado — revisar.

6. **Guardar en memoria de proyecto** los números clave (AOV, break-even, targets por producto) para arranques en frío.

## Resultado
- `contabilidad/tienda.config.json` lleno y validado.
- `dashboard.html` generado y abierto.
- Las skills `/cod-ops:*` listas para operar esta tienda.

> El método es idéntico para cualquier tienda COD; lo único que cambia es el config. Para una tienda nueva, repite esta skill en su proyecto.
