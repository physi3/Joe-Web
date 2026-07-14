import { openModal } from "../components/modal.js";
import { getCsrfToken } from "../components/csrf.js";

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#add-list-button").addEventListener("click", () => {
        openModal(`
            <h2>Create Award</h2>

            <div class="modal-form">

                <div class="form-row">
                    <label for="award-name">Name</label>
                    <input 
                        type="text"
                        id="award-name"
                        placeholder="e.g. The Fauxcademy Awards"
                    >
                </div>

                <div class="form-row">
                    <label for="award-description">Description</label>
                    <textarea
                        id="award-description"
                        placeholder="What are these awards celebrating?"
                    ></textarea>
                </div>

            </div>

            <div class="modal-actions">

                <button type="button" id="create-award-button">
                    Create
                </button>

                <button type="button" data-modal-close>
                    Close
                </button>

            </div>`);

        document.getElementById("create-award-button")
        ?.addEventListener("click", () => {
            createAward();
        });
    })
});


async function createAward() {
    const name = document.getElementById("award-name").value;
    const description = document.getElementById("award-description").value;

    const response = await fetch("create-award/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken()
        },
        body: JSON.stringify({
            name: name,
            description: description
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Failed to create award.");
        return;
    }

    window.location.href = data.award.url;
}