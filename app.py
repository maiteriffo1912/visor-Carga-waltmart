import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Walmart Tech Ops - Optimización de Suelo")

# Código HTML/JavaScript unificado para el Gemelo Digital
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.5/xlsx.full.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.23/jspdf.plugin.autotable.min.js"></script>
    <style>
        body { margin: 0; font-family: 'Segoe UI', sans-serif; background: #121212; color: white; overflow: hidden; }
        #ui-panel { position: absolute; top: 15px; left: 15px; z-index: 10; background: rgba(0,0,0,0.9); padding: 20px; border-radius: 10px; width: 340px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .kpi-card { background: #1e1e1e; padding: 12px; margin-bottom: 8px; border-radius: 6px; display: flex; justify-content: space-between; border-left: 4px solid #ffc220; }
        .kpi-val { font-weight: bold; color: #ffc220; font-size: 1.1em; }
        .status-ok { color: #4caf50; }
        .status-warn { color: #ff9800; }
        select, button { width: 100%; padding: 12px; margin-top: 10px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; }
        button { background: #007dc6; color: white; text-transform: uppercase; transition: 0.3s; }
        button:hover { background: #006199; }
        #tooltip { position: absolute; background: rgba(0,0,0,0.95); padding: 12px; border: 1px solid #ffc220; display: none; pointer-events: none; z-index: 100; border-radius: 5px; font-size: 13px; }
        #labels-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        .label-3d { position: absolute; background: #007dc6; color: white; padding: 4px 10px; font-size: 12px; font-weight: bold; border-radius: 4px; transform: translate(-50%, -50%); opacity: 0.8; }
    </style>
</head>
<body>

    <div id="ui-panel">
        <h2 style="margin:0 0 5px 0; color:#007dc6;">Layout de Suelo</h2>
        <p style="font-size: 11px; color: #888; margin-bottom: 15px;">Optimización basada en Superficie de Carga</p>
        
        <label style="font-size: 10px; color: #aaa;">SELECCIONAR VEHÍCULO</label>
        <select id="sel-camion" onchange="ejecutarSimulacion()"></select>

        <div style="margin-top:20px;">
            <div class="kpi-card"><span>Uso de Suelo:</span> <span id="lbl-suelo" class="kpi-val">0%</span></div>
            <div class="kpi-card"><span>Posiciones Base:</span> <span id="lbl-pallets" class="kpi-val">0</span></div>
            <div class="kpi-card"><span>Peso Estimado:</span> <span id="lbl-peso" class="kpi-val">0 kg</span></div>
            <div class="kpi-card"><span>Balance Lateral:</span> <span id="lbl-estabilidad" class="kpi-val">-</span></div>
        </div>

        <button onclick="ejecutarSimulacion()" style="margin-top:15px;">Recalcular Plan de Carga</button>
        <button onclick="descargarExcel()" style="background:#2e7d32;">Exportar Excel</button>
        <button onclick="descargarPDF()" style="background:#c62828;">Exportar PDF</button>
    </div>

    <div id="tooltip"></div>
    <div id="labels-container"></div>

    <script>
        const FLOTA = {
            "Sencillo": { L: 7.4, W: 2.4, H: 2.5, max_peso: 9000, desc: "Camión Sencillo (8.5 - 9T)" },
            "Tracto":   { L: 14.5, W: 2.5, H: 2.8, max_peso: 28000, desc: "Tractocamión (28T)" }
        };

        class OptimizadorSuelo {
            constructor(camionId) {
                this.camion = FLOTA[camionId];
                this.carga = [];
                this.metricas = { peso: 0, posiciones: 0, areaOcupada: 0 };
                this.areaSueloTotal = this.camion.L * this.camion.W;
            }

            ejecutar() {
                let id = 1;
                let x = 0.1; 
                const palletArea = 1.2 * 1.0;

                // Iteración para cubrir la superficie (objetivo 80-85%)
                while (x + 1.2 <= this.camion.L - 0.1) {
                    let y = 0.1;
                    while (y + 1.0 <= this.camion.W - 0.1) {
                        // Verificamos si aún no excedemos el 85% del suelo
                        if ((this.metricas.areaOcupada + palletArea) / this.areaSueloTotal <= 0.85) {
                            let p = this.crearPallet(id++, false);
                            p.x = x; p.y = y; p.z = 0;
                            this.carga.push(p);
                            this.sumar(p, true);

                            // Apilamiento visual (no cuenta para el % de suelo, pero optimiza peso/espacio)
                            if (Math.random() > 0.5 && (this.metricas.peso < this.camion.max_peso)) {
                                let pSup = this.crearPallet(id++, true);
                                pSup.x = x; pSup.y = y; pSup.z = p.alto;
                                this.carga.push(pSup);
                                this.sumar(pSup, false);
                            }
                        }
                        y += 1.05; 
                    }
                    x += 1.22;
                }
                return { carga: this.carga, metricas: this.metricas };
            }

            crearPallet(id, esApilado) {
                return {
                    id: "PLT-" + String(id).padStart(3, '0'),
                    tipo: Math.random() > 0.6 ? 'Alimento' : 'Contaminante',
                    peso: 350 + Math.floor(Math.random() * 500),
                    dimX: 1.2, dimY: 1.0, alto: 1.4,
                    apilado: esApilado
                };
            }

            sumar(p, esBase) {
                this.metricas.peso += p.peso;
                if (esBase) {
                    this.metricas.posiciones++;
                    this.metricas.areaOcupada += (p.dimX * p.dimY);
                }
            }
        }

        let scene, camera, renderer, controls, truckGroup, cargoGroup, palletMeshes = [];
        let RESULTADO_PLAN = null;

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0d0d0d);
            camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(22, 16, 22);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            const light = new THREE.DirectionalLight(0xffffff, 0.7);
            light.position.set(10, 20, 10);
            scene.add(light);

            truckGroup = new THREE.Group();
            cargoGroup = new THREE.Group();
            scene.add(truckGroup, cargoGroup);

            window.addEventListener('mousemove', onHover);
            animate();
        }

        function ejecutarSimulacion() {
            const id = document.getElementById('sel-camion').value;
            const cam = FLOTA[id];
            const opt = new OptimizadorSuelo(id);
            const res = opt.ejecutar();
            RESULTADO_PLAN = res;

            // Dibujar Estructura
            while(truckGroup.children.length > 0) truckGroup.remove(truckGroup.children[0]);
            const floor = new THREE.Mesh(new THREE.BoxGeometry(cam.L, 0.1, cam.W), new THREE.MeshLambertMaterial({color: 0x222222}));
            floor.position.set(cam.L/2, -0.05, cam.W/2);
            truckGroup.add(floor);

            const wire = new THREE.LineSegments(
                new THREE.EdgesGeometry(new THREE.BoxGeometry(cam.L, cam.H, cam.W)),
                new THREE.LineBasicMaterial({color: 0xffffff, opacity: 0.1, transparent: true})
            );
            wire.position.set(cam.L/2, cam.H/2, cam.W/2);
            truckGroup.add(wire);

            // Dibujar Pallets
            while(cargoGroup.children.length > 0) cargoGroup.remove(cargoGroup.children[0]);
            palletMeshes = [];
            let mY = 0;

            res.carga.forEach(p => {
                const color = p.tipo === 'Alimento' ? 0xff8f00 : 0x7b1fa2;
                const mesh = new THREE.Mesh(new THREE.BoxGeometry(p.dimX*0.95, p.alto*0.98, p.dimY*0.95), new THREE.MeshLambertMaterial({color}));
                mesh.position.set(p.x + p.dimX/2, p.z + p.alto/2, p.y + p.dimY/2);
                mesh.userData = p;
                
                const edg = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), new THREE.LineBasicMaterial({color: 0x000000, opacity: 0.3, transparent: true}));
                mesh.add(edg);
                cargoGroup.add(mesh);
                palletMeshes.push(mesh);
                mY += (p.y + p.dimY/2) * p.peso;
            });

            actualizarInterfaz(res.metricas, mY/res.metricas.peso, cam);
            crearLabels(cam);
        }

        function actualizarInterfaz(m, cy, cam) {
            const percSuelo = ((m.areaOcupada / (cam.L * cam.W)) * 100).toFixed(1);
            const lblS = document.getElementById('lbl-suelo');
            lblS.innerText = percSuelo + "%";
            lblS.className = (percSuelo >= 80) ? "kpi-val status-ok" : "kpi-val status-warn";

            document.getElementById('lbl-pallets').innerText = m.posiciones;
            document.getElementById('lbl-peso').innerText = m.peso.toLocaleString() + " kg";
            
            const est = Math.abs(cy - (cam.W/2)) < (cam.W * 0.1) ? "EQUILIBRADO" : "DESBALANCEADO";
            document.getElementById('lbl-estabilidad').innerText = est;
            document.getElementById('lbl-estabilidad').className = est === "EQUILIBRADO" ? "kpi-val status-ok" : "kpi-val status-warn";
        }

        function onHover(e) {
            const ray = new THREE.Raycaster();
            const mouse = new THREE.Vector2((e.clientX/window.innerWidth)*2-1, -(e.clientY/window.innerHeight)*2+1);
            ray.setFromCamera(mouse, camera);
            const inter = ray.intersectObjects(palletMeshes);
            const t = document.getElementById('tooltip');
            if(inter.length > 0) {
                const d = inter[0].object.userData;
                t.style.display = 'block';
                t.style.left = e.clientX + 15 + 'px'; t.style.top = e.clientY + 15 + 'px';
                t.innerHTML = `<b>${d.id}</b><br>Tipo: ${d.tipo}<br>Peso: ${d.peso}kg<br>Nivel: ${d.apilado ? 'Superior' : 'Suelo'}`;
            } else t.style.display = 'none';
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderLabels();
            renderer.render(scene, camera);
        }

        let labels = [];
        function crearLabels(cam) {
            const cont = document.getElementById('labels-container');
            cont.innerHTML = ''; labels = [];
            const l = (txt, pos) => {
                const d = document.createElement('div'); d.className = 'label-3d'; d.innerText = txt;
                cont.appendChild(d); labels.push({e: d, p: pos});
            };
            l("FRONT / CABINA", new THREE.Vector3(0, cam.H, cam.W/2));
            l("REAR / PUERTA", new THREE.Vector3(cam.L, cam.H, cam.W/2));
        }

        function renderLabels() {
            labels.forEach(l => {
                const v = l.p.clone().project(camera);
                if(v.z < 1) {
                    l.e.style.display = 'block';
                    l.e.style.left = (v.x * .5 + .5) * window.innerWidth + 'px';
                    l.e.style.top = (-(v.y * .5) + .5) * window.innerHeight + 'px';
                } else l.e.style.display = 'none';
            });
        }

        function descargarExcel() {
            const data = RESULTADO_PLAN.carga.map(p => ({
                ID: p.id, Tipo: p.tipo, Peso_kg: p.peso, Posicion: p.apilado ? "Nivel 2" : "Suelo"
            }));
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Estiba");
            XLSX.writeFile(wb, "Manifiesto_Suelo.xlsx");
        }

        async function descargarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.text("Reporte de Layout de Suelo", 10, 10);
            const rows = RESULTADO_PLAN.carga.map(p => [p.id, p.tipo, p.peso + "kg", p.apilado ? "Nivel 2" : "Suelo"]);
            doc.autoTable({ head: [['ID', 'Tipo', 'Peso', 'Ubicación']], body: rows, startY: 20 });
            doc.save("Reporte_Layout.pdf");
        }

        window.onload = () => {
            const s = document.getElementById('sel-camion');
            for(let k in FLOTA) {
                let o = document.createElement('option'); o.value = k; o.innerText = FLOTA[k].desc;
                s.appendChild(o);
            }
            init3D(); ejecutarSimulacion();
        };
    </script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=False)
