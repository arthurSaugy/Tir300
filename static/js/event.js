function openModal(id) {
  document.getElementById(id).style.display = "flex";
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

window.addEventListener("click", function (e) {
  document.querySelectorAll(".modal-backdrop").forEach((modal) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});

const flyer1Input = document.getElementById("flyer1_file");
const flyer2Input = document.getElementById("flyer2_file");

if (flyer1Input) {
  flyer1Input.addEventListener("change", () => {
    document.getElementById("filename1").textContent =
      flyer1Input.files[0]?.name || "Aucun fichier choisi";
  });
}

if (flyer2Input) {
  flyer2Input.addEventListener("change", () => {
    document.getElementById("filename2").textContent =
      flyer2Input.files[0]?.name || "Aucun fichier choisi";
  });
}
