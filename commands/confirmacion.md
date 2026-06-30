---
description: Snapshot diario del funnel de confirmación (Chatea Pro / UChat) — lista accionable + serie histórica
---

# Confirmación de Pedidos COD 📞✅

Monitoreas el **funnel de confirmación** de una operación COD que confirma por WhatsApp con **Chatea Pro** (white-label de **UChat**). Tu trabajo es sacar la **lista accionable del día** (pedidos frescos rescatables) y acumular la serie histórica, porque el dato es efímero.

> **Primer paso:** lee la sección `chatea_pro` de `tienda.config.json` (base URL + mapeo de tags). La API key se lee del entorno (`CHATEAPRO_API_KEY`), nunca del config ni del chat.

## ⚠️ Lo que tienes que entender de los datos (crítico)
En Chatea Pro **los tags son estado ACTUAL, no un registro histórico** — cuando un pedido confirma y avanza, el bot le **quita** el tag del funnel. Comprobado: de los pedidos ya despachados en Dropi, solo ~2% conservan tags del funnel. Implicaciones:
- **NO se puede reconstruir la tasa de confirmación histórica desde los tags** (se borra). Para la tasa confiable: cruzar **Shopify generado → Dropi despachado** por teléfono (ver `/cod-ops:reportes-logistica`).
- El valor del API está en el **funnel VIVO**: cazar los pedidos frescos (<72h) antes de que mueran, y leer el **motivo** de fricción.
- Por eso se corre como **snapshot diario que se acumula**, no como un pull único.

## Cómo se modela la confirmación (tags estándar Chatea Pro)
| Concepto | Señal |
|----------|-------|
| Entró al funnel (denominador vivo) | tag `Embudo: Confirmaciones` |
| Confirmado | tag `PEDIDO CONFIRMADO` / `Ya confirmado✅` |
| Pendiente | en funnel sin tag de confirmado |
| Falta dirección (fuga #1) | tag `[Confirmaciones] Faltan datos en la dirección` |
| Valor / ciudad | campo `Valor de la compra`, `city` del subscriber |
| Llave para cruzar con Dropi | `user_id` = teléfono |

## La API (UChat)
- Base: el dominio del white-label (p.ej. `https://chateapro.app/api`). Auth `Bearer` (key en `CHATEAPRO_API_KEY`).
- `GET /flow/tags`, `GET /flow/user-fields` — introspección (paginados 10/pág).
- `GET /subscribers?page=N` — lista paginada; cada subscriber trae `tags`, `user_fields` (84+ campos), `subscribed`, `last_message_at`, `user_id` (teléfono).
- **No expone el transcript** del chat; el **último turno** del agente IA vive en el campo `[Confirmaciones] Historial del agente` (útil para diagnosticar pendientes uno a uno).
- Rate-limit agresivo: pausar ~1.2s entre páginas y reintentar 403/429 con backoff.

## Ejecución (motor `snapshot_confirmacion.py`)
```bash
cd contabilidad
set -a && . ./.env && set +a        # carga CHATEAPRO_API_KEY
python3 snapshot_confirmacion.py    # opcional: YYYY-MM-DD
```
Produce:
- `accionables_hoy.json` — la lista del día (frescos <72h, falta-dirección primero).
- `confirmacion_log.jsonl` — una línea por día (serie histórica que se construye desde hoy).

## Lectura operativa (cadencia diaria, junto a `/cod-ops:seguimiento`)
1. **Actúa sobre los frescos (<72h)** de arriba abajo; los `📍FALTA DIR` primero (pídeles el dato hoy → se despachan).
2. **Ignora la cola muerta (>7d)** — es fuga, no lista de tareas. Perseguirla no rescata.
3. **Vigila la fuga sistémica:** si "falta dirección" es recurrente, el arreglo es **aguas arriba** (capturar bien la dirección en el formulario de Shopify / flujo del anuncio), no perseguir caso a caso.
4. La **tasa de confirmación** confiable y su tendencia salen del cruce Shopify→Dropi, no del tag.

> Diagnóstico profundo de pendientes (agrupar por causa leyendo el último turno del agente): script auxiliar `diag_pendientes.py`.
