import { getCsrfToken } from "./csrf.js";

export let input, results, debounceTimer;

export function initFilmSearch() {
    input = document.getElementById("film-search-input");
    results = document.getElementById("search-results");

    if (!input || !results) {
        return;
    }

    console.log("Initializing film search...");

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
}

export function renderResults(films) {
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

async function addFilm(film) {
    const csrfToken = getCsrfToken();

    if (!csrfToken) {
        console.error("CSRF token missing");
        return;
    }

    await fetch("add-film/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(film),
    });

    location.reload();
}
