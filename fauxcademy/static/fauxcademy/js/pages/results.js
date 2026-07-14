let categoryIndex = 0;


const categoryName = document.getElementById("category-name");
const nominees = document.getElementById("nominees");

const previousButton = document.getElementById("previous-category");
const nextButton = document.getElementById("next-category");

const winner = document.getElementById("winner");
const winnerPoster = document.getElementById("winner-poster");
const winnerName = document.getElementById("winner-name");
const winnerAnchor = document.getElementById("winner-anchor");
const revealButton = document.getElementById("reveal-winner");

function showCategory(index) {
    window.scrollTo(0, 0);

    const category = results[index];

    categoryName.textContent = category.name;

    nominees.innerHTML = "";

    winner.classList.add("hidden");
    revealButton.classList.add("hidden");
    winnerAnchor.classList.remove("hidden")

    category.nominees.forEach((nominee, i) => {

        const card = document.createElement("div");

        card.className="nominee";

        card.style.animationDelay = `${i * 300}ms`;

        card.innerHTML = `
            <img src="${nominee.poster_url}">
            <div class="nominee-title">
                ${nominee.str}
            </div>
        `;

        nominees.appendChild(card);
    });

    updateNavigation()

    setTimeout(() => {

        revealButton.classList.remove("hidden");

    }, category.nominees.length * 300 + 800);
}

function updateNavigation() {
    previousButton.disabled = categoryIndex === 0;
    nextButton.disabled = categoryIndex === results.length - 1;
}

function revealWinner(category) {

    const winning = category.nominees.find(
        n => n.winner
    );

    if (!winning) return;


    winnerPoster.src = winning.poster_url;
    winnerName.textContent = winning.title;


    // Scroll into position before revealing
    winnerAnchor.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });


    setTimeout(() => {
        winner.classList.remove("hidden");
        winnerAnchor.classList.add("hidden")
    }, 800);

}



document
.getElementById("next-category")
.addEventListener("click",()=>{

    categoryIndex =
        (categoryIndex + 1) % results.length;

    showCategory(categoryIndex);

});


document
.getElementById("previous-category")
.addEventListener("click",()=>{

    categoryIndex =
        (categoryIndex - 1 + results.length)
        % results.length;

    showCategory(categoryIndex);

});

revealButton.addEventListener("click", () => {

    const category = results[categoryIndex];

    revealWinner(category);

    revealButton.classList.add("hidden");

});

window.scrollTo(0, 0);
showCategory(0);