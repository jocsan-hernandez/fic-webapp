document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll("#dashboardTabs .nav-link");
    const panes = document.querySelectorAll(".tab-pane");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {

            const tab = btn.getAttribute("data-tab");

            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            panes.forEach(p => {
                p.classList.add("d-none");
                p.classList.remove("active");
            });

            const target = document.getElementById(tab);
            target.classList.remove("d-none");
            target.classList.add("active");

            if (tab === "movimientos") {
                if (pieChart) {
                    pieChart.destroy();
                    pieChart = null;
                }

                if (barChart) {
                    barChart.destroy();
                    barChart = null;
                }
                renderMovimientos(target);
            }

            if (tab === "mapa") {
                renderMapa(target);
            }

        });
    });

});


// ============================
// VARIABLES CHARTS
// ============================
let pieChart = null;
let barChart = null;


// ============================
// MAPA HONDURAS
// ============================
function renderMapa(target) {

    target.innerHTML = `
        <div class="card p-3 shadow-sm border-0">
            <h5 class="mb-3">Mapa de Honduras</h5>

            <div style="display:flex; gap:20px; align-items:flex-start;">

                <div style="position: relative; flex:1;">
                    
                    <div id="tooltip-map" style="
                        position:absolute;
                        background:black;
                        color:white;
                        padding:5px 10px;
                        border-radius:5px;
                        font-size:12px;
                        display:none;
                        pointer-events:none;
                        z-index:10;
                        white-space: nowrap;
                    "></div>

                    <div id="map-container" style="width:100%; max-width:800px; margin:auto;"></div>

                </div>

                <div id="legend" style="min-width:180px;"></div>

            </div>
        </div>
    `;

    cargarSVG();
}


// ============================
// CARGAR SVG
// ============================
function cargarSVG() {

    fetch("/static/IMG/HN.svg")
        .then(res => res.text())
        .then(svgText => {

            const container = document.getElementById("map-container");
            container.innerHTML = svgText;

            const svg = container.querySelector("svg");

            svg.style.width = "100%";
            svg.style.height = "auto";
            svg.removeAttribute("width");
            svg.removeAttribute("height");

            inicializarMapaInline(svg);
            cargarDatosMapa(svg);

        })
        .catch(err => console.error("Error cargando SVG:", err));
}


// ============================
// INTERACCIONES
// ============================
function inicializarMapaInline(svg) {

    const tooltip = document.getElementById("tooltip-map");

    const departamentos = {
        HNAT: "Atlántida",
        HNCH: "Choluteca",
        HNCL: "Colón",
        HNCM: "Comayagua",
        HNCP: "Copán",
        HNCR: "Cortés",
        HNEP: "El Paraíso",
        HNFM: "Francisco Morazán",
        HNGD: "Gracias a Dios",
        HNIB: "Islas de la Bahía",
        HNIN: "Intibucá",
        HNLE: "Lempira",
        HNLP: "La Paz",
        HNOC: "Ocotepeque",
        HNOL: "Olancho",
        HNSB: "Santa Bárbara",
        HNVA: "Valle",
        HNYO: "Yoro"
    };

    Object.keys(departamentos).forEach(id => {

        const el = svg.getElementById(id);
        if (!el) return;

        el.style.cursor = "pointer";
        el.style.stroke = "#374151";
        el.style.strokeWidth = "1";

        el.addEventListener("mousemove", (e) => {

            tooltip.style.display = "block";

            const rect = document.getElementById("map-container").getBoundingClientRect();

            tooltip.style.left = (e.clientX - rect.left + 12) + "px";
            tooltip.style.top = (e.clientY - rect.top - 28) + "px";

            const name = el.dataset.name || departamentos[id];
            const value = el.dataset.value || 0;

            tooltip.innerText = `${name}: ${value}`;

            el.style.stroke = "#111827";
            el.style.strokeWidth = "2";
        });

        el.addEventListener("mouseleave", () => {

            tooltip.style.display = "none";

            el.style.stroke = "#374151";
            el.style.strokeWidth = "1";
        });

    });
}


// ============================
// HEATMAP + LEYENDA
// ============================
async function cargarDatosMapa(svg) {

    try {
        const res = await fetch("/usuarios/clientesPorDepartamento/");
        const data = await res.json();

        const mapping = {
            "Atlántida": "HNAT",
            "Choluteca": "HNCH",
            "Colón": "HNCL",
            "Comayagua": "HNCM",
            "Copán": "HNCP",
            "Cortés": "HNCR",
            "El Paraíso": "HNEP",
            "Francisco Morazán": "HNFM",
            "Gracias a Dios": "HNGD",
            "Islas de la Bahía": "HNIB",
            "Intibucá": "HNIN",
            "Lempira": "HNLE",
            "La Paz": "HNLP",
            "Ocotepeque": "HNOC",
            "Olancho": "HNOL",
            "Santa Bárbara": "HNSB",
            "Valle": "HNVA",
            "Yoro": "HNYO"
        };

        const values = Object.values(data);
        const max = Math.max(...values, 1);

        Object.keys(mapping).forEach(dep => {

            const id = mapping[dep];
            const el = svg.getElementById(id);

            if (!el) return;

            const value = data[dep] || 0;

            const intensidad = value / max;

            // 🎨 Gradiente suave azul
            const hue = 210;
            const lightness = 92 - intensidad * 50;
            const color = `hsl(${hue}, 70%, ${lightness}%)`;

            el.style.fill = color;

            el.dataset.name = dep;
            el.dataset.value = value;

        });

        crearLeyenda(max);

    } catch (err) {
        console.error("Error cargando mapa:", err);
    }
}


// ============================
// LEYENDA
// ============================
function crearLeyenda(max) {

    const legend = document.getElementById("legend");
    if (!legend) return;

    legend.innerHTML = "";

    const title = document.createElement("div");
    title.innerText = "Clientes";
    title.style.fontWeight = "bold";
    title.style.marginBottom = "10px";

    legend.appendChild(title);

    const steps = 5;

    for (let i = 0; i <= steps; i++) {

        const intensity = i / steps;
        const value = Math.round((max / steps) * i);

        const lightness = 92 - intensity * 50;
        const color = `hsl(210, 70%, ${lightness}%)`;

        const row = document.createElement("div");
        row.style.display = "flex";
        row.style.alignItems = "center";
        row.style.marginBottom = "6px";

        const box = document.createElement("div");
        box.style.width = "18px";
        box.style.height = "18px";
        box.style.background = color;
        box.style.marginRight = "8px";
        box.style.border = "1px solid #ccc";

        const label = document.createElement("span");
        label.innerText = value;

        row.appendChild(box);
        row.appendChild(label);

        legend.appendChild(row);
    }
}


// ============================
// MOVIMIENTOS (NO CAMBIADO)
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

            rangeButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            cargarDatos(meses);
        });
    });
}


// ============================
// FETCH MOVIMIENTOS
// ============================
async function cargarDatos(meses = 1) {
    try {
        const res = await fetch(`/usuarios/metricasMovimientos/?meses=${meses}`);
        const data = await res.json();

        document.getElementById("totalDepositos").innerText =
            `L ${Number(data.total_depositos).toFixed(2)}`;

        document.getElementById("totalIntereses").innerText =
            `L ${Number(data.intereses).toFixed(2)}`;

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