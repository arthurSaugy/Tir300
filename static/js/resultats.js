const openBtn = document.getElementById("openFormBtn");
const modalAdd = document.getElementById("addModal");
const closeBtnAdd = document.getElementById("closeAddModal");

openBtn.addEventListener("click", () => {
  modalAdd.style.display = "flex";
  document.body.style.overflow = "hidden";
});

closeBtnAdd.addEventListener("click", () => {
  modalAdd.style.display = "none";
  document.body.style.overflow = "auto";
});

modalAdd.addEventListener("click", (e) => {
  if (e.target === modalAdd) {
    modalAdd.style.display = "none";
    document.body.style.overflow = "auto";
  }
});
