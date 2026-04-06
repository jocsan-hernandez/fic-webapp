let cantidadAnterior = 0;

function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

function obtenerSolicitudes(){
    fetch("/usuarios/obtenerSolicitudes")
    .then(response => response.json())
    .then(data => {
        renderSolicitudes(data);

        const badge = document.getElementById("badge-solicitudes");
        badge.textContent = data.length;

        if (data.length > 0) {
            badge.classList.remove("bg-light", "text-dark");
            badge.classList.add("bg-danger", "text-white");
        } else {
            badge.classList.remove("bg-danger", "text-white");
            badge.classList.add("bg-light", "text-dark");
        }

        if (data.length > cantidadAnterior) {
            reproducirSonido();
        }

        cantidadAnterior = data.length;
    })
    .catch(error => {
        console.log(error);
    });
}

function renderSolicitudes(data) {
    const contenedor = document.getElementById("contenedor-solicitudes");

    contenedor.innerHTML = "";

    if (data.length === 0) {
        contenedor.innerHTML = "<p>No hay solicitudes aún.</p>";
        return;
    }

    data.forEach((solicitud, index) => {
        const card = `
        <div class="col-12 mb-3">
            <div class="card shadow-sm">

                <div class="card-body">
                    <h5 class="card-title">
                        ${solicitud.nombreCompleto}
                    </h5>

                    <button class="btn btn-primary" type="button" data-bs-toggle="collapse" data-bs-target="#detalle${index}">
                        Ver más
                    </button>

                    <div class="collapse mt-3" id="detalle${index}">
                        <div class="card card-body">

                            <p>
                                <strong>Teléfono:</strong> ${solicitud.telefono}
                            </p>

                            <div class="d-flex gap-2">
                                <a href="#" class="btn btn-outline-success">
                                    Registrar
                                </a>

                                <a href="#" 
                                   class="btn btn-outline-danger btn-eliminar"
                                   data-id="${solicitud.id}">
                                    Eliminar
                                </a>
                            </div>

                        </div>
                    </div>

                </div>

            </div>
        </div>
        `;

        contenedor.innerHTML += card;
    });
}

// Delegación de eventos para botones eliminar
document.addEventListener("click", function (e) {
    if (e.target.classList.contains("btn-eliminar")) {
        e.preventDefault();

        const id = e.target.getAttribute("data-id");


        fetch(`/usuarios/delete/${id}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                obtenerSolicitudes(); // recarga sin refresh
            } else {
                alert(data.error || "Error al eliminar");
            }
        })
        .catch(error => {
            console.log(error);
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    obtenerSolicitudes();

    setInterval(obtenerSolicitudes, 60000);
});

function reproducirSonido() {
    const audio = new Audio("https://www.soundjay.com/buttons/sounds/button-3.mp3");
    audio.play();
}

