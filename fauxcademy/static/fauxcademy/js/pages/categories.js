import { openModal } from "../components/modal.js";
import { getCsrfToken } from "../components/csrf.js";

document.addEventListener('DOMContentLoaded', () => {
    const modalHtml = document.getElementById("create-category-modal-template").innerHTML;

    document.querySelector("#add-category-button").addEventListener("click", () => {
        openModal(modalHtml);

        document.getElementById("create-category-button")
        ?.addEventListener("click", () => {
            createCategory();
        });
    })
});

async function createCategory() {
    const name = document.getElementById("category-name").value;
    const description = document.getElementById("category-description").value;
    const nomineeType = document.getElementById("category-type").value;
    const priority = document.getElementById("category-priority").value;

    const response = await fetch(
        `create-category/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify({
                name: name,
                description: description,
                nominee_type: nomineeType,
                importance: priority
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        alert(data["error"]["importance"] || "Failed to create category.");
        return;
    }

    window.location.reload();
}
