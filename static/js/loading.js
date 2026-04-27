document.addEventListener("DOMContentLoaded", () => {
  const circle = document.getElementById("circle-transition");
  if (!circle || typeof gsap === "undefined") {
    document.body.classList.remove("loading");
    document.body.classList.add("loaded");
    return;
  }
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;

  circle.style.transformOrigin = "center center";
  circle.style.display = "none";

  // Suivi position souris
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    document.addEventListener(
      "mousemove",
      (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
      },
      { passive: true }
    );
  }

  // Animation d'entrée au chargement de la page
  gsap.fromTo(
    circle,
    { scale: 30, transformOrigin: "center center" },
    {
      scale: 0,
      duration: 0.7,
      ease: "power2.out",
      onStart: () => {
        circle.style.display = "block";
        circle.style.left = "50%";
        circle.style.top = "50%";
        // Translation centrée initiale pour le scale autour du centre
        circle.style.transform = "translate(-50%, -50%) scale(30)";
      },
      onComplete: () => {
        circle.style.display = "none";
        document.body.classList.remove("loading");
        document.body.classList.add("loaded");
      },
    }
  );

  // Animation de sortie au clic sur un lien
  document.querySelectorAll("a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    const target = link.getAttribute("target");
    if (
      !href ||
      href.startsWith("#") ||
      href.endsWith(".pdf") ||
      href.startsWith("mailto") ||
      href.startsWith("tel") ||
      target === "_blank" ||
      link.hasAttribute("download")
    )
      return;

    link.addEventListener("click", (e) => {
      if (
        e.defaultPrevented ||
        e.button !== 0 ||
        e.metaKey ||
        e.ctrlKey ||
        e.shiftKey ||
        e.altKey
      ) {
        return;
      }

      const url = new URL(link.href, window.location.href);
      if (url.origin !== window.location.origin) {
        return;
      }

      e.preventDefault();

      // Positionner cercle au curseur, sans translation centrée
      circle.style.left = `${mouseX}px`;
      circle.style.top = `${mouseY}px`;
      circle.style.transformOrigin = "center center";
      circle.style.transform = "scale(0)";
      circle.style.display = "block";

      gsap.to(circle, {
        scale: 30,
        duration: 0.3,
        ease: "power2.in",
        onComplete: () => {
          window.location = url.href;
        },
      });
    });
  });
});

window.addEventListener("pageshow", (event) => {
  if (event.persisted) {
    // La page est restaurée depuis le cache (ex: retour en arrière)
    document.body.classList.remove("loading");
    document.body.classList.add("loaded");
  }
});
