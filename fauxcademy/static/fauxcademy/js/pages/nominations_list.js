import { initPersonSearch } from '../components/person-search.js';
import { openModal } from '../components/modal.js';
import { getCsrfToken } from "../components/csrf.js";

let nominationState = {
    filmId: null,
    filmTitle: null,
    posterUrl: null,
    categoryId: null,
    categoryName: null,
    categoryType: null,
};

document.addEventListener('DOMContentLoaded', () => {
    let poster_add = document.getElementById("poster-add")

    let openNewNominationModalPoster = () => {openNewNominationModal(posterContent)}
    poster_add.addEventListener("click", openNewNominationModalPoster);

    const categoryData = JSON.parse(
        document.getElementById("category-data").textContent
    );

    document.querySelectorAll(".poster").forEach(poster => {
        poster.addEventListener("click", () => {
            posterClick(poster)
        });
    });

    nominationState.categoryId = categoryData.id;
    nominationState.categoryName = categoryData.name;
    nominationState.categoryType = categoryData.nomineeType;

    document.querySelectorAll(".vote-button").forEach(button => {
        button.addEventListener("click", () => {
            castVote(
                button.dataset.nominationId,
                button.dataset.choice,
                button
            );
        });
    });
})

function openNewNominationModal(posterContent) {
    openModal(`
            <h2>New Nomination</h2>

            <div class="carousel-container">

                <button class="carousel-button left" type="button">
                    <i data-lucide="chevron-left"></i>
                </button>

                <div class="poster-grid mini" id="film-carousel">
                    ${posterContent}
                </div>

                <button class="carousel-button right" type="button">
                    <i data-lucide="chevron-right"></i>
                </button>

            </div>
                
            <div class="carousel-selected-film" id="selected-film-title">
                Select a film
            </div>

            <div class="modal-actions">
                <button type="button" id="next-button" data-modal-next disabled>
                    Next
                </button>

                <button type="button" data-modal-close>
                    Close
                </button>
            </div>
    `);

    nominationState.filmId = nominationState.filmTitle = nominationState.posterUrl = null;
    nominationState.personName = nominationState.personRole = nominationState.personId = null;

    let modalContent = document.getElementById("modal-content");

    modalContent.querySelectorAll("[data-modal-next]").forEach(button => {
        if (nominationState.categoryType == "film"){
            button.addEventListener("click", openNominationDetailsModal);
        } else {
            button.addEventListener("click", openPersonModal);
        }
    });
    initCarousel();
}

function initCarousel(){
    let carousel = document.getElementById("film-carousel");

    document.querySelector(".carousel-button.left").addEventListener("click", () => {
        carousel.scrollBy({
            left: -400,
            behavior: "smooth"
        });
    });

    document.querySelector(".carousel-button.right").addEventListener("click", () => {
        carousel.scrollBy({
            left: 400,
            behavior: "smooth"
        });
    });

    let selectedTitle = document.getElementById("selected-film-title");
    let nextButton = document.getElementById("next-button");

    document.querySelectorAll("#film-carousel .poster").forEach(poster => {
        poster.addEventListener("click", () => {
            nominationState.filmId = poster.dataset.filmId;
            nominationState.filmTitle = poster.dataset.filmTitle;
            nominationState.posterUrl = poster.querySelector("img").src;

            selectedTitle.textContent = poster.dataset.filmTitle;

            document
                .querySelectorAll("#film-carousel .poster")
                .forEach(p => p.classList.remove("selected"));

            poster.classList.add("selected");

            nextButton.disabled = false;
        });
    });
}

function posterClick(poster){
    nominationState.filmTitle = poster.dataset.filmTitle;
    nominationState.posterUrl = poster.querySelector("img").src;
    nominationState.personName = poster.dataset.personName;
    nominationState.personRole = poster.dataset.personRole;

    openNominationDetailsModal(false);
}

function openNominationDetailsModal(create=true) {
    openModal(`
        ${create?`<h2>New Nomination</h2>`:""}
        
        <div class="nomination-film">

            <img 
                src="${nominationState.posterUrl}" 
                alt="${nominationState.filmTitle}"
            >

            <div class="carousel-selected-film">
                ${nominationState.filmTitle}
            </div>

            ${
                nominationState.personName 
                ? `<div class="nomination-person">${nominationState.personName}<div class="role">${nominationState.personRole}</div></div>`
                : ""
            }

        </div>

        <div class="nomination-category">
            for the category
            <span>${nominationState.categoryName}</span>
        </div>

        <!--
        <div class="nomination-notes">
            <label for="nomination-notes-input">
                Extra notes
            </label>

            <textarea
                id="nomination-notes-input"
                placeholder="Why does this deserve a nomination?"
            ></textarea>
        </div>-->

        <div class="modal-actions">
            ${create?`<button type="button" id="create-nomination-button">
                Create
            </button>`:""}
            
            <button type="button" data-modal-close>
                Close
            </button>
        </div>
    `);

    let nomination_create = document.getElementById("create-nomination-button")
    nomination_create.addEventListener("click", createNomination);
}

function capitalizeFirstLetter(val) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

function openPersonModal() {
    openModal(`
            <h2>New Nomination</h2>

            <h3>Nominate a Person For ${nominationState.categoryName}</h3>

            <input id="person-search-input" type="text" placeholder="Search ${nominationState.filmTitle} ${capitalizeFirstLetter(nominationState.categoryType)}..." />

            <div id="search-results" class="search-results"></div>

            <button type="button" data-modal-close>
                Close
            </button>
    `);

    initPersonSearch(nominationState.filmId, nominationState.categoryType, addPerson);
}

function addPerson(person) {
    nominationState.personName = person.name;
    nominationState.personRole = `${person.job}${person.character}`;
    nominationState.personId = person.tmdb_id;
    nominationState.posterUrl = person.profile;

    openNominationDetailsModal();
}

async function createNomination() {
    const csrfToken = getCsrfToken();

    if (!csrfToken) {
        console.error("CSRF token missing");
        return;
    }

    let data = {
        "film": nominationState.filmId,
    }

    if (nominationState.personId != null){
        data["nominated_person"] = nominationState.personId;
        data["nominated_role"] = nominationState.personRole;
    }


    await fetch("add-nomination/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(data),
    });

    location.reload();
}

async function castVote(id, place, button) {
    document.querySelectorAll(`.vote-button[data-choice="${place}"]`).forEach(button => {
        button.classList.remove("selected");
    });

    let card = document.querySelector(`#poster-card-${id}`)

    card.querySelectorAll("button").forEach(button => {
        button.classList.remove("selected");
    });

    button.classList.add("selected");

    // Cast vote with server

    const csrfToken = getCsrfToken();

    if (!csrfToken) {
        console.error("CSRF token missing");
        return;
    }

    let data = {
        "nomination": id,
        "place": place,
    }

    let response = await fetch("vote/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(data),
    });

    console.log(await response.json())

    location.reload();
}

window.castVote = castVote