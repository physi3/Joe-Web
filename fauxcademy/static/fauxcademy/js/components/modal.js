const modal = document.getElementById("add-film-modal");
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

export function openModal() {
    modal?.classList.remove("hidden");
}

export function closeModal() {
    modal?.classList.add("hidden");
}
