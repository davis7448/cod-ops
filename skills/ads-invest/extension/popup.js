// popup.js — muestra el contador y permite exportar el swipe_file.json o limpiar.
const KEY = "adlib_swipe";

function render() {
  chrome.storage.local.get([KEY], (res) => {
    const store = res[KEY] || {};
    document.getElementById("count").textContent = Object.keys(store).length;
  });
}

document.getElementById("export").addEventListener("click", () => {
  chrome.storage.local.get([KEY], (res) => {
    const store = res[KEY] || {};
    const ads = Object.values(store);
    if (!ads.length) {
      alert("Aún no hay anuncios capturados. Navega la Ad Library y desplázate.");
      return;
    }
    // Estructura compatible con scripts/download_swipe_media.py (espera { "ads": [...] }).
    const payload = { exported_at: new Date().toISOString(), count: ads.length, ads };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    chrome.downloads.download(
      { url, filename: "ad-library/swipe_file.json", saveAs: true },
      () => setTimeout(() => URL.revokeObjectURL(url), 5000)
    );
  });
});

document.getElementById("clear").addEventListener("click", () => {
  if (confirm("¿Borrar todos los anuncios capturados?")) {
    chrome.storage.local.set({ [KEY]: {} }, render);
  }
});

render();
