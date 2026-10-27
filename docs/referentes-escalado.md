# Referentes de escalado — cuentas COD Colombia (octubre 2026)

Datos del 1 al 27 de octubre de 2026, tomados por la API de Meta en cuentas reales de e-commerce contraentrega en Colombia. Son la base de las reglas de `/cod-ops:one-cbo` y `/cod-ops:seguimiento`. Los nombres de cuentas, productos y personas están **anonimizados**.

| Referente | Gasto del mes | Compras | CPA | Modelo |
|---|---|---|---|---|
| **A** (suplemento, un solo producto) | ~$157 M | ~5.300 | ~$30k (atribución 7 d clic + 1 d vista + video con interacción) | Ráfaga + escalado intradía |
| **B** (suplementos, varios productos) | ~$9,8 M | ~415 | ~$24k | Madre permanente + laboratorio |
| **C** (salud y belleza, varios productos) | ~$5,1 M | ~237 | ~$21k | Madre permanente + laboratorio, presupuestos bajos |

## 1. Estructura (los tres)
- Ventas, CBO, máximo volumen. Conjuntos abiertos: país, 21–65, Advantage+ Audience.
- **A:** cada campaña lleva 2 conjuntos, "OPEN 1 FLEX" (formato flexible) y "OPEN 2 CBO" (anuncios normales), con 1–3 anuncios cada uno.
- **B y C:** "CONJUNTO 1 FLEXIBLE VIDEO", "CONJUNTO 2 FLEXIBLE VIDEO", "CONJUNTO 3 FLEXIBLE imágenes" y "LOOKALIKE 3 %".
- **B y C:** la campaña madre lleva viva desde febrero o abril, con CPA estable de $23–24k (B). Los creativos ganadores del laboratorio entran con la etiqueta "graduado del test".

## 2. Creativo (A)
- Todos los anuncios llevan el mismo copy: testimonio largo en primera persona (dolor → lo que ya intentó → beneficios → envío gratis + contraentrega + tiempo limitado).
- Título de prueba social: "+20,000 UNIDADES VENDIDAS ⭐".
- **Solo cambia el video.** Un video se llevó el 76 % del gasto de su campaña ($13 M de $17 M).
- CTR entre 4 % y 9 %, CPM de $20–30k.

## 3. Escalado vertical (A): campaña ganadora, ventas por hora del 17 al 25 oct contra cada cambio de presupuesto
Meta de CPA aproximada: $26k.

| Día y hora | CPA del día en ese momento | Cambio de presupuesto |
|---|---|---|
| 18-oct 12 h | $15,9k (5 compras) | 100k → 238k |
| 18-oct 14 h | $12,8k (9) | 238k → 780k |
| 18-oct 18 h | $10,6k (22) | 780k → 1,28 M |
| 19-oct 08 h | $41,8k (6; mañana inflada) | 1,28 M → 680k |
| 19-oct 10 h | $18,3k (22) | 680k → 1,28 M |
| 20-oct 12 h | $19,6k (22) | 480k → 2,48 M |
| 20-oct 15 h | $21,7k (37) | 2,48 M → 3,48 M |
| 22-oct 05 h | $31,6k | 3,1 M → 800k |
| 23-oct 08 h | $21,2k (21) | 1,1 M → 1,8 M |
| 24-oct 08 h | $35,6k | 1,5 M → 1 M |
| 24-oct 15 h | $46,5k | 1 M → 600k |

Gasto real por día y CPA:

| Día (oct) | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|
| Gasto | 89k | 533k | 1,65 M | 2,03 M | 3,66 M | 1,06 M | 1,61 M | 1,05 M | 1,24 M |
| CPA | — | $17k | $27,6k | $27,7k | $31,3k | $26k | $24,8k | $33,9k | $22,6k |

**Lectura:**
- Suben de ×1,5 a ×5 cuando el CPA del día queda ≤ ~0,85 × meta.
- Bajan entre 30 % y 60 % cuando pasa de ~1,15 × meta.
- Nunca apagan la ganadora: la estacionan en un piso de 480–600k.
- El presupuesto funciona como techo: se gasta el 60–80 % de lo asignado.
- Punto de saturación: 1,2–1,6 M/día.

## 4. Escalado horizontal y corte (A)
- Del 7 al 11 de octubre lanzaron unas 30 campañas a $60k/día: mismo copy, distinto video o combinación, nombres `DD-MM-AAAA PRODUCTO (variante) N`.
- Del 14 al 16 de octubre apagaron cerca de 30 en bloque, con 6–8 días de vida y gastos entre $150k y $700k.
- Regla de corte, deducida de las cifras: apagan con CPA ≥ ~1,2 × meta, **incluso una campaña con $5,1 M gastados**. Sobrevive lo que tiene CPA ≤ ~meta.
- Sobrevivientes: 2–3 de unas 30 (≈ 7 %), con $17,1 M a CPA $26,4k y $9,5 M a CPA $26,6k.
- Desde el 14 de octubre no crearon más campañas.
- Tope de puja ("BIDCAP | 10 VIDEOS", tope de $26k por conjunto, presupuesto de $15 M como techo): CPA $22,5k, el mejor de la cuenta. Las versiones con cost cap dieron CPA de $69k a $104k.
