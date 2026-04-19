import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Walmart Tech Ops - Gemelo Digital")

# Código HTML/JavaScript completo
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
        body { margin: 0; font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; overflow: hidden; }
        #ui-panel { position: absolute; top: 10px; left: 10px; z-index: 10; background: rgba(0,0,0,0.85); padding: 15px; border-radius: 8px; width: 320px; border: 1px solid #444; }
        .kpi-card { background: #2d2d2d; padding: 10px; margin-bottom: 6px; border-radius: 4px; display: flex; justify-content: space-between; font-size: 13px; }
        .kpi-val { font-weight: bold; color: #ffc220; }
        .status-ok { color: #4caf50; font-weight: bold; }
        .status-warn { color: #ff9800; }
        .status-err { color: #f44336; }
        select, button { width: 100%; padding: 10px; margin-top: 8px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }
        button { background: #007dc6; color: white; transition: 0.3s; }
        button:hover { background: #006199; }
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); padding: 10px; border: 1px solid #ffc220; display: none; pointer-events: none; font-size: 12px; z-index: 100; border-radius: 4px; }
        #labels-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        .label-3d { position: absolute; background: rgba(0, 125, 198, 0.7); color: white; padding: 2px 8px; font-size: 11px; border-radius: 10px; transform: translate(-50%, -50%); }
    </style>
</head>
<body>

    <div id="ui-panel">
        <h3 style="margin:0 0 15px 0; color:#007dc6; border-bottom: 1px solid #444; padding-bottom: 5px;">Digital Twin: Estiba Tech Ops</h3>
        
        <label style="font-size: 12px; color: #aaa;">CONFIGURACIÓN DE FLOTA</label>
        <select id="sel-camion" onchange="ejecutarSimulacion()"></select>

        <div style="margin-top:15px;">
            <div class="kpi-card"><span>Ocupación Volumétrica:</span> <span id="lbl-vol" class="kpi-val">0%</span></div>
            <div class="kpi-card"><span>Total Pallets:</span> <span id="lbl-pallets" class="kpi-val">0</span></div>
            <div class="kpi-card"><span>Peso Bruto:</span> <span id="lbl-peso" class="kpi-val">0 kg</span></div>
            <div class="kpi-card"><span>Estabilidad Lateral:</span> <span id="lbl-estabilidad" class="kpi-val">-</span></div>
            <div class="kpi-card"><span>Cumplimiento Meta:</span> <span id="lbl-estado-cajas" class="kpi-val">-</span></div>
        </div>

        <button onclick="ejecutarSimulacion()" style="margin-top:15px;">REGENERAR PLAN DE CARGA</button>
        <button onclick="descargarExcel()" style="background:#2e7d32;">EXPORTAR MANIFIESTO (.XLSX)</button>
        <button onclick="descargarPDF()" style="background:#c62828;">EXPORTAR LAYOUT (.PDF)</button>
    </div>

    <div id="tooltip"></div>
    <div id="labels-container"></div>

    <script>
        const FLOTA = {
            "Sencillo": { L: 7.2, W: 2.4, H: 2.5, max_peso: 8500, min_cajas: 350, desc: "Camión Sencillo (8.5T)" },
            "Tracto":   { L: 14.2, W: 2.5, H: 2.7, max_peso: 28000, min_cajas: 900, desc: "Tracto Remolque (28T)" }
        };

        class OptimizadorCarga {
            constructor(camionId) {
                this.camion = FLOTA[camionId];
                this.carga = [];
                this.metricas = { peso: 0, cajas: 0, palletsCount: 0 };
                this.volTotal = this.camion.L * this.camion.W * this.camion.H;
            }

            esCompatible(base, nuevo) {
                if (base.tipo === 'Alimento' && nuevo.tipo === 'Contaminante') return false;
                if ((base.z + base.alto + nuevo.alto) > this.camion.H) return false;
                if (nuevo.peso > (base.peso * 1.1)) return false; // El de arriba no puede ser significativamente más pesado
                return true;
            }

            ejecutar() {
                let idCounter = 1;
                let x = 0.15; // Holgura cabina
                let palletsBase = [];

                // FASE 1: LLENAR PISO (Z=0)
                while (x + 1.2 <= this.camion.L - 0.2) {
                    let y = 0.05;
                    while (y + 1.0 <= this.camion.W - 0.05) {
                        let p = this.generarPallet(idCounter++);
                        p.x = x; p.y = y; p.z = 0;
                        p.lado = y < (this.camion.W / 2) ? 'Izquierda' : 'Derecha';
                        this.carga.push(p);
                        palletsBase.push(p);
                        this.sumarMetricas(p);
                        y += 1.1; // Espacio entre filas
                    }
                    x += 1.25; // Espacio entre columnas
                }

                // FASE 2: APILAMIENTO RECURSIVO PARA LLEGAR AL 80-85%
                for (let base of palletsBase) {
                    let ocupacionActual = (this.metricas.palletsCount * 1.68) / this.volTotal;
                    if (ocupacionActual >= 0.83) break; // Detenerse en el rango óptimo

                    let pSup = this.generarPallet(idCounter++);
                    if (this.esCompatible(base, pSup) && (this.metricas.peso + pSup.peso < this.camion.max_peso)) {
                        pSup.x = base.x; pSup.y = base.y; pSup.z = base.alto;
                        pSup.lado = base.lado;
                        pSup.apiladoSobre = base.id;
                        this.carga.push(pSup);
                        this.sumarMetricas(pSup);
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

            sumarMetricas(p) {
                this.metricas.peso += p.peso;
                this.metricas.cajas += p.cajas;
                this.metricas.palletsCount++;
            }
        }

        // --- RENDERIZADO 3D ---
        let scene, camera, renderer, controls, truckGroup, cargoGroup, palletMeshes = [];
        let ULTIMO_PLAN = null;

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(18, 12, 18);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            const light = new THREE.DirectionalLight(0xffffff, 0.8);
            light.position.set(5, 15, 5);
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
            const opt = new OptimizadorCarga(id);
            const res = opt.ejecutar();
            ULTIMO_PLAN = res;

            // Dibujar Camion
            while(truckGroup.children.length > 0) truckGroup.remove(truckGroup.children[0]);
            const floor = new THREE.Mesh(new THREE.BoxGeometry(cam.L, 0.1, cam.W), new THREE.MeshLambertMaterial({color: 0x333333}));
            floor.position.set(cam.L/2, -0.05, cam.W/2);
            truckGroup.add(floor);

            const wire = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(cam.L, cam.H, cam.W)), new THREE.LineBasicMaterial({color: 0xffffff, opacity: 0.1, transparent: true}));
            wire.position.set(cam.L/2, cam.H/2, cam.W/2);
            truckGroup.add(wire);

            // Dibujar Carga
            while(cargoGroup.children.length > 0) cargoGroup.remove(cargoGroup.children[0]);
            palletMeshes = [];
            let mX = 0, mY = 0;

            res.carga.forEach(p => {
                const mat = new THREE.MeshLambertMaterial({ color: p.tipo === 'Alimento' ? 0xff8f00 : 0x7b1fa2 });
                const mesh = new THREE.Mesh(new THREE.BoxGeometry(p.dimX*0.96, p.alto*0.98, p.dimY*0.96), mat);
                mesh.position.set(p.x + p.dimX/2, p.z + p.alto/2, p.y + p.dimY/2);
                mesh.userData = p;
                
                const edges = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), new THREE.LineBasicMaterial({color: 0x000000, opacity: 0.4, transparent: true}));
                mesh.add(edges);
                cargoGroup.add(mesh);
                palletMeshes.push(mesh);

                mX += (p.x + p.dimX/2) * p.peso;
                mY += (p.y + p.dimY/2) * p.peso;
            });

            actualizarInterfaz(res.metricas, mX/res.metricas.peso, mY/res.metricas.peso, cam);
            crearLabels(cam);
        }

        function actualizarInterfaz(m, cx, cy, cam) {
            const volPerc = ((m.palletsCount * (1.2*1.0*1.45)) / (cam.L * cam.W * cam.H) * 100).toFixed(1);
            const lblV = document.getElementById('lbl-vol');
            lblV.innerText = volPerc + "%";
            lblV.className = (volPerc >= 80) ? "kpi-val status-ok" : "kpi-val status-warn";

            document.getElementById('lbl-pallets').innerText = m.palletsCount;
            document.getElementById('lbl-peso').innerText = m.peso.toLocaleString() + " kg";
            
            const est = Math.abs(cy - (cam.W/2)) < (cam.W * 0.1) ? "ESTABLE" : "DESBALANCEADO";
            document.getElementById('lbl-estabilidad').innerText = est;
            document.getElementById('lbl-estabilidad').className = est === "ESTABLE" ? "kpi-val status-ok" : "kpi-val status-err";

            const meta = m.cajas >= cam.min_cajas ? "CUMPLIDA" : "FALTAN " + (cam.min_cajas - m.cajas);
            document.getElementById('lbl-estado-cajas').innerText = meta;
            document.getElementById('lbl-estado-cajas').className = meta === "CUMPLIDA" ? "kpi-val status-ok" : "kpi-val status-warn";
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
                t.style.left = e.clientX + 10 + 'px'; t.style.top = e.clientY + 10 + 'px';
                t.innerHTML = `<strong>${d.id}</strong><br>Tipo: ${d.tipo}<br>Peso: ${d.peso}kg<br>Nivel: ${d.z === 0 ? 'Piso' : 'Apilado'}`;
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
            l("CABINA / FRONT", new THREE.Vector3(0, 2.8, cam.W/2));
            l("PUERTAS / REAR", new THREE.Vector3(cam.L, 2.8, cam.W/2));
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
            const data = ULTIMO_PLAN.carga.map(p => ({
                ID: p.id, Tipo: p.tipo, Peso: p.peso, Nivel: p.z === 0 ? "Piso" : "Nivel 2", Lado: p.lado
            }));
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Plan de Carga");
            XLSX.writeFile(wb, "Manifiesto_Walmart_Estiba.xlsx");
        }

        async function descargarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.setFontSize(16); doc.text("Layout de Estiba - Tech Ops", 10, 15);
            const rows = ULTIMO_PLAN.carga.map(p => [p.id, p.tipo, p.peso + "kg", p.lado, p.z === 0 ? "Piso" : "Apilado"]);
            doc.autoTable({ head: [['ID', 'Tipo', 'Peso', 'Lado', 'Nivel']], body: rows, startY: 25 });
            doc.save("Layout_Estiba_Walmart.pdf");
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
