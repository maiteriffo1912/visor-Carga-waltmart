<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Optimización de Estiba - Tech Ops</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.5/xlsx.full.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.23/jspdf.plugin.autotable.min.js"></script>

    <style>
        body { margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #222; color: white; }
        
        /* Panel Lateral de Control */
        #ui-panel {
            position: absolute; top: 10px; left: 10px; width: 320px;
            background: rgba(30, 30, 30, 0.9); padding: 15px; border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 10;
            border: 1px solid #444;
        }

        h2 { margin: 0 0 15px 0; font-size: 18px; color: #007dc6; border-bottom: 1px solid #444; padding-bottom: 5px; }
        
        .control-group { margin-bottom: 12px; }
        label { display: block; font-size: 12px; color: #aaa; margin-bottom: 4px; }
        select, button { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #555; background: #333; color: white; cursor: pointer; }
        button { background: #007dc6; border: none; font-weight: bold; margin-top: 5px; transition: 0.3s; }
        button:hover { background: #005a91; }
        button.secondary { background: #4caf50; }

        /* KPIs */
        .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        .kpi-card { background: #2a2a2a; padding: 10px; border-radius: 4px; text-align: center; border-left: 3px solid #007dc6; }
        .kpi-label { font-size: 10px; text-transform: uppercase; color: #888; }
        .kpi-val { font-size: 16px; font-weight: bold; margin-top: 2px; }
        
        .status-ok { color: #4caf50; }
        .status-warn { color: #ffc107; }
        .status-err { color: #f44336; }

        /* Tooltip 3D */
        #tooltip {
            position: absolute; display: none; background: rgba(0,0,0,0.8);
            padding: 8px; border-radius: 4px; font-size: 12px; pointer-events: none;
            border: 1px solid #666; z-index: 20;
        }

        /* Modal Manifiesto */
        #modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 100;
        }
        #modal-content {
            background: #fff; color: #333; width: 90%; max-height: 80%;
            padding: 20px; border-radius: 8px; overflow-y: auto;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }
        th { background: #007dc6; color: white; }

        #toast {
            position: fixed; bottom: 20px; right: 20px; padding: 12px 20px;
            border-radius: 4px; display: none; z-index: 200; font-weight: bold;
        }
    </style>
</head>
<body>

    <div id="ui-panel">
        <h2>OPTIMIZACIÓN TECH OPS</h2>
        
        <div class="control-group">
            <label>Configuración Camión</label>
            <select id="sel-camion">
                <option value="sencillo">Sencillo (6.5m - 8T)</option>
                <option value="doble">Doble Puente (7.5m - 12T)</option>
                <option value="rampa" selected>Rampa Estándar (14.5m - 28T)</option>
            </select>
        </div>

        <div class="control-group">
            <label>Cargar Datos (Excel)</label>
            <input type="file" id="input-excel" accept=".xlsx, .xls" style="display:none">
            <button onclick="document.getElementById('input-excel').click()">📂 IMPORTAR LISTADO</button>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Pallets</div>
                <div id="lbl-pallets" class="kpi-val">0</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Peso Total</div>
                <div id="lbl-peso" class="kpi-val">0 kg</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Estabilidad (CoG)</div>
                <div id="lbl-estabilidad" class="kpi-val">-</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Cajas Actuales</div>
                <div id="lbl-cajas-actuales" class="kpi-val">0</div>
            </div>
        </div>

        <div class="control-group" style="margin-top:15px">
            <label>Meta Requerida: <span id="lbl-meta-cajas">0</span> cajas</label>
            <div id="lbl-estado-cajas" class="kpi-val" style="text-align:center; padding:5px; border-radius:4px; font-size:14px; background:#1e1e1e">ESPERANDO DATOS</div>
        </div>

        <button class="secondary" onclick="mostrarTabla()">📋 VER MANIFIESTO</button>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap:5px; margin-top:5px">
            <button onclick="descargarExcel()" style="background:#2e7d32">💾 EXCEL</button>
            <button onclick="descargarPDF()" style="background:#c62828">📄 PDF LAYOUT</button>
        </div>
    </div>

    <div id="tooltip"></div>
    <div id="toast"></div>

    <div id="modal-overlay" onclick="cerrarTabla()">
        <div id="modal-content" onclick="event.stopPropagation()">
            <h3 style="margin-top:0">Manifiesto de Carga Detallado</h3>
            <table id="tabla-manifiesto">
                <thead>
                    <tr>
                        <th>Sec</th>
                        <th>Lado</th>
                        <th>ID Pallet</th>
                        <th>Tipo</th>
                        <th>Peso (kg)</th>
                        <th>Cajas</th>
                        <th>Dist. Cabina</th>
                        <th>Posición</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <button onclick="cerrarTabla()" style="margin-top:15px; background:#333">Cerrar</button>
        </div>
    </div>

    <script>
        // ==============================================================================
        // 1. VARIABLES GLOBALES Y CONSTANTES
        // ==============================================================================
        let STOCK_SHIPPING = [];
        let ULTIMO_PLAN_CARGA = [];
        
        const FLOTA = {
            "sencillo": { L: 6.5, W: 2.45, H: 2.4, peso_max: 8000, min_cajas: 800, desc: "Sencillo 8T" },
            "doble": { L: 7.5, W: 2.45, H: 2.6, peso_max: 12000, min_cajas: 1200, desc: "Doble Puente 12T" },
            "rampa": { L: 14.5, W: 2.5, H: 2.8, peso_max: 28000, min_cajas: 2200, desc: "Rampa 28T" }
        };

        // ==============================================================================
        // 2. LÓGICA DE PROCESAMIENTO EXCEL
        // ==============================================================================
        document.getElementById('input-excel').addEventListener('change', handleFileSelect, false);

        function handleFileSelect(evt) {
            const file = evt.target.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, {type: 'array'});
                const jsonData = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]);
                procesarDatosExcel(jsonData);
            };
            reader.readAsArrayBuffer(file);
        }

        function procesarDatosExcel(jsonData) {
            STOCK_SHIPPING = jsonData.map((row, index) => ({
                id: row.id || row.pallet || `P-${index+1}`,
                peso: parseFloat(row.peso || row.weight || 500),
                cajas: parseInt(row.cajas || row.qty || 40),
                tipo: row.tipo || (index % 5 === 0 ? 'Contaminante' : 'Alimento'),
                alto: 1.4,
                dimX: 1.0, 
                dimY: 1.2
            }));
            mostrarToast("Excel cargado: " + STOCK_SHIPPING.length + " items", "#4caf50");
            ejecutarSimulacion();
        }

        // ==============================================================================
        // 3. MOTOR DE OPTIMIZACIÓN (BIN PACKING)
        // ==============================================================================
        class Optimizador {
            constructor(camionId) {
                this.camion = FLOTA[camionId];
                this.cursorX = 0.2; // Margen cabina
            }

            ejecutar() {
                let cola = [...STOCK_SHIPPING].sort((a, b) => b.peso - a.peso);
                let plan = [];
                let pesoActual = 0;
                let cajasActual = 0;
                let lado = 0; // 0: Izquierda, 1: Derecha

                for (let p of cola) {
                    if (this.cursorX + 1.1 > this.camion.L) break;
                    if (pesoActual + p.peso > this.camion.peso_max) break;

                    p.x = this.cursorX;
                    p.y = lado === 0 ? 0.1 : 1.3;
                    p.z = 0;
                    p.lado = lado === 0 ? "Izquierda" : "Derecha";
                    
                    plan.push({...p});
                    pesoActual += p.peso;
                    cajasActual += p.cajas;

                    if (lado === 1) this.cursorX += 1.1;
                    lado = lado === 0 ? 1 : 0;
                }
                return { plan, metricas: { peso: pesoActual, cajas: cajasActual, count: plan.length } };
            }
        }

        // ==============================================================================
        // 4. VISUALIZACIÓN 3D (THREE.JS)
        // ==============================================================================
        let scene, camera, renderer, controls, cargoGroup, truckGroup;

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);
            camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 100);
            camera.position.set(-10, 10, 10);
            
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            const sun = new THREE.DirectionalLight(0xffffff, 0.5);
            sun.position.set(10, 20, 10);
            scene.add(sun);

            truckGroup = new THREE.Group();
            cargoGroup = new THREE.Group();
            scene.add(truckGroup, cargoGroup);

            animate();
        }

        function dibujarCamion(camion) {
            truckGroup.clear();
            const geo = new THREE.BoxGeometry(camion.L, 0.1, camion.W);
            const mat = new THREE.MeshLambertMaterial({ color: 0x444444 });
            const floor = new THREE.Mesh(geo, mat);
            floor.position.set(camion.L/2, -0.05, camion.W/2);
            truckGroup.add(floor);

            const grid = new THREE.GridHelper(20, 20, 0x333333, 0x222222);
            grid.position.y = -0.06;
            truckGroup.add(grid);
        }

        function dibujarCarga(plan, camion) {
            cargoGroup.clear();
            let momentoX = 0, momentoY = 0, pesoTotal = 0;

            plan.forEach(p => {
                const mesh = new THREE.Mesh(
                    new THREE.BoxGeometry(p.dimX*0.95, p.alto, p.dimY*0.95),
                    new THREE.MeshLambertMaterial({ color: p.tipo === 'Alimento' ? 0xff8f00 : 0x7b1fa2 })
                );
                mesh.position.set(p.x + 0.5, p.alto/2, p.y + 0.6);
                cargoGroup.add(mesh);
                
                momentoX += (p.x + 0.5) * p.peso;
                momentoY += (p.y + 0.6) * p.peso;
                pesoTotal += p.peso;
            });

            const cogX = momentoX / pesoTotal || 0;
            const cogY = momentoY / pesoTotal || 0;
            actualizarUI({ count: plan.length, peso: pesoTotal, cajas: plan.reduce((a,b)=>a+b.cajas,0) }, cogX, cogY, camion);
        }

        function actualizarUI(m, cx, cy, cam) {
            document.getElementById('lbl-pallets').innerText = m.count;
            document.getElementById('lbl-peso').innerText = m.peso.toLocaleString() + " kg";
            document.getElementById('lbl-cajas-actuales').innerText = m.cajas;
            document.getElementById('lbl-meta-cajas').innerText = cam.min_cajas;

            const diffY = Math.abs(cy - cam.W/2);
            const est = document.getElementById('lbl-estabilidad');
            if (m.peso === 0) { est.innerText = "-"; est.className = "kpi-val"; }
            else if (diffY < 0.2) { est.innerText = "ESTABLE"; est.className = "kpi-val status-ok"; }
            else { est.innerText = "DESBALANCEADO"; est.className = "kpi-val status-err"; }

            const statusCajas = document.getElementById('lbl-estado-cajas');
            if (m.cajas >= cam.min_cajas) { statusCajas.innerText = "META CUMPLIDA"; statusCajas.className = "kpi-val status-ok"; }
            else { statusCajas.innerText = `FALTAN ${cam.min_cajas - m.cajas}`; statusCajas.className = "kpi-val status-warn"; }
        }

        function ejecutarSimulacion() {
            const camId = document.getElementById('sel-camion').value;
            const opt = new Optimizador(camId);
            const res = opt.ejecutar();
            ULTIMO_PLAN_CARGA = res.plan;
            dibujarCamion(FLOTA[camId]);
            dibujarCarga(res.plan, FLOTA[camId]);
            generarTabla();
        }

        // ==============================================================================
        // 5. EXPORTACIÓN Y UI FINAL
        // ==============================================================================
        function generarTabla() {
            const tbody = document.querySelector('#tabla-manifiesto tbody');
            tbody.innerHTML = ULTIMO_PLAN_CARGA.map((p, i) => `
                <tr>
                    <td>${i+1}</td>
                    <td>${p.lado}</td>
                    <td>${p.id}</td>
                    <td>${p.tipo}</td>
                    <td>${p.peso}</td>
                    <td>${p.cajas}</td>
                    <td>${p.x.toFixed(2)}m</td>
                    <td>${p.z === 0 ? 'Piso' : 'Apilado'}</td>
                </tr>
            `).join('');
        }

        function descargarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF('l', 'mm', 'a4');
            doc.text("Reporte de Estiba Walmart - Tech Ops", 10, 10);
            
            const tableData = ULTIMO_PLAN_CARGA.map((p, i) => [i+1, p.id, p.tipo, p.peso, p.cajas, p.lado]);
            doc.autoTable({
                head: [['Sec', 'ID', 'Tipo', 'Peso', 'Cajas', 'Lado']],
                body: tableData,
                startY: 20
            });
            doc.save("Layout_Carga.pdf");
        }

        function descargarExcel() {
            const ws = XLSX.utils.json_to_sheet(ULTIMO_PLAN_CARGA);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Carga");
            XLSX.writeFile(wb, "Manifiesto_Carga.xlsx");
        }

        function mostrarTabla() { document.getElementById('modal-overlay').style.display = 'flex'; }
        function cerrarTabla() { document.getElementById('modal-overlay').style.display = 'none'; }
        function mostrarToast(m, c) { 
            const t = document.getElementById('toast'); 
            t.innerText = m; t.style.background = c; t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 3000);
        }
        function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }

        window.onload = init3D;
        document.getElementById('sel-camion').addEventListener('change', ejecutarSimulacion);
    </script>
</body>
</html>
