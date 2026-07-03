import { openModal } from "./modal.js";

export function initPosterActions() {
    document.querySelectorAll(".poster").forEach(poster => {
        poster.addEventListener("click", () => {
            const filmId = poster.dataset.filmId;
            posterClicked(filmId, poster);
        });
    });
}

function getCurrentTool() {
    if (document.body.classList.contains("tool-delete")) {
        return "delete";
    }
    if (document.body.classList.contains("tool-watched")) {
        return "watched";
    }
    return "select";
}

function openAddFilmModal() {
    openModal(`
            <h2>Add Film</h2>

            <input id="film-search-input" type="text" placeholder="Search TMDB..." />

            <div id="search-results" class="search-results"></div>

            <button id="close-modal">Close</button>
    `);
}

function openDeleteModal(filmId, filmTitle) {
    openModal(`
        <h2>Delete Film</h2>

        <p>Are you sure you want to delete <strong>${filmTitle}</strong>?</p>

        <div class="modal-actions">
            <button onclick="deleteFilm(${filmId})" class="danger">
                Delete
            </button>

            <button onclick="closeModal()">
                Cancel
            </button>
        </div>
    `);
}

function posterClicked(filmId, poster) {
    if (filmId === "add") {
        openAddFilmModal();
        return;
    }

    switch (getCurrentTool()) {
        case "delete":
            deleteFilm(filmId, poster);
            break;
        case "watched":
            markWatched(filmId, poster);
            break;
        case "select":
            
            break;
    }
}

function deleteFilm(filmId, poster) {
    openDeleteModal(filmId, poster.dataset.filmTitle);
    poster.remove();
    console.log("Deleting film", filmId);
}

function markWatched(filmId, poster) {
    poster.classList.toggle("unwatched")
    console.log("Marking film as watched", filmId);
}
