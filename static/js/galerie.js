document.addEventListener("DOMContentLoaded", () => {
  const main = document.querySelector("main");
  const isAdmin = main.classList.contains("admin-page");

  // Modale ajout (admin)
  const btnAjouter = document.getElementById("btn-ajouter");
  if (btnAjouter) {
    btnAjouter.addEventListener("click", () => {
      document.getElementById("modal-ajout").style.display = "flex";
    });

    document.getElementById("fermer-modal").addEventListener("click", () => {
      document.getElementById("modal-ajout").style.display = "none";
    });

    // Fermer modale ajout en cliquant en dehors
    const modalAjout = document.getElementById("modal-ajout");
    modalAjout.addEventListener("click", (e) => {
      if (e.target === modalAjout) {
        modalAjout.style.display = "none";
      }
    });
  }

  // Modale modification (admin)
  const editModal = document.getElementById("editModal");
  if (editModal) {
    const closeBtn = editModal.querySelector(".close-modal, .close");

    closeBtn.addEventListener("click", () => {
      editModal.classList.add("hidden");
      editModal.style.display = "none";
    });

    editModal.addEventListener("click", (e) => {
      if (e.target === editModal) {
        editModal.classList.add("hidden");
        editModal.style.display = "none";
      }
    });

    // Bouton supprimer dans modale
    deleteBtn.addEventListener("click", () => {
      const id = document.getElementById("photoId").value;

      // Création manuelle d’un formulaire invisible pour cette suppression
      const form = document.createElement("form");
      form.method = "POST";
      form.action = `/admin_galerie/delete/${id}`;

      // Classe pour qu’on sache quoi supprimer
      form.classList.add("temp-delete-form");

      // Ajout CSRF si nécessaire
      const csrfToken = document.querySelector("input[name='csrf_token']");
      if (csrfToken) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "csrf_token";
        input.value = csrfToken.value;
        form.appendChild(input);
      }

      document.body.appendChild(form);

      // Stocke la référence dans le script global
      const modal = document.getElementById("deleteModal");
      const confirmBtn = document.getElementById("confirmDeleteBtn");

      // Empêche double écoute
      confirmBtn.onclick = null;

      // Montre la modale
      modal.style.display = "flex";

      // Quand on clique sur confirmer, on soumet le form et recharge
      confirmBtn.onclick = () => {
        form.submit();
      };

      // Fermeture / nettoyage géré par le script global
    });

    // Ouvre la modale édition avec données + aperçu image
    document.querySelectorAll(".box_list .item").forEach((item) => {
      // Ignore l'item "ajouter"
      if (item.classList.contains("add-item")) return;

      item.addEventListener("click", () => {
        const id = item.dataset.id;
        const description = item.dataset.description;
        const imgSrc = item.querySelector("img")?.src || "";

        document.getElementById("photoId").value = id;
        document.getElementById("photoDescription").value = description;

        // Met à jour l'aperçu de la photo actuelle
        const previewImg = document.getElementById("currentImagePreview");
        previewImg.src = imgSrc;

        editModal.classList.remove("hidden");
        editModal.style.display = "flex";
      });
    });
  }

  // Lightbox (public)
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const lightboxClose = document.getElementById("lightbox-close");

  if (lightboxClose) {
    lightboxClose.addEventListener("click", () => {
      lightbox.style.display = "none";
      lightboxImg.src = "";
    });

    // Fermer lightbox en cliquant en dehors de l'image
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox) {
        lightbox.style.display = "none";
        lightboxImg.src = "";
      }
    });
  }

  // 👇 Fermer la lightbox avec Échap
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox.style.display === "flex") {
      lightbox.style.display = "none";
      lightboxImg.src = "";
    }
  });

  // Ajout des événements click et hover selon mode admin ou public
  document.querySelectorAll(".box_list .item").forEach((item) => {
    // Ignore l'item "ajouter"
    if (item.classList.contains("add-item")) return;

    if (isAdmin) {
      // Admin : le click ouvre modale édition (déjà géré plus haut)
      // On ne fait rien ici pour éviter double gestion
    } else {
      // Public : clic ouvre lightbox
      item.addEventListener("click", () => {
        const img = item.querySelector("img");
        if (!img) return;

        lightboxImg.src = img.dataset.full || img.src;
        lightbox.style.display = "flex";
      });
    }
  });

  document.querySelectorAll(".box_list .item").forEach((item) => {
    const img = item.querySelector("img");

    item.addEventListener("mouseenter", () => {
      if (img) {
        img.classList.remove("fade-out");
        img.classList.add("fade-in");
      }
    });

    item.addEventListener("mouseleave", () => {
      if (img) {
        img.classList.remove("fade-in");
        img.classList.add("fade-out");
      }
    });
  });
});
