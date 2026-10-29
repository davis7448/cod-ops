// content.js — corre en el world ISOLATED (con acceso a chrome.storage).
// Recibe los anuncios que inject.js extrae de la página, los deduplica por
// ad_archive_id y los acumula en chrome.storage.local. El popup luego exporta todo.
(function () {
  "use strict";

  const KEY = "adlib_swipe";

  window.addEventListener("message", (ev) => {
    if (ev.source !== window) return;
    const msg = ev.data;
    if (!msg || msg.source !== "adlib-toolkit" || !Array.isArray(msg.ads)) return;

    chrome.storage.local.get([KEY], (res) => {
      const store = res[KEY] || {};
      let added = 0;
      for (const ad of msg.ads) {
        // dedupe: solo guardamos anuncios con algún archivo de media
        const hasMedia = ad.video_hd_url || ad.video_sd_url || ad.image_url;
        if (!hasMedia) continue;
        const id = ad.ad_archive_id || ad.ad_snapshot_url || JSON.stringify(ad).slice(0, 60);
        if (!store[id]) {
          store[id] = ad;
          added++;
        }
      }
      if (added > 0) {
        chrome.storage.local.set({ [KEY]: store });
      }
    });
  });
})();
