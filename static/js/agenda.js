window.addEventListener("DOMContentLoaded", () => {
  const list = document.querySelector(".agenda-list");
  const items = document.querySelectorAll(".agenda-item");

  // === SCROLL VERS PROCHAIN ÉVÉNEMENT ===
  const now = new Date();
  let targetIndex = 0;

  items.forEach((item, i) => {
    const endStr = item.getAttribute("data-end");
    if (endStr) {
      const endDate = new Date(endStr);
      if (endDate > now && targetIndex === 0) {
        targetIndex = i;
      }
    }
  });

  items.forEach((item) => {
    const endStr = item.getAttribute("data-end");
    if (endStr) {
      const endDate = new Date(endStr);
      if (endDate < now) {
        item.classList.add("passe");
      }
    }
  });

  const target = items[targetIndex];
  if (target) {
    target.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function updateActiveItem() {
    const listRect = list.getBoundingClientRect();
    let closestItem = null;
    let minDistance = Infinity;

    items.forEach((item) => {
      const itemRect = item.getBoundingClientRect();
      const itemCenter = itemRect.top + itemRect.height / 2;
      const listCenter = listRect.top + listRect.height / 2;
      const distance = Math.abs(listCenter - itemCenter);
      if (distance < minDistance) {
        minDistance = distance;
        closestItem = item;
      }
    });

    items.forEach((item) => item.classList.remove("active"));
    if (closestItem) closestItem.classList.add("active");
  }

  list.addEventListener("scroll", updateActiveItem);
  updateActiveItem();

  // === CLIC POUR CENTRER UN ÉLÉMENT ===
  items.forEach((item) => {
    item.addEventListener("click", () => {
      item.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });

  // === POPUP AJOUT RDV ===
  const popupAdd = document.getElementById("popupBackdrop");
  const closeAddBtn = document.getElementById("closeRdvPopup");
  const openAddBtns = document.querySelectorAll("#openRdvPopup, .openRdvPopup");

  if (popupAdd && closeAddBtn) {
    openAddBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        popupAdd.querySelector("form").reset();
        popupAdd.style.display = "flex";
      });
    });

    closeAddBtn.addEventListener("click", () => {
      popupAdd.style.display = "none";
    });

    popupAdd.addEventListener("click", (e) => {
      if (e.target === popupAdd) {
        popupAdd.style.display = "none";
      }
    });
  }

  // === POPUP ÉDITION RDV ===
  const popupEdit = document.getElementById("popupEditBackdrop");
  const closeEditBtn = document.getElementById("closeEditPopup");
  const deleteForm = document.getElementById("deleteForm");

  if (popupEdit && closeEditBtn) {
    closeEditBtn.addEventListener("click", () => {
      popupEdit.style.display = "none";
    });

    popupEdit.addEventListener("click", (e) => {
      if (e.target === popupEdit) {
        popupEdit.style.display = "none";
      }
    });
  }

  document.querySelectorAll(".agenda-item.clickable").forEach((item) => {
    item.addEventListener("click", () => {
      const id = item.getAttribute("data-id");
      const date = item.getAttribute("data-date");
      const debut = item.getAttribute("data-debut");
      const fin = item.getAttribute("data-fin");
      const desc = item.getAttribute("data-desc");

      document.getElementById("edit_id").value = id;
      document.getElementById("edit_date").value = date;
      document.getElementById("edit_debut").value = debut;
      document.getElementById("edit_fin").value = fin;
      document.getElementById("edit_description").value = desc;

      const editForm = document.getElementById("editRdvForm");
      editForm.action = `/admin/agenda/edit/${id}`;

      if (deleteForm) {
        deleteForm.action = `/admin/agenda/delete/${id}`;
      }

      popupEdit.style.display = "flex";
    });
  });

  // === GESTION DE L'AJOUT DE RÉSULTAT (modale formulaire ajout) ===
  const openBtn = document.getElementById("openFormBtn");
  const ajoutModal = document.getElementById("modalOverlay");
  const closeAjoutBtn = document.getElementById("closeModal");

  if (openBtn) {
    openBtn.addEventListener("click", () => {
      ajoutModal.style.display = "flex";
      document.body.style.overflow = "hidden";
    });
  }

  if (closeAjoutBtn) {
    closeAjoutBtn.addEventListener("click", closeAjoutModal);
  }

  if (ajoutModal) {
    ajoutModal.addEventListener("click", (e) => {
      if (e.target === ajoutModal) closeAjoutModal();
    });
  }

  function closeAjoutModal() {
    ajoutModal.style.display = "none";
    document.body.style.overflow = "auto";
  }

  const input = document.getElementById("pdfInput");
  const filenameSpan = document.getElementById("filename");

  if (input && filenameSpan) {
    input.addEventListener("change", () => {
      filenameSpan.textContent =
        input.files.length > 0 ? input.files[0].name : "Aucun fichier choisi";
    });
  }

  // === MODALE CONFIRMATION SUPPRESSION GLOBALE ===
  const closeModalBtn = document.getElementById("closeModal");
  const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  let formToSubmit = null;
  const deleteForms = document.querySelectorAll(".delete-form");

  deleteForms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      formToSubmit = form;
      ajoutModal.style.display = "flex";
      document.body.style.overflow = "hidden";
    });
  });

  function closeDeleteModal() {
    ajoutModal.style.display = "none";
    document.body.style.overflow = "auto";
    formToSubmit = null;
  }

  if (closeModalBtn) closeModalBtn.addEventListener("click", closeDeleteModal);
  if (cancelDeleteBtn)
    cancelDeleteBtn.addEventListener("click", closeDeleteModal);
  if (ajoutModal) {
    ajoutModal.addEventListener("click", (e) => {
      if (e.target === ajoutModal) closeDeleteModal();
    });
  }

  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", () => {
      if (formToSubmit) formToSubmit.submit();
    });
  }
});
