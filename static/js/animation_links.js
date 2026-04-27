document.querySelectorAll(".desktop-menu ul li a").forEach((link) => {
  const text = link.textContent.trim();
  const letters = text
    .split("")
    .map((char, i) => {
      return `
      <span class="letter-mask">
        <span class="letter" style="transition-delay: ${
          i * 25
        }ms">${char}</span>
      </span>
    `;
    })
    .join("");
  link.innerHTML = letters;
  link.setAttribute("data-text", text);
});

document.querySelectorAll(".desktop-menu ul li a").forEach((link) => {
  const clone = link.cloneNode(true);
  clone.classList.add("hover-clone");
  clone.style.display = "inline-block";

  clone.querySelectorAll(".letter").forEach((span, i) => {
    span.style.transform = "translateY(100%)";
    span.style.transitionDelay = `${i * 25}ms`;
  });

  link.style.position = "relative";
  link.appendChild(clone);

  link.addEventListener("mouseenter", () => {
    link.querySelectorAll(".letter").forEach((span, i) => {
      span.style.transform = "translateY(-100%)";
    });
    clone.querySelectorAll(".letter").forEach((span, i) => {
      span.style.transform = "translateY(0)";
    });
  });

  link.addEventListener("mouseleave", () => {
    link.querySelectorAll(".letter").forEach((span) => {
      span.style.transform = "translateY(0)";
    });
    clone.querySelectorAll(".letter").forEach((span) => {
      span.style.transform = "translateY(100%)";
    });
  });
});

const underline = document.querySelector(".nav-underline");
const links = document.querySelectorAll(".desktop-menu ul li a");
const activeLink = document.querySelector(".desktop-menu a.active");

/* ============= Trait sous liens =========== */
function moveUnderlineTo(el, asDot = false) {
  const rect = el.getBoundingClientRect();
  const containerRect = el.closest(".nav-links").getBoundingClientRect();
  const width = asDot ? 6 : rect.width / 1.3; // largeur du point ou du lien
  const left = rect.left - containerRect.left + (rect.width - width) / 2; // centré

  underline.style.width = `${width}px`;
  underline.style.left = `${left}px`;

  // Ajoute ou retire la classe "as-dot"
  if (asDot) {
    underline.classList.add("as-dot");
  } else {
    underline.classList.remove("as-dot");
  }
}

// Initial
window.addEventListener("load", () => {
  if (activeLink) moveUnderlineTo(activeLink, true);
});

// Hover
links.forEach((link) => {
  link.addEventListener("mouseenter", () => moveUnderlineTo(link));
  link.addEventListener("mouseleave", () => {
    if (activeLink) moveUnderlineTo(activeLink, true);
  });
});

/* ================= Burger button */

const burger = document.getElementById("burgerMenu");
const overlay = document.getElementById("menuOverlay");
const listItems = document.querySelectorAll(".menu-links li");

// Découpe chaque lettre dans chaque lien <a> en <span>
document.querySelectorAll(".menu-links a").forEach((link) => {
  const text = link.textContent.trim();
  link.textContent = "";
  [...text].forEach((letter, index) => {
    const span = document.createElement("span");
    span.textContent = letter;
    span.classList.add("letter-out");
    span.style.display = "inline-block";
    span.style.transition =
      "transform 0.6s cubic-bezier(.73,.04,.83,.67), opacity 0.7s ease-in";
    span.style.transitionDelay = `${(text.length - 1 - index) * 10}ms`;
    link.appendChild(span);
  });
});

// Gestion du clic sur le burger
burger.addEventListener("click", () => {
  if (overlay.classList.contains("active")) {
    // menu ouvert → animation de fermeture
    overlay.classList.add("closing");

    document.querySelectorAll(".menu-links a span").forEach((span) => {
      span.classList.add("letter-out");
    });
    document.querySelectorAll(".menu-links a").forEach((link) => {
      link.classList.add("hide-arrow"); // pour masquer la flèche lors de la fermeture
    });

    listItems.forEach((li) => li.classList.add("hide-line"));

    setTimeout(() => {
      overlay.classList.remove("active", "closing");
      burger.classList.remove("active");
      document.body.classList.remove("no-scroll");
    }, 250);
  } else {
    // menu fermé → ouverture normale
    overlay.classList.add("active");
    burger.classList.add("active");
    document.body.classList.add("no-scroll");

    document.querySelectorAll(".menu-links a span").forEach((span) => {
      span.classList.remove("letter-out");
    });
    document.querySelectorAll(".menu-links a").forEach((link) => {
      link.classList.remove("hide-arrow"); // pour faire réapparaître la flèche
    });
    listItems.forEach((li) => li.classList.remove("hide-line"));
  }
});

// Gestion du clic sur un lien dans le menu
document.querySelectorAll(".menu-links a").forEach((link) => {
  link.addEventListener("click", () => {
    overlay.classList.add("closing");

    document.querySelectorAll(".menu-links a span").forEach((span) => {
      span.classList.add("letter-out");
    });

    setTimeout(() => {
      overlay.classList.remove("active", "closing");
      burger.classList.remove("active");
      document.body.classList.remove("no-scroll");

      document.querySelectorAll(".menu-links a span").forEach((span) => {
        span.classList.remove("letter-out");
      });
    }, 500);
  });
});
