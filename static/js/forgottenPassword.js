document.addEventListener("DOMContentLoaded", () => {
    const formularioDiv = document.querySelector("#formulario");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value; // guardamos CSRF una sola vez

    // Listener del formulario de correo
    const correoForm = formularioDiv.querySelector("form");
    correoForm.addEventListener("submit", function(e) {
        e.preventDefault();

        const correoInput = this.querySelector("input[name='correo']");
        const correo = correoInput.value.trim();

        const formData = new FormData();
        formData.append("correo", correo);

        fetch(window.location.href, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                // Reemplazamos contenido con formulario de código
                formularioDiv.innerHTML = `
                    <h2 id="titulo2">Ingresa el código</h2>
                    <p id="parrafo2">Se envió un código a tu email</p> 
                    
                    <form id='codigoForm'>
                        <div class='codigoContainer'>
                            <input type="text" maxlength="1" class="codigo">
                            <input type="text" maxlength="1" class="codigo">
                            <input type="text" maxlength="1" class="codigo">
                            <input type="text" maxlength="1" class="codigo">
                            <input type="text" maxlength="1" class="codigo">
                            <input type="text" maxlength="1" class="codigo">
                        </div>

                        <button type="submit" class="btn btn-primary" id='verificarCodigo'>
                            Verificar
                        </button>
                    </form>
                `;

                // Enfocamos el primer input
                document.querySelector(".codigo").focus();

                // Activamos comportamiento de las cajas
                activarInputsCodigo();

                // Listener para verificar código
                const codigoForm = document.querySelector("#codigoForm");
                codigoForm.addEventListener("submit", function(e){
                    e.preventDefault();

                    const codigo = [...document.querySelectorAll(".codigo")]
                        .map(input => input.value)
                        .join("");

                    fetch("/usuarios/verify-reset-code/", {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "X-Requested-With": "XMLHttpRequest",
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ codigo: codigo })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if(data.valid){
                            // Código correcto → redirigir a página de cambio de contraseña
                            window.location.href = "/usuarios/resetPassword/";
                        } else {
                            alert("Código incorrecto o expirado");
                        }
                    })
                    .catch(err => console.log("Error:", err));
                });

            } else {
                console.log("Correo no encontrado");
            }
        })
        .catch(error => {
            console.log("Error:", error);
        });
    });
});

// Función para manejar el foco y backspace en las 6 cajas
function activarInputsCodigo(){
    const inputs = document.querySelectorAll(".codigo");

    inputs.forEach((input, index) => {

        input.addEventListener("input", () => {
            if (input.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });

        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && input.value === "" && index > 0) {
                inputs[index - 1].focus();
            }
        });

    });
}