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

2. **Copiar TODOS los templates del plugin** a esa carpeta (`${CLAUDE_PLUGIN_ROOT}/templates/`):
   - `tienda.config.json` → `contabilidad/tienda.config.json` (el config de la tienda)
   - `build_data.py` + `build_dashboard.py` → motor del dashboard
   - `snapshot_confirmacion.py` → snapshot diario del funnel de confirmación (Chatea Pro)
   - `seguimiento_reclamos.py` → seguimiento de reclamos de rechazados
   - `gen_reclamo_rechazados.py` → genera el Excel de reclamo para el proveedor
   - `update_config_mensual.py` → escribe pauta+ventas al config (lo usa la rutina)
   Si no resuelves `${CLAUDE_PLUGIN_ROOT}`, búscalos en el repo del plugin instalado.

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

6. **Confirmación por WhatsApp (opcional, si usa Chatea Pro / UChat):**
   - Llenar la sección `chatea_pro` del config (base_url del white-label; los tags estándar suelen servir).
   - La API key va en `contabilidad/.env` como `CHATEAPRO_API_KEY` (NUNCA en el config ni en el chat). Crear `.gitignore` con `.env`.
   - Introspeccionar la cuenta (`/flow/tags`, `/flow/user-fields`, `/subscribers`) para verificar que los tags del funnel coinciden.

7. **Última milla (opcional):** si tiene operación propia, llenar `ultima_milla` (report + columnas) para detectar recreaciones cross-plataforma.

8. **Rutinas programadas (opcional pero recomendado):** crear con scheduled-tasks, adaptando los prompts de Kovia:
   - **Snapshot de confirmación** (diario) → corre `snapshot_confirmacion.py`.
   - **Actualizar dashboard** (diario) → jala pauta (Meta MCP) + ventas (Shopify MCP) del mes en curso vía `update_config_mensual.py` y regenera. Apps y reportes Dropi quedan manuales.
   Recordar al usuario darles "Run now" una vez para pre-aprobar permisos.

9. **Guardar en memoria de proyecto** los números clave (AOV, break-even, targets por producto, IDs de cuenta) para arranques en frío.

## Resultado
- `contabilidad/tienda.config.json` lleno y validado + todos los scripts.
- `dashboard.html` generado (P&G, confirmación neta, no-despacho con recreaciones, rechazados, utilidad esperada en provisionales).
- Rutinas diarias configuradas (si aplica).
- Las skills `/cod-ops:*` listas para operar esta tienda.

## Lo que es POR TIENDA (no se comparte entre tiendas)
Cada tienda tiene su propio: `tienda.config.json`, `.env` (API key Chatea), reportes de Dropi/última milla, cuenta Meta y tienda Shopify, rutinas programadas, y archivos generados (data.json, dashboard.html, reclamos_estado.csv, confirmacion_log.jsonl). El **método** (skills + scripts) es idéntico; solo cambian los datos.

> Para una tienda nueva: proyecto/conversación nueva → `/cod-ops:setup-tienda` → operar con `/cod-ops:seguimiento`.
