const cursor = document.getElementById("customCursor");
const toggleBtn = document.getElementById("cursorToggle");
const toggleIcon = document.getElementById("cursorToggleIcon");

if (!cursor || !toggleBtn || !toggleIcon) {
  // Nothing to initialize on pages without the cursor UI.
} else if (window.matchMedia("(hover: none), (pointer: coarse)").matches) {
  cursor.style.display = "none";
  toggleBtn.style.display = "none";
  document.body.classList.remove("custom-cursor-active");
} else {
  let customCursorEnabled = true;

  cursor.style.pointerEvents = "none";
  document.body.classList.add("custom-cursor-active");

  document.addEventListener("mousemove", (e) => {
    cursor.style.left = `${e.clientX}px`;
    cursor.style.top = `${e.clientY}px`;
  });

  document.addEventListener("mouseover", (e) => {
    if (!customCursorEnabled) return;

    const clickable = e.target.closest("a, button, .clickable, [role='button']");
    cursor.classList.toggle("pointer", !!clickable);

    if (e.target.closest(".fond-vert")) {
      cursor.classList.add("force-white");
    } else {
      cursor.classList.remove("force-white");
    }
  });

  document.addEventListener("click", () => {
    if (!customCursorEnabled) return;

    const rotation = cursor.classList.contains("pointer") ? "45deg" : "0deg";
    cursor.style.setProperty("--rotation", rotation);
    cursor.classList.add("click");
    setTimeout(() => cursor.classList.remove("click"), 300);
  });

  toggleBtn.addEventListener("click", () => {
    customCursorEnabled = !customCursorEnabled;

    if (customCursorEnabled) {
      cursor.style.display = "block";
      document.body.classList.add("custom-cursor-active");
      toggleIcon.src = "/static/assets/img/default_cursor.webp";
      toggleIcon.classList.remove("curseur_perso_img");
    } else {
      cursor.style.display = "none";
      document.body.classList.remove("custom-cursor-active");
      toggleIcon.src = "/static/assets/svg/curseur.svg";
      toggleIcon.classList.add("curseur_perso_img");
    }
  });
}
