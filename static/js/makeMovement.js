document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("form-deposito");
    const mensaje = document.getElementById("mensaje-deposito");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const identidad = document.getElementById("identidad").value;
        const tipo = document.getElementById("tipo").value;
        const monto = document.getElementById("monto").value;

        fetch("/depositos/ajax/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: `identidad=${identidad}&tipo=${tipo}&monto=${monto}`
        })
        .then(res => res.json())
        .then(data => {
            // Limpiar cualquier alerta previa
            mensaje.innerHTML = "";

            // Crear alerta de Bootstrap con botón de cierre
            const alerta = document.createElement("div");
            alerta.className = data.success ? "alert alert-success alert-dismissible fade show" : "alert alert-danger alert-dismissible fade show";
            alerta.setAttribute("role", "alert");
            alerta.innerHTML = `
                ${data.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            mensaje.appendChild(alerta);
            if (data.success) {
                form.reset();
            }
        })
        .catch(err => {
            mensaje.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    Error en la solicitud.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        });
    });
});