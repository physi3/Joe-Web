const input = document.getElementById("film-search-input");
const results = document.getElementById("search-results");
let debounceTimer;

export function initSearch() {
    if (!input || !results) {
        return;
    }

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
    await fetch("add-film/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify(film),
    });

    location.reload();
}
