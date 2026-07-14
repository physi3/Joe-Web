import { getCsrfToken } from "../components/csrf.js";

document.addEventListener('DOMContentLoaded', () => {
    const resultsToggle = document.getElementById("results-toggle");
    
    resultsToggle.addEventListener("change", async () => {

        const revealed = resultsToggle.checked;


        const response = await fetch(
            "../reveal_results/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                },

                body: JSON.stringify({
                    revealed: revealed
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            alert(data.error || "Something went wrong.");

            // revert switch if failed
            resultsToggle.checked = !revealed;

            return;
        }


        console.log(
            data.results_revealed
                ? "Results revealed"
                : "Results hidden"
        );

    });
});