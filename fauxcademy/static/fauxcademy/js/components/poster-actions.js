import { openModal, closeModal } from "./modal.js";
import { initFilmSearch } from "./film-search.js";
import { getCsrfToken } from "./csrf.js";

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

async function deleteFilm(filmId) {
    const csrfToken = getCsrfToken();

    if (!csrfToken) {
        console.error("CSRF token missing");
        return;
    }

    let response = await fetch("remove-film/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ tmdb_id: filmId }),
    });

    if (!response.ok) {
        console.error("Failed to delete film", response.status, response.statusText);
        return;
    }

    let poster = document.getElementById(`${filmId}-poster`);
    if (poster) {
        poster.remove();
    }
}

async function markWatched(filmId, poster) {
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error("CSRF token missing");
        return;
    }

    const isUnwatched = poster.classList.toggle("unwatched");
    const watched = !isUnwatched;

    const response = await fetch("watch-film/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
            tmdb_id: filmId,
            watched,
        }),
    });

    console.log(await response.json());

    if (!response.ok) {
        poster.classList.toggle("unwatched");
        let errorText = response.statusText;

        try {
            const data = await response.json();
            if (data?.error) {
                errorText = data.error;
            }
        } catch {
            console.error("Failed to parse error response as JSON");
        }

        console.error("Failed to update watched status:", errorText);
    }
}

function openAddFilmModal() {
    openModal(`
            <h2>Add Film</h2>

            <input id="film-search-input" type="text" placeholder="Search TMDB..." />

            <div id="search-results" class="search-results"></div>

            <button type="button" data-modal-close>
                Close
            </button>
    `);

    initFilmSearch();
}

async function openViewModal(filmId){
    let response = await fetch(`film-details/?id=${encodeURIComponent(filmId)}`);
    let json = await response.json();
    openModal(json["html"]);
}

function openDeleteModal(filmId, filmTitle) {
    openModal(`
        <h2>Delete Film</h2>

        <p>Are you sure you want to delete <strong>${filmTitle}</strong>?</p>

        <div class="modal-actions">
            <button type="button" id="delete-confirm-btn" class="danger">
                Delete
            </button>

            <button type="button" data-modal-close>
                Cancel
            </button>
        </div>
    `);

    const deleteButton = document.getElementById("delete-confirm-btn");
    if (deleteButton) {
        deleteButton.addEventListener("click", () => {
            deleteFilm(filmId);
            closeModal();
        });
    }
}

function posterClicked(filmId, poster) {
    if (filmId === "add") {
        openAddFilmModal();
        return;
    }

    switch (getCurrentTool()) {
        case "delete":
            openDeleteModal(filmId, poster.dataset.filmTitle);
            break;
        case "watched":
            markWatched(filmId, poster);
            break;
        case "select":
            openViewModal(filmId);
            break;
    }
}
