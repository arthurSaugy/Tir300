document.addEventListener("DOMContentLoaded", () => {
  const burger = document.getElementById("burgerMenu");
  const overlay = document.getElementById("menuOverlay");

  if (!burger || !overlay) return;

  function closeMenu() {
    overlay.classList.remove("active", "closing");
    burger.classList.remove("active");
    document.body.classList.remove("no-scroll");
  }

  burger.addEventListener("click", () => {
    const isOpen = overlay.classList.contains("active");

    if (isOpen) {
      closeMenu();
    } else {
      overlay.classList.add("active");
      burger.classList.add("active");
      document.body.classList.add("no-scroll");
    }
  });

  overlay.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });
});
