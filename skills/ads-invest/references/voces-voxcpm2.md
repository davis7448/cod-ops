# Voces por avatar con VoxCPM2 (motor recomendado)

Probado el 2026-10-23 contra OmniVoice con un mismo guion UGC. El usuario eligió VoxCPM2: suena más natural, toma mejor el acento y, dirigido frase por frase, alcanza la expresividad de un creador real. OmniVoice ([voces-omnivoice.md](voces-omnivoice.md)) queda como respaldo.

**Regla:** cada guion tiene un **avatar** (quién habla) y el avatar tiene **su propia voz**, con acento y personalidad acordes. No se reutiliza la misma voz para todos los anuncios.

## Por qué suena "a comercial" (y cómo se mide)
Medido sobre 15 anuncios UGC reales en español contra tomas de TTS:

| Métrica | Creador real | TTS "de comercial" |
|---|---|---|
| Pausas > 0,25 s por minuto | 0–4 (habla de corrido, encadena con "y", "y es que", "pero") | 8–14 (una pausa limpia en cada punto) |
| Rango de tono (p95 − p5) | 17–28 semitonos | 7–14 |
| Texto | Narra lo que muestra: "miren", "por aquí", "a mí me pasaba que…", "o sea", "literal" | Frases de ficha técnica |

Se mide con whisper (`word_timestamps`) para las pausas y `librosa.pyin` para el tono. **Meta de cada voz final: ≤ 6 pausas/min de más de 0,25 s (fuera de las dramáticas) y ≥ 17 st de rango.**

## Instalación (Apple Silicon)
```bash
uv venv -p 3.11 ~/.venvs/voz-mlx
uv pip install -p ~/.venvs/voz-mlx/bin/python mlx-audio soundfile
```
Modelo `mlx-community/VoxCPM2-4bit` (2,3 GB, Apache-2.0, 48 kHz, 30 idiomas con español). La versión 8-bit pesa 3,2 GB. Entorno **aparte** del de OmniVoice: `mlx-audio` exige un `transformers` que lo rompe.
- Con 8 GB de RAM: Chrome **cerrado** (`osascript -e 'tell application "Google Chrome" to quit'` y verificar con `pgrep -x "Google Chrome"`; si sigue vivo, el proceso de PyTorch/MLX se queda colgado esperando la GPU, con el swap lleno).
- Revisa el disco antes de descargar (`df -h ~`): las cachés de brew/npm/uv se pueden limpiar con sus propios comandos.

## Paso 1 — Ficha del avatar (en `GUIONES.md`, antes de cada guion)
`Avatar: mujer de 30–35, Medellín, oficinista, chismosa y cálida, se graba con el celular en el sofá` · región/acento · personalidad · situación de grabación. Sale del ángulo y la referencia (mamá → 45–55; hija regalando → 25–35; tutorial → clara y práctica; reacción → baja y relajada; papá → hombre 35–45).

## Paso 2 — Guion en estilo UGC (no de folleto)
- De corrido: comas en vez de puntos; une con "y", "y es que", "entonces", "o sea".
- Narra lo que se ve: "miren", "uno se lo pone así", "aquí en la frente".
- Léxico de la región del avatar con mesura (Colombia: "un ratico", "quedo nueva", "súper", diminutivos). Interjecciones cortas ("¡Ay no!") como frase propia.
- Precio contado como experiencia ("me costó… y lo pagué cuando me llegó"), con números en letras.
- Lo de siempre: el producto y su mecanismo en los primeros 5 s, solo claims ✅.

