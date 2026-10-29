#!/usr/bin/env python3
"""
download_swipe_media.py — Descarga los archivos de creativos (video/imagen) listados
en el swipe_file.json que exporta la extensión "ad-library-toolkit", y genera un
INDEX-CREATIVOS.md con la ficha de cada uno.

Por qué existe: la Meta Ad Library API NO devuelve el archivo de media, solo el link
al anuncio. El swipe_file.json es la única fuente con URLs de media descargables.
Esas URLs (CDN de Facebook) caducan en horas: ejecuta el mismo día de exportar.

Uso:
    python download_swipe_media.py --input swipe_file.json --out ./media [opciones]

Opciones:
    --input PATH     Ruta al swipe_file.json (obligatorio).
    --out DIR        Carpeta destino de la media (obligatorio). Se crea si no existe.
    --limit N        Máximo de creativos a descargar (default: todos).
    --filter TEXT    Solo descarga anuncios cuyo copy/marca contenga TEXT (case-insensitive).
    --no-index       No genera INDEX-CREATIVOS.md.

Solo usa la librería estándar de Python (3.8+). No requiere pip install.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

UA = "Mozilla/5.0 (compatible; ads-invest-downloader/1.0)"

# Claves donde las distintas versiones del export suelen guardar cada dato.
VIDEO_KEYS = ("video_url", "videoUrl", "video_sd_url", "video_hd_url", "video")
IMAGE_KEYS = ("image_url", "imageUrl", "original_image_url", "thumbnail_url", "image")
BODY_KEYS = ("ad_creative_body", "body", "ad_body", "text", "caption", "title",
             "ad_creative_link_title", "link_title")
PAGE_KEYS = ("page_name", "pageName", "advertiser", "page")
LANDING_KEYS = ("link_url", "landing_url", "ad_creative_link_url", "url", "destination")
SNAPSHOT_KEYS = ("ad_snapshot_url", "snapshot_url", "snapshotUrl", "ad_library_url")
DATE_KEYS = ("ad_delivery_start_time", "ad_creation_time", "start_date", "created")


def first(d, keys):
    """Devuelve el primer valor no vacío entre las claves dadas."""
    for k in keys:
        v = d.get(k)
        if v:
            return v
    return ""


def iter_ads(data):
    """Soporta swipe_file.json como lista, o como dict con 'ads'/'results'/'items'."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("ads", "results", "items", "swipe", "data"):
            if isinstance(data.get(k), list):
                return data[k]
        # dict de un solo nivel cuyos valores son anuncios
        vals = [v for v in data.values() if isinstance(v, dict)]
        if vals:
            return vals
    raise ValueError("No reconozco la estructura del JSON (esperaba lista o dict con 'ads').")


def slugify(text, maxlen=40):
    text = re.sub(r"https?://\S+", "", str(text))
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:maxlen].strip("_") or "ad"


def to_date(val):
    """Convierte epoch (s) o string a fecha YYYY-MM-DD si se puede."""
    if not val:
        return ""
    try:
        n = int(val)
        if n > 10_000_000:  # parece epoch en segundos
            return datetime.fromtimestamp(n, tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass
    return str(val)[:10]


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def main():
    ap = argparse.ArgumentParser(description="Descarga media de swipe_file.json")
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--filter", default="")
    ap.add_argument("--no-index", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"ERROR: no existe el archivo {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    ads = iter_ads(data)
    needle = args.filter.lower().strip()
    os.makedirs(args.out, exist_ok=True)

    index_rows, n = [], 0
    for ad in ads:
        if not isinstance(ad, dict):
            continue
        page = first(ad, PAGE_KEYS) or "advertiser"
        body = first(ad, BODY_KEYS)
        if needle and needle not in (str(page) + " " + str(body)).lower():
            continue

        video = first(ad, VIDEO_KEYS)
        image = first(ad, IMAGE_KEYS)
        url = video or image
        if not url:
            continue

        n += 1
        ext = ".mp4" if video else os.path.splitext(str(image).split("?")[0])[1] or ".jpg"
        name = f"{n:02d}_{slugify(page)}_{slugify(body, 24)}{ext}"
        dest = os.path.join(args.out, name)

        try:
            download(url, dest)
            status = "OK"
            print(f"[{n:02d}] {name}")
        except Exception as e:  # noqa: BLE001
            status = f"FALLÓ ({e})"
            print(f"[{n:02d}] {name} -> {status}", file=sys.stderr)

        index_rows.append({
            "file": name,
            "page": page,
            "body": (str(body)[:200] or "—"),
            "landing": first(ad, LANDING_KEYS) or "—",
            "snapshot": first(ad, SNAPSHOT_KEYS) or "—",
            "date": to_date(first(ad, DATE_KEYS)),
            "status": status,
        })

        if args.limit and n >= args.limit:
            break

    print(f"\n{n} creativos procesados en {args.out}")

    if not args.no_index and index_rows:
        idx = os.path.join(args.out, "INDEX-CREATIVOS.md")
        with open(idx, "w", encoding="utf-8") as f:
            f.write("# Índice de creativos (swipe file)\n\n")
            f.write(f"Total: {len(index_rows)} anuncios. Generado por download_swipe_media.py.\n\n")
            for r in index_rows:
                f.write(f"## {r['file']}\n")
                f.write(f"- **Anunciante:** {r['page']}\n")
                f.write(f"- **Copy:** {r['body']}\n")
                f.write(f"- **Landing:** {r['landing']}\n")
                f.write(f"- **Ad Library:** {r['snapshot']}\n")
                f.write(f"- **Fecha inicio:** {r['date']}\n")
                f.write(f"- **Descarga:** {r['status']}\n\n")
        print(f"Índice escrito en {idx}")


if __name__ == "__main__":
    main()
