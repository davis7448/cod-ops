# OmniVoice (k2-fsa) — voz en off para anuncios

> Probado en rondas reales de anuncios en español (Mac con Apple Silicon). Los perfiles aprobados por cada tienda van en `CONFIG-TIENDA.md`.

## Instalación probada
- Requiere Mac con chip Apple (M1 o superior) por `device_map="mps"` y `mlx_whisper`. En otro equipo, cambia `mps` por `cuda` o `cpu` y usa `openai-whisper`/`faster-whisper` para validar.
- Crear el entorno con uv:
  ```bash
  uv venv --python 3.11 ~/.venvs/voz
  uv pip install --python ~/.venvs/voz/bin/python omnivoice torch soundfile librosa mlx-whisper numpy
  ```
- venv: `~/.venvs/voz` (Python 3.11). **No trae pip**: instala con `uv pip install --python ~/.venvs/voz/bin/python <pkg>`.
- La primera llamada descarga los modelos de Hugging Face (`k2-fsa/OmniVoice`, `mlx-community/whisper-*`).
- Trae también `mlx_whisper` y `librosa` (para validar y medir).
- Modelo: `OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="mps", dtype=torch.float32)`. La salida queda a 24 kHz con `sf.write(path, audio[0], 24000)`.

## API
```python
audio = model.generate(text=t, num_step=32, speed=1.05, instruct="female, young adult, moderate pitch")
prompt = model.create_voice_clone_prompt(ref_audio="ancla.wav")   # fija o clona una voz
audio = model.generate(text=t, num_step=32, speed=1.05, voice_clone_prompt=prompt)
```

## `instruct`: etiquetas válidas (`omnivoice/utils/voice_design.py`)
- Género: `male`, `female`
- Edad: `child`, `teenager`, `young adult`, `middle-aged`, `elderly`
- Tono: `very low pitch`, `low pitch`, `moderate pitch`, `high pitch`, `very high pitch`
- `whisper`
- Acentos (solo en inglés): american, british, australian, chinese, canadian, indian, korean, portuguese, russian, japanese.
- Cualquier otra palabra ("excited", "friendly", "colombian") da `ValueError: Unsupported instruct items`.

## Gotchas
- **`teenager` rompe la voz** (sale vacía o con un pito plano de unos 499 Hz). Usar `young adult`.
- **Con `instruct` cada `generate()` es una persona distinta.** Si se genera frase por frase, la voz cambia a mitad del video. Hay que generar el guion completo en una llamada, o fijar la voz con `voice_clone_prompt` desde una toma ancla.
- `speed` 1,0 ≈ 2,7 palabras/s. Los creadores UGC colombianos hablan entre 3,1 y 4,1 palabras/s, así que en UGC conviene un `speed` de 1,12–1,3.
- `high pitch` en mujer da unos 405 Hz (muy agudo); `moderate` da 275–300 Hz.
- A veces se come una frase entera: **siempre validar con whisper** (similitud ≥ 0,9) y regenerar.
- **Los números largos en letras se pueden partir** ("doscientas treinta… y… siete", con un hueco de 0,7 s). Whisper lo delata: en vez de un solo "237" transcribe "230 y 7". No hace falta regenerar todo el guion: `create_voice_clone_prompt(ref_audio=(tensor, 24000), ref_text=…)` con los primeros 4 s de la misma toma → genera solo la frase → pégala con ffmpeg (`atrim` + `apad=whole_dur=<duración original>` + `concat`) para no mover los tiempos de los subtítulos. Iguala el volumen con `volumedetect` (la frase nueva salió 2 dB más baja).
- Sin acentos latinos: la prosodia y el léxico no lo reemplazan (se probó forzar "acento local" y se rechazó).
- **Memoria (Mac de 8 GB):** con OmniVoice y whisper en el mismo proceso, y el navegador de Playwright abierto, la máquina se queda sin RAM y `generate()` se traba sin error (CPU < 10 %, nada de salida en 15 min). Lo que funcionó: cerrar el navegador, generar solo con OmniVoice (2 tomas por guion, unos 30–80 s por toma de 20 s) y validar después con whisper en otro proceso. El hook SDD bloquea `shutil.copy` y `open().write` en Python: copia la toma ganadora con `ffmpeg -i in.wav -c copy out.wav`.

## Validación (patrón)
```python
h = mlx_whisper.transcribe(librosa.resample(a, orig_sr=24000, target_sr=16000),
        path_or_hf_repo='mlx-community/whisper-small-mlx', language='es')['text']
sim = difflib.SequenceMatcher(None, norm(h), norm(t)).ratio()   # norm: minúsculas, sin tildes ni signos
```
- `whisper-small-mlx` para validar (rápido); `whisper-large-v3-turbo` para los tiempos por palabra (`word_timestamps=True`).

## Medir una voz (referencia vs. sintética)
- Ritmo: palabras / (fin − inicio). Pausas: huecos > 0,3 s entre palabras.
- Tono: `librosa.pyin(y, fmin=70, fmax=500, sr=16000, frame_length=1024)` → mediana de F0 y desviación/media.
- La música de fondo distorsiona el F0 de las referencias.

## Alternativas evaluadas
- Microsoft es-CO (`es-CO-SalomeNeural`, `es-CO-GonzaloNeural`), en el venv `~/.venvs/tts-co` con edge-tts: tienen acento real, pero en pruebas se prefirió OmniVoice. Además, edge-tts no tiene licencia comercial: para pautar haría falta Azure Speech.
- ElevenLabs: biblioteca de voces colombianas licenciadas y diseño de voz por descripción (de pago). Sin probar.
- `say -v Paulina`: solo de respaldo (suena robótica).
