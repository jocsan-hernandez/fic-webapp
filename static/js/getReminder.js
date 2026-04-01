function actualizarBadgeDepositos() {
    const badge = document.getElementById("badge-depositos");
    if (!badge) return;

    const hoy = new Date();
    const dia = hoy.getDate();

    if (dia === 28) {
        
        badge.textContent = "!";
        badge.classList.remove("bg-light", "text-dark");
        badge.classList.add("bg-danger", "text-white");
    } else {
        
        badge.textContent = "";
        badge.classList.remove("bg-danger", "text-white");
        badge.classList.add("bg-light", "text-dark");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarBadgeDepositos();
});