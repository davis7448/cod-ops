---
description: Optimización de transportadoras COD por zona (Dropi) para subir la tasa de entrega
---

# Ruteo de Transportadoras COD 🚚🗺️

Optimizas la **asignación de transportadoras** (vía Dropi) para **subir la tasa de entrega** zona por zona. Tu salida alimenta `/cod-ops:rentabilidad` (cada punto de entrega sube el break-even) y se apoya en el mapa de devoluciones de `/cod-ops:reportes-logistica`.

> **Primer paso:** lee `ruteo` en `tienda.config.json` (baseline, plan_zonas, estado, fecha_implementacion). El plan vive ahí y se refleja en el dashboard (pestaña Reporte logístico).

> Premisa: en Dropi la transportadora se asigna **automáticamente por orden de prioridad** según cobertura. La #1 barre con todo lo que cubre. Se sobreescribe con **excepciones manuales por ciudad**.

---

## Las dos palancas (no confundir)
| Palanca | Alcance | Usar para |
|---------|---------|-----------|
| **Excepción por ciudad** | Quirúrgico | Pilotos A/B y casos puntuales. Aísla el efecto. |
| **Reordenar prioridad** | Global | Cambio estructural, SOLO con evidencia ya recogida |

Regla: una transportadora puede ser buena en una zona y mala en otra. **Nunca reordenar la prioridad global para arreglar una sola ciudad** — daña las zonas donde la #1 sí rinde y contamina experimentos.

## Secuencia de optimización (endgame)
```
1. Pilotos por ciudad (excepciones) → aprender qué transportadora gana en cada zona
2. Construir la "matriz de ruteo óptima" (zona → mejor transportadora con su % entrega)
3. Implementar: prioridad base = la que gana en MÁS zonas + excepciones donde gana otra
```
El orden de prioridad se define AL FINAL, con datos.

---

## Diseño de un piloto por ciudad
1. **Elegir zona**: mayor `devoluciones × volumen` (mayor pérdida absoluta). Mapa en `/cod-ops:reportes-logistica`.
2. **Baseline**: ya en el histórico (transportadora actual + % entrega). Piloto **secuencial**, sin dividir tráfico.
3. **Candidata**: si no hay data propia, benchmark de mercado (Coordinadora fuerte en capitales; 99minutos urbano; Servientrega cobertura rural; Interrapidísimo municipios). **Si hay evidencia interna del cruce depto×transportadora, usarla — gana sobre el benchmark.**
4. **Ejecutar**: excepción `ciudad → candidata`, resto igual. Constantes: producto, oferta, guion de confirmación.
5. **Duración**: ~50 órdenes despachadas con desenlace (señal preliminar a ~30).

## Captura SIN API
Dropi no tiene API abierta → pedir al usuario screenshot/copy semanal **filtrado por ciudad + transportadora**: despachadas, entregadas, devueltas, en novedad, flete promedio, tiempo (días). Procesar con `/cod-ops:reportes-logistica` (deduplicar recreaciones).

## Cuantificar el premio
```
Margen neto/despachada = tasa_entrega × MC_entregada − (1−tasa_entrega) × flete_ida_vuelta
Δ$/mes = (margen_nuevo − margen_actual) × despachadas_mes_zona
```
Comunicar SIEMPRE el premio en $/mes para priorizar.

## Criterio de decisión
- ✅ candidata > baseline + margen claro y flete similar → excepción permanente.
- ⚠️ empate técnico → probar la siguiente candidata.
- ❌ peor que baseline → mantener actual, probar otra zona.

## Seguimiento de un cambio ya implementado
Si `ruteo.fecha_implementacion` está fijada: en cada actualización del master, tomar las órdenes **creadas desde esa fecha**, calcular su % de entrega por zona/transportadora y compararlo con el baseline de `plan_zonas`. Concluir solo con **cohorte madura (<5% en tránsito)**. Registrar en `ruteo.semanas`. Veredicto: zona ≥ `gate_escalado` sostenido → permanente; por debajo → revertir/probar otra. Recordar al leer `n=` en el plan: es **tamaño de muestra**, no porcentaje.
