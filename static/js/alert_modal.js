document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("deleteModal");
  const closeBtn = document.getElementById("closeDeleteModal");
  const cancelBtn = document.getElementById("cancelDeleteBtn");
  const confirmBtn = document.getElementById("confirmDeleteBtn");

  let formToDelete = null;

  // Intercepter les soumissions de formulaire "delete"
  document.querySelectorAll(".delete-resultat-form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault(); // Empêche la soumission immédiate
      formToDelete = form; // Stocke le formulaire
      modal.style.display = "flex"; // Affiche la modale
    });
  });

  // Fermer la modale
  function closeModal() {
    modal.style.display = "none";
    formToDelete = null;
  }

  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  confirmBtn.addEventListener("click", () => {
    if (formToDelete) formToDelete.submit();
    closeModal();
  });
});
