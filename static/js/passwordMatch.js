document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#formulario form");
    const pswd = document.getElementById("pswd");
    const pswdConfirmar = document.getElementById("pswdConfirmar");

    // Crear un contenedor para el alert si no existe
    let alertContainer = document.createElement("div");
    form.prepend(alertContainer);

    form.addEventListener("submit", (e) => {
        // Limpiamos cualquier alert previo
        alertContainer.innerHTML = "";

        if (pswd.value !== pswdConfirmar.value) {
            e.preventDefault(); // Evita enviar el formulario

            // Crear alert Bootstrap
            const alertDiv = document.createElement("div");
            alertDiv.className = "alert alert-danger alert-dismissible fade show";
            alertDiv.role = "alert";
            alertDiv.innerHTML = `
                Las contraseñas no coinciden.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            alertContainer.appendChild(alertDiv);

            pswd.focus();
        }
    });
});

