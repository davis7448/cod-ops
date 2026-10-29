// inject.js — corre en el MAIN world de la página de la Ad Library.
// Hookea fetch y XMLHttpRequest para leer las respuestas GraphQL que el propio
// navegador ya recibe al navegar la Ad Library, extrae los anuncios (con sus URLs
// de media) y los envía al content script vía window.postMessage.
//
// Solo lee datos PÚBLICOS que la página ya cargó. No automatiza navegación ni login.
(function () {
  "use strict";

  function emit(ads) {
    if (ads && ads.length) {
      window.postMessage({ source: "adlib-toolkit", ads: ads }, "*");
    }
  }

  // Recorre cualquier objeto JSON buscando nodos que parezcan un anuncio
  // (tienen `snapshot` y un id de archivo) y los normaliza a las claves que
  // espera scripts/download_swipe_media.py.
  function harvest(obj, out, seen) {
    if (!obj || typeof obj !== "object") return;
    if (seen.has(obj)) return;
    seen.add(obj);

    if (Array.isArray(obj)) {
      for (const it of obj) harvest(it, out, seen);
      return;
    }

    const snap = obj.snapshot || obj.snapshot_data;
    const id = obj.ad_archive_id || obj.adArchiveID || obj.ad_archive_ID;
    if (snap && (id || snap.page_name)) {
      out.push(normalize(obj, snap, id));
    }

    for (const k in obj) {
      const v = obj[k];
      if (v && typeof v === "object") harvest(v, out, seen);
    }
  }

  function pick(arr, keys) {
    if (!Array.isArray(arr) || !arr.length) return "";
    const first = arr[0] || {};
    for (const k of keys) if (first[k]) return first[k];
    return "";
  }

  function normalize(ad, snap, id) {
    const body =
      (snap.body && (snap.body.text || snap.body.markup || snap.body)) ||
      snap.caption ||
      "";
    return {
      ad_archive_id: id || "",
      page_id: ad.page_id || snap.page_id || "",
      page_name: snap.page_name || ad.page_name || "",
      body: typeof body === "string" ? body : "",
      link_title: snap.title || snap.link_description || snap.cta_text || "",
      link_url: snap.link_url || "",
      ad_snapshot_url: id
        ? "https://www.facebook.com/ads/library/?id=" + id
        : "",
      ad_delivery_start_time: ad.start_date || snap.start_date || "",
      video_hd_url: pick(snap.videos, ["video_hd_url"]),
      video_sd_url: pick(snap.videos, ["video_sd_url"]),
      image_url: pick(snap.images, ["original_image_url", "resized_image_url"]),
      original_image_url: pick(snap.images, ["original_image_url"]),
    };
  }

  function scan(text) {
    if (!text || text.indexOf("snapshot") === -1) return;
    try {
      const data = JSON.parse(text);
      const out = [];
      harvest(data, out, new WeakSet());
      emit(out);
    } catch (_) {
      // Respuestas FB a veces traen prefijo anti-JSON-hijacking (for (;;);)
      const cleaned = text.replace(/^for\s*\(;;\);/, "").trim();
      if (cleaned !== text) {
        try {
          const data = JSON.parse(cleaned);
          const out = [];
          harvest(data, out, new WeakSet());
          emit(out);
        } catch (_) {}
      }
    }
  }

  // --- hook fetch ---
  const origFetch = window.fetch;
  window.fetch = function (...args) {
    return origFetch.apply(this, args).then((res) => {
      try {
        res.clone().text().then(scan).catch(() => {});
      } catch (_) {}
      return res;
    });
  };

  // --- hook XHR ---
  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (...a) {
    return origOpen.apply(this, a);
  };
  XMLHttpRequest.prototype.send = function (...a) {
    this.addEventListener("load", function () {
      try {
        if (typeof this.responseText === "string") scan(this.responseText);
      } catch (_) {}
    });
    return origSend.apply(this, a);
  };

  console.log("[ad-library-toolkit] interceptor activo en la Ad Library.");
})();
