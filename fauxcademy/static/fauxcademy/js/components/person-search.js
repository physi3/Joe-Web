import { getCsrfToken } from "./csrf.js";

export let input, results, debounceTimer;

export function renderResults(people, addPersonFunction) {
    results.innerHTML = "";

    people.forEach(person => {
        const div = document.createElement("div");
        div.className = "result";

        div.innerHTML = `
            <img src="${person.profile}" width="40" />
            <span><b>${person.name}</b> - ${person.job}${person.character}</span>
            <button>Add</button>
        `;

        div.querySelector("button").addEventListener("click", () => {
            addPersonFunction(person);
        });

        results.appendChild(div);
    });
}

export function initPersonSearch(filmId, categoryType, addPersonFunction) {
    input = document.getElementById("person-search-input");
    results = document.getElementById("search-results");

    if (!input || !results) {
        return;
    }

    console.log("Initializing person search...");

    function personSearch(){
        clearTimeout(debounceTimer);

        debounceTimer = setTimeout(async () => {
            const query = input.value;

            const res = await fetch(`/fauxcademy/person-search/?movie_id=${encodeURIComponent(filmId)}&type=${encodeURIComponent(categoryType)}&q=${encodeURIComponent(query)}`);
            const data = await res.json();

            renderResults(data.results, addPersonFunction);
        }, 300);
    }

    personSearch();
    input.addEventListener("input", () => {
        personSearch();
    });
}