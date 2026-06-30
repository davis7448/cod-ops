# cod-ops 🦞📦

Sistema operativo para e-commerce **contra-entrega (COD)** en Colombia, empaquetado como plugin de Claude Code. Reúne el método de operar una tienda — rentabilidad, escalado de Meta Ads (One CBO), ruteo de transportadoras, parser logístico Dropi/última milla y un dashboard — de forma **reutilizable entre tiendas**.

> Principio de diseño: **el método es genérico, los datos son por tienda.** Las skills y el motor del dashboard no tienen nada hardcodeado; todo lo específico de un negocio vive en `tienda.config.json`.

## Qué incluye

**Skills (slash commands):**
| Comando | Rol |
|---------|-----|
| `/cod-ops:setup-tienda` | Onboarda una tienda nueva (crea config + dashboard) |
| `/cod-ops:seguimiento` | Cadencia operativa diaria/semanal/quincenal/mensual (la batuta) |
| `/cod-ops:one-cbo` | Decisiones de escalado/desescalado en Meta (por CPA) |
| `/cod-ops:rentabilidad` | Break-even, target CPA, ROAS real, cierre contable |
| `/cod-ops:ruteo` | Optimización de transportadoras por zona |
| `/cod-ops:reportes-logistica` | Parser Dropi + última milla, dedup de recreaciones |

**Motor del dashboard** (`templates/`): `build_data.py` (reportes → `data.json`) + `build_dashboard.py` (`data.json` → `dashboard.html` interactivo, 2 páginas) + `tienda.config.json` (la plantilla de config).

## Instalación

```
/plugin marketplace add /Users/danielusechemarin/cod-ops
/plugin install cod-ops@cod-ops
```
(o apunta el marketplace a un repo git remoto si lo subes a GitHub).

## Uso en una tienda nueva

1. Abre el proyecto de esa tienda en Claude Code.
2. Corre `/cod-ops:setup-tienda` → entrevista, autocompleta con los MCPs (Meta/Shopify) y genera `contabilidad/tienda.config.json` + `dashboard.html`.
3. Opera con `/cod-ops:seguimiento` (orquesta las demás).

Cada cierre: actualizas `mensual.pauta/apps/shopify_orders` y `targets` en el config, regeneras el dashboard. El plugin no corre nada solo — tú controlas el ritmo.

## Requisitos
- MCPs conectados: Meta Ads, Shopify (y opcional NotebookLM para el protocolo One CBO).
- Python 3 con `openpyxl` para el motor del dashboard.
- Reportes de Dropi exportados en `.xlsx`.

## Cómo está parametrizado
`tienda.config.json` controla: nombre/IDs de la tienda, familias de producto (keywords), costos del modelo, targets por producto, mapeo de columnas del reporte Dropi, estatus, rutas de reportes, datos mensuales (pauta/apps/shopify), informativo histórico y el estado del piloto de ruteo. Cambiar de tienda = cambiar de config.

## Licencia

[MIT](LICENSE) © David Camilo Useche Marín