## Paso 3 — Voz base del avatar (diseño por descripción)
Una toma del guion completo con `instruct` en **español** (en inglés salió más plana y con errores), describiendo persona + acento + situación + "nada de locutora ni de comercial":
```python
from mlx_audio.tts.utils import load
import numpy as np, soundfile as sf
m = load("mlx-community/VoxCPM2-4bit")
D = "Una mujer colombiana común de treinta años de Medellín grabándose con el celular en su casa, habla espontánea y de corrido, sin pausas largas, como una nota de voz de WhatsApp a una amiga, tono de chisme emocionado, sube y baja la voz, nada de locutora ni de comercial"
a = np.concatenate([np.array(r.audio) for r in m.generate(text=GUION, instruct=D, inference_timesteps=12, cfg_value=2.0)])
sf.write("base.wav", a, 48000)
```
**Control de tono (obligatorio):** el modelo tiende a voces graves; con "mujer" a secas salieron voces de 115–150 Hz que el usuario oyó "como de hombre". Pon el género en la voz misma ("voz claramente femenina de tono medio-alto" o "voz masculina de tono medio"), genera **4 candidatas** y mide la mediana de F0 con `librosa.pyin`: mujer 185–240 Hz (ideal ~210), hombre 100–140 Hz. Quédate con la que caiga en rango. En el paso 4, descarta las tomas de frase que se salgan del rango (mujer < 175 Hz) y repite hasta tener 2 válidas.
**El tono no basta:** una voz a 215 Hz sonó "de hombre" (el timbre manda). Filtro definitivo: clasificador de género `prithivMLmods/Common-Voice-Gender-Detection` (wav2vec2, Apache-2.0, `AutoModelForAudioClassification`, etiquetas 0=female/1=male) en el entorno de OmniVoice (tiene torch). Calibrado contra el oído del usuario: las voces que oyó "de hombre" dieron P(mujer)=0,00 y las aceptadas 0,77–1,00. Regla: candidatas y tomas de frase con **P(género del avatar) ≥ 0,9**. De 16 candidatas "femeninas" por descripción, 9 salieron masculinas: genera 8 (4 descripciones × 2) y filtra.
Que el usuario **escuche y elija la voz base antes** de actuar el guion completo (muestras de ~10 s): así no se gastan 15 min actuando una voz que no le gusta. La elegida se recorta (8–10 s limpios) a `voz_<avatar>.wav`: **esa es la voz del personaje** y se guarda junto al producto para reusarla en todas sus piezas. VoxCPM2 no tiene `speed`; el ritmo sale de la descripción.

## Paso 4 — Actuación dirigida frase por frase (lo que da la expresividad)
Partir el guion en frases cortas, cada una con su emoción, **clonando la voz base** (`ref_audio`) para que el hablante no cambie:
```python
SEG = [("¡Amigas, miren lo que me compré!", "sorprendida y muy emocionada, voz aguda, sonriendo"),
       ("como si alguien le estuviera haciendo masaje con las manos.", "suave y placentera, voz más baja y lenta"),
       ("¡Ay no!", "exclamación de alivio, con un suspiro"),
       ("Me costó … y lo pagué cuando me llegó.", "en tono de chisme, cómplice"), ...]
for i, (t, e) in enumerate(SEG):
    for k in range(2):  # 2 tomas por frase
        a = np.concatenate([np.array(r.audio) for r in m.generate(text=t, ref_audio="voz_avatar.wav",
             instruct="<persona y región>, hablando espontánea por el celular, " + e, inference_timesteps=12, cfg_value=2.0)])
        sf.write(f"s{i:02d}_{k}.wav", a, 48000)
```
Emociones que funcionaron: sorprendida · explicando con entusiasmo · mostrando con curiosidad · suave y placentera · tierna · alivio con suspiro · quejándose exagerada · aliviada sonriendo · rápida y práctica · chisme cómplice · despedida cálida.

## Paso 5 — Elegir tomas y ensamblar
Por frase, en este orden: (1) whisper dice **exactamente** la frase (similitud ≥ 0,97; el modelo a veces inventa palabras: "¡Piano, amigas!", "deco"), (2) menos silencio muerto interno, (3) más rango de tono. Luego:
- Recortar los bordes y comprimir los silencios internos a ≤ 0,18 s (`librosa.effects.split(top_db=38)`).
- Igualar el volumen por frase (RMS) y fundidos de 12 ms.
- **Pausas a mano** entre frases: 0,05–0,1 s donde se habla de corrido, 0,2–0,3 s normales, 0,4–0,5 s antes del remate ("…y quedo nueva") o del precio.
- Medir el resultado (meta de arriba) y validar con whisper el guion completo.

## Paso 6 — Sonido de celular (opcional, recomendado para UGC)
```bash
ffmpeg -i voz.wav -af "highpass=f=140,lowpass=f=9500,aecho=0.85:0.6:18|31:0.12|0.07,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-16" -ar 48000 voz_celular.wav
```
Si el total queda largo, `atempo=1.08–1.12` (no cambia el tono). Con 1,2 el usuario dijo que "dejó de sonar natural": no pasar de 1,12; si sigue largo, recorta pausas o acorta el guion. Entrega al usuario las variantes limpia / celular / rápida y deja que elija.

## Tiempos de referencia (M1/M2, 8 GB, 4-bit)
Guion de 25 s en una llamada: 50–90 s. Actuación de 11 frases × 2 tomas: ~10–12 min (correr en segundo plano y vigilar con Monitor).

## Límites
- Describir un acento con palabras tiene techo; la actuación por frase lo compensa. El salto siguiente es una referencia real (15–30 s) de una persona **que autorice por escrito** su voz. Nunca se clona a un creador ni a un competidor.
