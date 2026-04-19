import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Walmart Tech Ops - Gemelo Digital 85%")

# Código unificado con lógica de apilamiento denso
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
        .kpi-card { background: #1e1e1e; padding: 12px; margin-bottom: 8px; border-radius: 6px; display: flex; justify-content: space-between; border-left: 4px solid #007dc6; }
        .kpi-val { font-weight: bold; color: #ffc220; font-size: 1.1em; }
        .status-ok { color: #4caf50; }
        .status-warn { color: #ff9800; }
        .status-err { color: #f44336; }
        select, button { width: 100%; padding: 12px; margin-top: 10px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; font-size: 14px; }
        button { background: #007dc6; color: white; text-transform: uppercase; }
        button:hover { background: #006199; }
        #tooltip { position: absolute; background: rgba(0,0,0,0.95); padding: 12px; border: 1px solid #ffc220; display: none; pointer-events: none; z-index: 100; border-radius: 5px; font-size: 13px; line-height: 1.4; }
        #labels-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        .label-3d { position: absolute; background: #007dc6; color: white; padding: 4px 10px; font-size: 12px; font-weight: bold; border-radius: 4px; transform: translate(-50%, -50%); opacity: 0.9; }
    </style>
</head>
<body>

    <div id="ui-panel">
        <h2 style="margin:0 0 10px 0; color:#007dc6;">Walmart Digital Twin</h2>
        <p style="font-size: 12px; color: #888; margin-bottom: 20px;">Optimización de Estiba y Layout 3D</p>
        
        <label style="font-size: 11px; color: #aaa; text-transform: uppercase;">Selección de Equipo</label>
        <select id="sel-camion" onchange="ejecutarSimulacion()"></select>

        <div style="margin-top:20px;">
            <div class="kpi-card"><span>Ocupación Vol:</span> <span id="lbl-vol" class="kpi-val">0%</span></div>
            <div class="kpi-card"><span>Cant. Pallets:</span> <span id="lbl-pallets" class="kpi-val">0</span></div>
            <div class="kpi-card"><span>Peso Total:</span> <span id="lbl-peso" class="kpi-val">0 kg</span></div>
            <div class="kpi-card"><span>Estabilidad:</span> <span id="lbl-estabilidad" class="kpi-val">-</span></div>
            <div class="kpi-card"><span>Meta Cajas:</span> <span id="lbl-estado-cajas" class="kpi-val">-</span></div>
        </div>

        <button onclick="ejecutarSimulacion()" style="margin-top:20px;">Recalcular Plan de Carga</button>
        <button onclick="descargarExcel()" style="background:#2e7d32;">Descargar Excel</button>
        <button onclick="descargarPDF()" style="background:#c62828;">Descargar PDF</button>
    </div>

    <div id="tooltip"></div>
    <div id="labels-container"></div>

    <script>
        // --- DATA DE VEHÍCULOS ---
        const FLOTA = {
            "Sencillo": { L: 7.2, W: 2.4, H: 2.5, max_peso: 9000, min_cajas: 350, desc: "Sencillo (Capacidad 8.5 - 9T)" },
            "Tracto":   { L: 14.5, W: 2.5, H: 2.8, max_peso: 28000, min_cajas: 950, desc: "Tracto (Capacidad 28T)" }
        };

        // --- MOTOR DE OPTIMIZACIÓN ---
        class OptimizadorCarga {
            constructor(camionId) {
                this.camion = FLOTA[camionId];
                this.carga = [];
                this.metricas = { peso: 0, cajas: 0, palletsCount: 0 };
                this.volCamion = this.camion.L * this.camion.W * this.camion.H;
            }

            esCompatible(base, nuevo) {
                // QA/QC: No contaminantes sobre alimentos
                if (base.tipo === 'Alimento' && nuevo.tipo === 'Contaminante') return false;
                // QA/QC: Altura máxima
                if ((base.z + base.alto + nuevo.alto) > this.camion.H) return false;
                // QA/QC: Estabilidad de peso (el de arriba no debe exceder al de abajo)
                if (nuevo.peso > (base.peso * 1.05)) return false;
                return true;
            }

            ejecutar() {
                let id = 1;
                let x = 0.2; // Inicio carga
                let palletsEnPiso = [];

                // 1. LLENADO DE BASE (PISO)
                while (x + 1.2 <= this.camion.L - 0.2) {
                    let y = 0.1;
                    while (y + 1.0 <= this.camion.W - 0.1) {
                        let p = this.generarPallet(id++);
                        p.x = x; p.y = y; p.z = 0;
                        p.lado = y < (this.camion.W / 2) ? 'IZQ' : 'DER';
                        this.carga.push(p);
                        palletsEnPiso.push(p);
                        this.sumar(p);
                        y += 1.1; 
                    }
                    x += 1.25;
                }

                // 2. LLENADO POR APILAMIENTO (PARA LLEGAR AL 80-85%)
                for (let pBase of palletsEnPiso) {
                    let ocupacionActual = (this.metricas.palletsCount * (1.2 * 1.0 * 1.5)) / this.volCamion;
                    if (ocupacionActual >= 0.83) break; // Objetivo 83% aprox

                    let pSup = this.generarPallet(id++);
                    if (this.esCompatible(pBase, pSup) && (this.metricas.peso + pSup.peso <= this.camion.max_peso)) {
                        pSup.x = pBase.x; pSup.y = pBase.y; pSup.z = pBase.alto;
                        pSup.lado = pBase.lado;
                        pSup.apiladoSobre = pBase.id;
                        this.carga.push(pSup);
                        this.sumar(pSup);
                    }
                }
                return { carga: this.carga, metricas: this.metricas };
            }

            generarPallet(id) {
                const tipo = Math.random() > 0.4 ? 'Alimento' : 'Contaminante';
                const alto = 1.45; 
                return {
                    id: "PLT-" + String(id).padStart(3, '0'),
                    tipo: tipo,
                    peso: 400 + Math.floor(Math.random() * 600),
                    cajas: 35 + Math.floor(Math.random() * 25),
                    dimX: 1.2, dimY: 1.0, alto: alto
                };
            }

            sumar(p) {
                this.metricas.peso += p.peso;
                this.metricas.cajas += p.cajas;
                this.metricas.palletsCount++;
            }
        }

        // --- VISUALIZACIÓN 3D ---
        let scene, camera, renderer, controls, truckGroup, cargoGroup, palletMeshes = [];
        let PLAN_ACTUAL = null;

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);
            camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(22, 14, 22);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            scene.add(new THREE.AmbientLight(0xffffff, 0.4));
            const sun = new THREE.DirectionalLight(0xffffff, 0.7);
            sun.position.set(10, 20, 10);
            scene.add(sun);

            truckGroup = new THREE.Group();
            cargoGroup = new THREE.Group();
            scene.add(truckGroup, cargoGroup);

            window.addEventListener('mousemove', onHover);
            animate();
        }

        function ejecutarSimulacion() {
            const id = document.getElementById('sel-camion').value;
            const cam = FLOTA[id];
            const opt = new OptimizadorCarga(id);
            const res = opt.ejecutar();
            PLAN_ACTUAL = res;

            // Dibujar Camión
            while(truckGroup.children.length > 0) truckGroup.remove(truckGroup.children[0]);
            const floor = new THREE.Mesh(new THREE.BoxGeometry(cam.L, 0.1, cam.W), new THREE.MeshLambertMaterial({color: 0x222222}));
            floor.position.set(cam.L/2, -0.05, cam.W/2);
            truckGroup.add(floor);

            const frame = new THREE.LineSegments(
                new THREE.EdgesGeometry(new THREE.BoxGeometry(cam.L, cam.H, cam.W)),
                new THREE.LineBasicMaterial({color: 0xffffff, transparent: true, opacity: 0.1})
            );
            frame.position.set(cam.L/2, cam.H/2, cam.W/2);
            truckGroup.add(frame);

            // Dibujar Pallets
            while(cargoGroup.children.length > 0) cargoGroup.remove(cargoGroup.children[0]);
            palletMeshes = [];
            let mX = 0, mY = 0;

            res.carga.forEach(p => {
                const color = p.tipo === 'Alimento' ? 0xff8f00 : 0x7b1fa2;
                const mesh = new THREE.Mesh(
                    new THREE.BoxGeometry(p.dimX * 0.96, p.alto * 0.98, p.dimY * 0.96),
                    new THREE.MeshLambertMaterial({ color: color })
                );
                mesh.position.set(p.x + p.dimX/2, p.z + p.alto/2, p.y + p.dimY/2);
                mesh.userData = p;
                
                const edges = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), new THREE.LineBasicMaterial({color: 0x000000, opacity: 0.3, transparent: true}));
                mesh.add(edges);
                cargoGroup.add(mesh);
                palletMeshes.push(mesh);

                mX += (p.x + p.dimX/2) * p.peso;
                mY += (p.y + p.dimY/2) * p.peso;
            });

            actualizarUI(res.metricas, mX/res.metricas.peso, mY/res.metricas.peso, cam);
            crearEtiquetas(cam);
        }

        function actualizarUI(m, cx, cy, cam) {
            const vol = ((m.palletsCount * (1.2 * 1.0 * 1.45)) / (cam.L * cam.W * cam.H) * 100).toFixed(1);
            const lblV = document.getElementById('lbl-vol');
            lblV.innerText = vol + "%";
            lblV.className = (vol >= 80) ? "kpi-val status-ok" : "kpi-val status-warn";

            document.getElementById('lbl-pallets').innerText = m.palletsCount;
            document.getElementById('lbl-peso').innerText = m.peso.toLocaleString() + " kg";
            
            const est = Math.abs(cy - (cam.W/2)) < (cam.W * 0.1) ? "ESTABLE" : "DESBALANCEADO";
            document.getElementById('lbl-estabilidad').innerText = est;
            document.getElementById('lbl-estabilidad').className = est === "ESTABLE" ? "kpi-val status-ok" : "kpi-val status-err";

            const meta = m.cajas >= cam.min_cajas ? "CUMPLIDA" : "PENDIENTE (" + (cam.min_cajas - m.cajas) + ")";
            document.getElementById('lbl-estado-cajas').innerText = meta;
            document.getElementById('lbl-estado-cajas').className = m.cajas >= cam.min_cajas ? "kpi-val status-ok" : "kpi-val status-warn";
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
                t.innerHTML = `<b>${d.id}</b><br>Tipo: ${d.tipo}<br>Peso: ${d.peso}kg<br>Posición: ${d.z === 0 ? 'Piso' : 'Apilado'}`;
            } else t.style.display = 'none';
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderLabels();
            renderer.render(scene, camera);
        }

        let labels = [];
        function crearEtiquetas(cam) {
            const cont = document.getElementById('labels-container');
            cont.innerHTML = ''; labels = [];
            const l = (txt, pos) => {
                const d = document.createElement('div'); d.className = 'label-3d'; d.innerText = txt;
                cont.appendChild(d); labels.push({e: d, p: pos});
            };
            l("FRONT / CABINA", new THREE.Vector3(0, cam.H + 0.5, cam.W/2));
            l("REAR / PUERTA", new THREE.Vector3(cam.L, cam.H + 0.5, cam.W/2));
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
            const data = PLAN_ACTUAL.carga.map(p => ({
                ID: p.id, Tipo: p.tipo, Peso: p.peso, Nivel: p.z === 0 ? "Piso" : "Nivel 2", Lado: p.lado
            }));
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Manifiesto");
            XLSX.writeFile(wb, "Plan_Carga_Walmart.xlsx");
        }

        async function descargarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.text("Reporte de Estiba Walmart Tech Ops", 10, 10);
            const rows = PLAN_ACTUAL.carga.map(p => [p.id, p.tipo, p.peso + "kg", p.lado, p.z === 0 ? "Piso" : "Apilado"]);
            doc.autoTable({ head: [['ID', 'Tipo', 'Peso', 'Lado', 'Nivel']], body: rows, startY: 20 });
            doc.save("Reporte_Estiba.pdf");
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
