document.addEventListener("DOMContentLoaded", () => {

    // Cargar valor inicial (1 mes)
    cargarTasa("1m");

    const botones = document.querySelectorAll(".periodo-btn");

    botones.forEach(btn => {
        btn.addEventListener("click", () => {

            const periodo = btn.getAttribute("data-periodo");

            // UI active
            botones.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Cargar datos
            cargarTasa(periodo);
        });
    });

});


// ============================
// FETCH TASA
// ============================
async function cargarTasa(periodo) {

    try {
        const res = await fetch(`/depositos/calculoIntereses/${periodo}/`);
        const data = await res.json();

        if (data.error) {
            console.error("Error del servidor:", data.error);
            return;
        }

        // Actualizar UI
        document.getElementById("capital").innerText =
            `L ${Number(data.capital).toFixed(2)}`;

        document.getElementById("capitalPromedio").innerText =
            `L ${Number(data.capital_promedio).toFixed(2)}`;

        document.getElementById("intereses").innerText =
            `L ${Number(data.intereses_pagados).toFixed(2)}`;

        document.getElementById("tasa").innerText =
            `${(Number(data.tasa) * 100).toFixed(2)}%`;

    } catch (error) {
        console.error("Error al obtener tasa:", error);
    }
}