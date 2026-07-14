export function initToolSelector() {
    let currentTool = "select";

    document.body.classList.add(`tool-${currentTool}`);

    document.querySelectorAll(".tool").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tool").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentTool = btn.dataset.tool;

            document.body.classList.remove(
                "tool-select",
                "tool-watched",
                "tool-delete"
            );

            document.body.classList.add(`tool-${currentTool}`);
        });
    });
}
