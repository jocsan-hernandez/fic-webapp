// getBadgeOnly.js
let cantidadAnterior = 0;

function actualizarBadge() {
    fetch("/usuarios/obtenerSolicitudes")
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById("badge-solicitudes");
            if (!badge) return; // si no está el badge, salimos

            // asumimos que data es un array
            const cantidad = Array.isArray(data) ? data.length : 0;
            badge.textContent = cantidad;

            if (cantidad > 0) {
                badge.classList.remove("bg-light", "text-dark");
                badge.classList.add("bg-danger", "text-white");
            } else {
                badge.classList.remove("bg-danger", "text-white");
                badge.classList.add("bg-light", "text-dark");
            }

            // reproducir sonido si hay nuevas solicitudes
            if (cantidad > cantidadAnterior) {
                const audio = new Audio("https://www.soundjay.com/buttons/sounds/button-3.mp3");
                audio.play();
            }

            cantidadAnterior = cantidad;
        })
        .catch(err => console.error("Error al actualizar badge:", err));
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarBadge();
    setInterval(actualizarBadge, 60000); // actualizar cada minuto
});