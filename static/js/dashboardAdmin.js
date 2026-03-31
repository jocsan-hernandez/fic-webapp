document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll("#dashboardTabs .nav-link");
    const panes = document.querySelectorAll(".tab-pane");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {

            const tab = btn.getAttribute("data-tab");

            // Activar botón
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Ocultar panes
            panes.forEach(p => {
                p.classList.add("d-none");
                p.classList.remove("active");
            });

            // Mostrar pane seleccionado
            const target = document.getElementById(tab);
            target.classList.remove("d-none");
            target.classList.add("active");

            if (tab === "movimientos") {
                renderMovimientos(target);
            }

        });
    });

});


// Variables globales para charts
let pieChart = null;
let barChart = null;


// ============================
// RENDER UI
// ============================
function renderMovimientos(target) {

    target.innerHTML = `
        <div class="row mb-4">

            <div class="col-md-6">
                <div class="card p-3 shadow-sm border-0">
                    <h6>Total de depósitos</h6>
                    <h3 id="totalDepositos">Cargando...</h3>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card p-3 shadow-sm border-0">
                    <h6>Intereses pagados</h6>
                    <h3 id="totalIntereses">Cargando...</h3>
                </div>
            </div>

        </div>

        <div class="mb-4">
            <button class="btn btn-outline-primary me-2 range-btn active" data-range="1">1 mes</button>
            <button class="btn btn-outline-primary me-2 range-btn" data-range="3">3 meses</button>
            <button class="btn btn-outline-primary me-2 range-btn" data-range="6">6 meses</button>
            <button class="btn btn-outline-primary range-btn" data-range="12">1 año</button>
        </div>

        <div class="row">
            <div class="col-md-6">
                <canvas id="pieChart"></canvas>
            </div>
            <div class="col-md-6">
                <canvas id="barChart"></canvas>
            </div>
        </div>
    `;

    cargarDatos(1);

    const rangeButtons = target.querySelectorAll(".range-btn");

    rangeButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            const meses = btn.getAttribute("data-range");

            // activar botón seleccionado
            rangeButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            cargarDatos(meses);
        });
    });
}


// ============================
// FETCH + UPDATE UI
// ============================
async function cargarDatos(meses = 1) {
    try {
        const res = await fetch(`/usuarios/metricasMovimientos/?meses=${meses}`);
        const data = await res.json();

        // KPI
        document.getElementById("totalDepositos").innerText =
            `L ${Number(data.total_depositos).toFixed(2)}`;

        document.getElementById("totalIntereses").innerText =
            `L ${Number(data.intereses).toFixed(2)}`;

        // Actualizar gráficas
        actualizarGraficas(data);

    } catch (error) {
        console.error("Error al obtener métricas:", error);
    }
}


// ============================
// CHARTS
// ============================
function actualizarGraficas(data) {

    const labels = ["Depósitos", "Retiros", "Intereses"];
    const valores = [data.total_depositos, data.total_retiros, data.intereses];

    // ===== PIE CHART =====
    if (pieChart) {
        pieChart.data.datasets[0].data = valores;
        pieChart.update();
    } else {
        const ctxPie = document.getElementById("pieChart").getContext("2d");

        pieChart = new Chart(ctxPie, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{
                    data: valores
                }]
            }
        });
    }

    // ===== BAR CHART =====
    if (barChart) {
        barChart.data.datasets[0].data = valores;
        barChart.update();
    } else {
        const ctxBar = document.getElementById("barChart").getContext("2d");

        barChart = new Chart(ctxBar, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Monto",
                    data: valores
                }]
            }
        });
    }
}