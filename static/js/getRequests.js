let cantidadAnterior = 0;

function obtenerSolicitudes(){
    fetch("/usuarios/obtenerSolicitudes")
    .then(
        response=> response.json()
    )
    .then(
        data=>{
            renderSolicitudes(data)

            // actualizar contador
            const badge = document.getElementById("badge-solicitudes");
            badge.textContent = data.length;

            //  cambiar color según cantidad
            if (data.length > 0) {
                badge.classList.remove("bg-light", "text-dark");
                badge.classList.add("bg-danger", "text-white");
            } else {
                badge.classList.remove("bg-danger", "text-white");
                badge.classList.add("bg-light", "text-dark");
            }

            //  detectar nuevas solicitudes
            if (data.length > cantidadAnterior) {
                reproducirSonido();
            }

            cantidadAnterior = data.length;
        }
    )
    .catch(error =>{
        console.log(error)
    })
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

            <!-- Botón desplegable -->
            <button class="btn btn-primary" type="button" data-bs-toggle="collapse" data-bs-target="#detalle${index}">
              Ver más
            </button>

            <div class="collapse mt-3" id="detalle${index}">
              <div class="card card-body">

                <p>
                  <strong>Teléfono:</strong> ${solicitud.telefono}
                </p>

                <a href="#" class="btn btn-outline-success">
                  Registrar
                </a>

              </div>
            </div>

          </div>

        </div>
      </div>
    `;

    contenedor.innerHTML += card;
  });
}

document.addEventListener("DOMContentLoaded", function () {
    obtenerSolicitudes();
        // actualizar cada 60 segundos (60000 ms)
    setInterval(obtenerSolicitudes, 60000);
});

function reproducirSonido() {
    const audio = new Audio("https://www.soundjay.com/buttons/sounds/button-3.mp3");
    audio.play();
}