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

function posterClicked(filmId, poster) {
    if (filmId === "add") {
        openModal();
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
    poster.remove();
    console.log("Deleting film", filmId);
}

function markWatched(filmId, poster) {
    poster.classList.toggle("unwatched")
    console.log("Marking film as watched", filmId);
}
