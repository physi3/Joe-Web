const modal = document.getElementById("modal");
const modalContent = document.getElementById("modal-content");
const backdrop = document.querySelector(".modal-backdrop");
const closeButton = document.getElementById("close-modal");

export function initModal() {
    if (!modal) {
        return;
    }

    if (backdrop) {
        backdrop.addEventListener("click", closeModal);
    }

    if (closeButton) {
        closeButton.addEventListener("click", closeModal);
    }
}

export function openModal(html) {
    modalContent.innerHTML = html;
    modal?.classList.remove("hidden");
}

export function closeModal() {
    modal?.classList.add("hidden");
    modalContent.innerHTML = "";
}
