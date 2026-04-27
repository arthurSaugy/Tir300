const map = L.map("map", {
  scrollWheelZoom: false,
  zoomControl: false,
  dragging: window.innerWidth >= 900,
  tap: window.innerWidth >= 900,
  touchZoom: window.innerWidth >= 900,
  doubleClickZoom: window.innerWidth >= 900,
  boxZoom: window.innerWidth >= 900,
}).setView([lat, lng], 13);

// Ajout de la couche des tuiles OpenStreetMap
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Supprime complètement l’attribution
map.attributionControl.setPrefix(false);

// Contrôle zoom repositionné en bas à gauche
L.control
  .zoom({
    position: "topleft",
  })
  .addTo(map);

// Style CSS dynamique pour les boutons zoom
const style = document.createElement("style");
style.innerHTML = `
  .leaflet-control-zoom {
    bottom: -20px !important;
    left: 20px !important;
    top: auto !important;
  }

  .leaflet-control-zoom-in,
  .leaflet-control-zoom-out {
    width: 50px !important;
    height: 50px !important;
    font-size: 36px !important;
    line-height: 50px !important;
  }

  .leaflet-control-zoom a {
    background-color: #fff;
    color: #000;
    border: 2px solid #ccc;
    border-radius: 10px;
    text-align: center;
  }
`;
document.head.appendChild(style);

// Icône personnalisée
const customIcon = L.icon({
  iconUrl: "/static/assets/svg/pin.svg",
  iconSize: [100, 100],
  iconAnchor: [50, 100],
});

// Lien vers Google Maps
const addressText = "Route de Lucens 178A, 1527 Villeneuve";
const addressIcon = L.divIcon({
  className: "custom-label",
  html: `<a class="clickable-label" href="https://www.google.com/maps/place/Tir300+Villeneuve+FR/@46.7362767,6.8602262,635m/data=!3m1!1e3!4m15!1m8!3m7!1s0x478e787d63af76db:0xfb7ac6ca1a47d998!2sRte+de+Lucens+178A,+1527+Villeneuve!3b1!8m2!3d46.7362731!4d6.8628011!16s%2Fg%2F11kj3h1lb4!3m5!1s0x478e79f56761be63:0x2035cac8fe614b9e!8m2!3d46.7362731!4d6.8628011!16s%2Fg%2F11yfz9p8tv?entry=ttu&g_ep=EgoyMDI1MDcwOS4wIKXMDSoASAFQAw%3D%3D" target="_blank">${addressText}</a>`,
  iconSize: [0, 0],
});

// Ajout du pin + label
L.marker([lat, lng], { icon: customIcon }).addTo(map);
const labelMarker = L.marker([lat, lng], {
  icon: addressIcon,
  interactive: true,
}).addTo(map);

/* =========== Map en Mobile ================ */
function moveMapToPage2() {
  const mapSection = document.getElementById("map-section");
  const mapPlaceholder = document.querySelector(".map-mobile-placeholder");

  if (window.innerWidth < 900) {
    if (mapSection && mapPlaceholder && !mapPlaceholder.contains(mapSection)) {
      mapPlaceholder.appendChild(mapSection);
    }
  } else {
    // Si tu veux qu'elle retourne dans le body (ou ailleurs) en desktop :
    const main = document.querySelector("main");
    const lastSection = document.querySelector("main > section:last-child");

    if (mapSection && main && lastSection !== mapSection) {
      main.appendChild(mapSection);
    }
  }
}

window.addEventListener("load", moveMapToPage2);
window.addEventListener("resize", moveMapToPage2);
