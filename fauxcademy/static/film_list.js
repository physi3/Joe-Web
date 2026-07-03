let currentTool = "select";

document.body.classList.add(`tool-${currentTool}`);

/* TOOL SWITCHING */
document.querySelectorAll(".tool").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tool").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        currentTool = btn.dataset.tool;

        document.body.classList.remove(
            "tool-select",
            "tool-watched",
            "tool-unwatched",
            "tool-delete"
        );

        document.body.classList.add(`tool-${currentTool}`);
    });
});

document.querySelectorAll(".poster").forEach(poster => {
    poster.addEventListener("click", () => {
        const filmId = poster.dataset.filmId;
        posterClicked(filmId, poster);
    });
});


const modal = document.getElementById("add-film-modal");

function posterClicked(filmId, poster) {
    if (filmId === "add") {
        modal.classList.remove("hidden");
        return;
    }

    // Decide what to do based on the current tool
    switch (currentTool) {
        case "delete":
            deleteFilm(filmId, poster);
            break;

        case "watched":
            markWatched(filmId, poster);
            break;

        case "select":
            toggleSelection(filmId, poster);
            break;
    }
}

function deleteFilm(filmId, poster) {
    poster.remove();

    console.log("Deleting film", filmId);
}

function markWatched(filmId, poster) {
    console.log(poster.classList)
    console.log(poster.classList.contains("unwatched"))
    if (poster.classList.contains("unwatched")) {
        poster.classList.remove("unwatched");
    } else {
        poster.classList.add("unwatched");
    }

    console.log("Marking film as watched", filmId);
}

function toggleSelection(filmId) {
    console.log("selected", filmId);
}


document.querySelector(".modal-backdrop").addEventListener("click", closeModal);
document.getElementById("close-modal").addEventListener("click", closeModal);

function closeModal() {
    modal.classList.add("hidden");
}


const input = document.getElementById("film-search-input");
const results = document.getElementById("search-results");

let debounceTimer;

input.addEventListener("input", () => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(async () => {
        const query = input.value;

        if (query.length < 2) return;

        const res = await fetch(`/fauxcademy/film-search/?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        renderResults(data.results);
    }, 300);
});

function renderResults(films) {
    results.innerHTML = "";

    films.forEach(film => {
        const div = document.createElement("div");
        div.className = "result";

        div.innerHTML = `
            <img src="${film.poster}" width="40" />
            <span>${film.title} (${film.year || "Unknown"})</span>
            <button>Add</button>
        `;

        div.querySelector("button").addEventListener("click", () => {
            addFilm(film);
        });

        results.appendChild(div);
    });
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

async function addFilm(film) {
    console.log("Adding film", film);
    
    await fetch("add-film/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(film)
    });

    location.reload(); // simple first version
}