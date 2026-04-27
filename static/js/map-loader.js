(function () {
  const mapSection = document.getElementById("map-section");

  if (!mapSection) return;

  let hasStarted = false;

  function loadStylesheet(href, marker) {
    if (document.querySelector(`link[data-loader="${marker}"]`)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.dataset.loader = marker;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }

  function loadScript(src, marker) {
    if (document.querySelector(`script[data-loader="${marker}"]`)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.defer = true;
      script.dataset.loader = marker;
      script.onload = resolve;
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  async function loadMap() {
    if (hasStarted) return;
    hasStarted = true;

    try {
      await loadStylesheet(
        "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
        "leaflet-css"
      );
      await loadScript(
        "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
        "leaflet-js"
      );

      if (window.mapScriptUrl) {
        await loadScript(window.mapScriptUrl, "local-map");
      }
    } catch (error) {
      console.error("Leaflet n'a pas pu etre charge.", error);
    }
  }

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          observer.disconnect();
          loadMap();
        }
      },
      {
        rootMargin: "300px 0px",
      }
    );

    observer.observe(mapSection);
  } else {
    window.addEventListener("load", loadMap, { once: true });
  }
})();
