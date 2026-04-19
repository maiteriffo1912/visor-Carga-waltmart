import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Gemelo Digital - Optimización de Estiba")

# Estilos CSS para la interfaz de usuario dentro del componente
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Visualizador de Estiba 3D</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.5/xlsx.full.min.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.23/jspdf.plugin.autotable.min.js"></script>
    <style>
        body { margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: white; overflow: hidden; }
        #ui-panel { position: absolute; top: 10px; left: 10px; z-index: 10; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 8px; width: 300px; border: 1px solid #444; }
        .kpi-card { background: #2d2d2d; padding: 10px; margin-bottom: 8px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .kpi-val { font-weight: bold; color: #ffc220; }
        .status-ok { color: #4caf50; }
        .status-err { color: #f44336; }
        .status-warn { color: #ff9800; }
        select, button { width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: none; cursor: pointer; }
        button { background: #007dc6; color: white; font-weight: bold; margin-bottom: 5px; }
        button:hover { background: #006199; }
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); padding: 10px; border: 1px solid #ffc220; display: none; pointer-events: none; font-size: 12px; z-index: 100; }
        #labels-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        .label-3d { position: absolute; background: rgba(255,255,255,0.1); color: white; padding: 2px 5px; font-size: 10px; border: 0.5px solid rgba(255,255,255,0.3); border-radius: 3px; }
    </style>
</head>
<body>

    <div id="ui-panel">
        <h3 style="margin-top:0; color:#007dc6;">Layout de Carga Walmart</h3>
        
        <label>Seleccionar Vehículo:</label>
        <select id="sel-camion" onchange="ejecutarSimulacion()"></select>

        <div style="margin-top:15px;">
            <div class="kpi-card"><span>Pallets Estibados:</span> <span id="lbl-pallets" class="kpi-val">0</span></div>
            <div class="kpi-card"><span>Ocupación Vol:</span> <span id="lbl-vol" class="kpi-val">0%</span></div>
            <div class="kpi-card"><span>Peso Total:</span> <span id="lbl-peso" class="kpi-val">0 kg</span></div>
            <div class="kpi-card"><span>Estabilidad:</span> <span id="lbl-estabilidad" class="kpi-val">-</span></div>
            <div class="kpi-card"><span>Meta Cajas:</span> <span id="lbl-estado-cajas" class="kpi-val">-</span></div>
        </div>

        <button onclick="ejecutarSimulacion()">RECALCULAR CARGA</button>
        <button onclick="descargarExcel()" style="background:#2e7d32;">DESCARGAR MANIFIESTO (.XLSX)</button>
        <button onclick="descargarPDF()" style="background:#c62828;">DESCARGAR LAYOUT (.PDF)</button>
    </div>

    <div id="tooltip"></div>
    <div id="labels-container"></div>

    <script>
        // --- CONFIGURACIÓN DE FLOTA ---
        const FLOTA = {
            "Sencillo": { L: 7.5, W: 2.4, H: 2.6, max_peso: 8000, min_cajas: 350, desc: "Camión Sencillo 8T" },
            "Tracto":   { L: 14.5, W: 2.5, H: 2.7, max_peso: 28000, min_cajas: 950, desc: "Tractocamión 28T" }
        };

        // --- CLASE OPTIMIZADORA (HEURÍSTICA DE CARGA) ---
        class OptimizadorCarga {
            constructor(camionId) {
                this.camion = FLOTA[camionId];
                this.carga = [];
                this.metricas = { peso: 0, cajas: 0, palletsCount: 0 };
                this.volumenActual = 0;
                this.volTotalCamion = this.camion.L * this.camion.W * this.camion.H;
                this.targetVol = 0.82; // Objetivo central 82%
            }

            esCompatible(base, nuevo) {
                // Regla 1: No contaminantes sobre alimentos
                if (base.tipo === 'Alimento' && nuevo.tipo === 'Contaminante') return false;
                // Regla 2: Límite de altura
                if ((base.z + base.alto + nuevo.alto) > this.camion.H) return false;
                // Regla 3: El de abajo debe pesar igual o más
                if (nuevo.peso > base.peso) return false;
                return true;
            }

            ejecutar() {
                let id = 1;
                let x = 0.15; // Empezar después de holgura de cabina
                let y = 0;
                let palletsPiso = [];

                // Llenado de Piso primero
                while (x + 1.2 <= this.camion.L - 0.2) {
                    y = 0;
                    while (y + 1.0 <= this.camion.W) {
                        let p = this.crearPallet(id++);
                        p.x = x; p.y = y; p.z = 0;
                        p.lado = y < (this.camion.W / 2) ? 'Izquierda' : 'Derecha';
                        
                        this.carga.push(p);
                        palletsPiso.push(p);
                        this.actualizarMetricas(p);
                        
                        y += 1.05; // Espaciado entre pallets en ancho
                    }
                    x += 1.25; // Espaciado en largo
                }

                // Fase de Apilamiento para llegar al 80-85%
                for (let base of palletsPiso) {
                    if (this.volumenActual / this.volTotalCamion >= 0.85) break;

                    let p = this.crearPallet(id++);
                    if (this.esCompatible(base, p) && (this.metricas.peso + p.peso < this.camion.max_peso)) {
                        p.x = base.x; p.y = base.y; p.z = base.alto;
                        p.lado = base.lado;
                        p.apiladoSobre = base.id;
                        this.carga.push(p);
                        this.actualizarMetricas(p);
                    }
                }
                return { carga: this.carga, metricas: this.metricas };
            }

            crearPallet(id) {
                const tipo = Math.random() > 0.3 ? 'Alimento' : 'Contaminante';
                const alto = 1.4; 
                return {
                    id: "PLT-" + id,
                    tipo: tipo,
                    peso: 450 + Math.floor(Math.random() * 500),
                    cajas: 30 + Math.floor(Math.random() * 20),
                    dimX: 1.2, dimY: 1.0, alto: alto,
                    volumen: 1.2 * 1.0 * alto
                };
            }

            actualizarMetricas(p) {
                this.metricas.peso += p.peso;
                this.metricas.cajas += p.cajas;
                this.metricas.palletsCount++;
                this.volumenActual += p.volumen;
            }
        }

        // --- MOTOR 3D (THREE.JS) ---
        let scene, camera, renderer, controls, truckGroup, cargoGroup, palletMeshes = [];
        let ULTIMO_PLAN_CARGA = null;

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a1a);
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(20, 15, 20);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            const sun = new THREE.DirectionalLight(0xffffff, 0.8);
            sun.position.set(10, 20, 10);
            scene.add(sun);

            truckGroup = new THREE.Group();
            cargoGroup = new THREE.Group();
            scene.add(truckGroup);
            scene.add(cargoGroup);

            window.addEventListener('mousemove', onMouseMove);
            animate();
        }

        function dibujarCamion(camion) {
            while(truckGroup.children.length > 0) truckGroup.remove(truckGroup.children[0]);
            
            // Piso y Estructura
            const floorGeo = new THREE.BoxGeometry(camion.L, 0.1, camion.W);
            const floorMat = new THREE.MeshLambertMaterial({ color: 0x333333 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.position.set(camion.L/2, -0.05, camion.W/2);
            truckGroup.add(floor);

            // Wireframe del contenedor
            const wireGeo = new THREE.BoxGeometry(camion.L, camion.H, camion.W);
            const wireEdges = new THREE.EdgesGeometry(wireGeo);
            const wireMat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.2 });
            const wireframe = new THREE.LineSegments(wireEdges, wireMat);
            wireframe.position.set(camion.L/2, camion.H/2, camion.W/2);
            truckGroup.add(wireframe);

            controls.target.set(camion.L/2, 0, camion.W/2);
            crearEtiquetas(camion);
        }

        function dibujarCarga(carga, metricas, camion) {
            while(cargoGroup.children.length > 0) cargoGroup.remove(cargoGroup.children[0]);
            palletMeshes = [];
            
            let momX = 0, momY = 0;

            carga.forEach(p => {
                const color = p.tipo === 'Alimento' ? 0xff8f00 : 0x7b1fa2;
                const geo = new THREE.BoxGeometry(p.dimX * 0.95, p.alto * 0.98, p.dimY * 0.95);
                const mat = new THREE.MeshLambertMaterial({ color: color });
                const mesh = new THREE.Mesh(geo, mat);
                
                mesh.position.set(p.x + p.dimX/2, p.z + p.alto/2, p.y + p.dimY/2);
                mesh.userData = p;
                
                // Bordes
                const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({color: 0x000000, opacity: 0.3, transparent:true}));
                mesh.add(edges);

                cargoGroup.add(mesh);
                palletMeshes.push(mesh);

                momX += (p.x + p.dimX/2) * p.peso;
                momY += (p.y + p.dimY/2) * p.peso;
            });

            const cogX = momX / metricas.peso;
            const cogY = momY / metricas.peso;
            actualizarUI(metricas, cogX, cogY, camion);
        }

        function actualizarUI(metricas, cogX, cogY, camion) {
            document.getElementById('lbl-pallets').innerText = metricas.palletsCount;
            document.getElementById('lbl-peso').innerText = metricas.peso.toLocaleString() + " kg / " + camion.max_peso;
            
            const volOcupado = (metricas.palletsCount * (1.2*1.0*1.4)) / (camion.L * camion.W * camion.H);
            const volPerc = (volOcupado * 100).toFixed(1);
            const lblVol = document.getElementById('lbl-vol');
            lblVol.innerText = volPerc + "%";
            lblVol.className = (volPerc >= 80) ? "kpi-val status-ok" : "kpi-val status-warn";

            const diffY = Math.abs(cogY - (camion.W / 2));
            const lblEst = document.getElementById('lbl-estabilidad');
            if (diffY < (camion.W * 0.1)) {
                lblEst.innerText = "ESTABLE"; lblEst.className = "kpi-val status-ok";
            } else {
                lblEst.innerText = "DESBALANCE"; lblEst.className = "kpi-val status-err";
            }

            const lblCajas = document.getElementById('lbl-estado-cajas');
            if(metricas.cajas >= camion.min_cajas) {
                lblCajas.innerText = "META OK (" + metricas.cajas + ")"; lblCajas.className = "kpi-val status-ok";
            } else {
                lblCajas.innerText = "FALTAN " + (camion.min_cajas - metricas.cajas); lblCajas.className = "kpi-val status-warn";
            }
        }

        function ejecutarSimulacion() {
            const camionId = document.getElementById('sel-camion').value;
            const camion = FLOTA[camionId];
            const opt = new OptimizadorCarga(camionId);
            const res = opt.ejecutar();
            ULTIMO_PLAN_CARGA = res.carga;
            dibujarCamion(camion);
            dibujarCarga(res.carga, res.metricas, camion);
        }

        function onMouseMove(event) {
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(palletMeshes);

            const t = document.getElementById('tooltip');
            if (intersects.length > 0) {
                const data = intersects[0].object.userData;
                t.style.display = 'block';
                t.style.left = event.clientX + 15 + 'px';
                t.style.top = event.clientY + 15 + 'px';
                t.innerHTML = `<strong>${data.id}</strong><br>Tipo: ${data.tipo}<br>Peso: ${data.peso}kg<br>Z: ${data.z.toFixed(2)}m`;
            } else {
                t.style.display = 'none';
            }
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            updateLabels();
            renderer.render(scene, camera);
        }

        // --- EXPORTACIÓN ---
        function descargarExcel() {
            const data = ULTIMO_PLAN_CARGA.map(p => ({
                ID: p.id, Tipo: p.tipo, Peso_kg: p.peso, Cajas: p.cajas, 
                Pos_Largo: p.x.toFixed(2), Nivel: p.z === 0 ? "Piso" : "Apilado", 
                Lado: p.lado
            }));
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Estiba");
            XLSX.writeFile(wb, "Manifiesto_Walmart.xlsx");
        }

        async function descargarPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.text("Reporte de Estiba Logística", 10, 10);
            const rows = ULTIMO_PLAN_CARGA.map(p => [p.id, p.tipo, p.peso + "kg", p.lado, p.z === 0 ? "Piso" : "Nivel 2"]);
            doc.autoTable({ head: [['ID', 'Tipo', 'Peso', 'Lado', 'Nivel']], body: rows, startY: 20 });
            doc.save("Reporte_Estiba.pdf");
        }

        // --- ETIQUETAS Y AUXILIARES ---
        let labels = [];
        function crearEtiquetas(camion) {
            const container = document.getElementById('labels-container');
            container.innerHTML = ''; labels = [];
            const add = (txt, x, y, z) => {
                const div = document.createElement('div');
                div.className = 'label-3d'; div.innerText = txt;
                container.appendChild(div);
                labels.push({ elem: div, pos: new THREE.Vector3(x, y, z) });
            };
            add("CABINA", 0, 2, camion.W/2);
            add("PUERTA", camion.L, 2, camion.W/2);
        }

        function updateLabels() {
            labels.forEach(l => {
                const v = l.pos.clone().project(camera);
                if(v.z < 1) {
                    l.elem.style.display = 'block';
                    l.elem.style.left = (v.x * .5 + .5) * window.innerWidth + 'px';
                    l.elem.style.top = (-(v.y * .5) + .5) * window.innerHeight + 'px';
                } else { l.elem.style.display = 'none'; }
            });
        }

        function poblarSelectores() {
            const sel = document.getElementById('sel-camion');
            for(let key in FLOTA) {
                let opt = document.createElement('option');
                opt.value = key; opt.innerText = FLOTA[key].desc;
                sel.appendChild(opt);
            }
        }

        window.onload = () => { poblarSelectores(); init3D(); ejecutarSimulacion(); };
    </script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
