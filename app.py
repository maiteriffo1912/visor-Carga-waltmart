import streamlit as st
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="Visor Carga Walmart")

st.title("🚛 Visor de Carga 3D - Walmart")
st.markdown("Visualización de distribución de pallets (Visualización Dividida: Izquierda/Derecha).")

# --- CÓDIGO HTML/JS INTEGRADO ---
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Visor 3D Walmart</title>
    <style>
        body { margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f6; }
        #canvas-container { width: 100%; height: 600px; background: #e0e0e0; border-radius: 8px; overflow: hidden; position: relative; }
        
        /* Panel de métricas estilo Dashboard */
        .ui-panel { 
            margin-top: 15px; padding: 15px; background: white; border-radius: 8px; 
            display: flex; flex-wrap: wrap; gap: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }
        .kpi-box { 
            flex: 1; min-width: 140px; text-align: center; border-right: 1px solid #eee; 
        }
        .kpi-box:last-child { border-right: none; }
        .kpi-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
        .kpi-val { font-size: 20px; color: #333; font-weight: 700; }
        
        .status-ok { color: #2e7d32; }
        .status-warn { color: #f57c00; }
        .status-err { color: #c62828; }

        .controls { margin: 10px 0; padding: 10px; background: #fff; border-radius: 8px; }
        select { padding: 8px; border-radius: 4px; border: 1px solid #ccc; width: 200px; }
    </style>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

    <div class="controls">
        <label style="font-weight:bold; margin-right:10px;">Configuración de Camión:</label>
        <select id="sel-camion" onchange="ejecutarSimulacion()">
            <option value="camion_grande">Rampla 48ft (Grande)</option>
            <option value="camion_medio">Camión 3/4 (Medio)</option>
        </select>
    </div>

    <div id="canvas-container"></div>

    <div class="ui-panel">
        <div class="kpi-box"><div class="kpi-title">Pallets Cargados</div><div id="lbl-pallets" class="kpi-val">0</div></div>
        <div class="kpi-box"><div class="kpi-title">Peso Total</div><div id="lbl-peso" class="kpi-val">0 kg</div></div>
        <div class="kpi-box"><div class="kpi-title">Ocupación Vol.</div><div id="lbl-vol" class="kpi-val">0%</div></div>
        <div class="kpi-box"><div class="kpi-title">Estabilidad</div><div id="lbl-estabilidad" class="kpi-val">-</div></div>
        <div class="kpi-box"><div class="kpi-title">Estado Meta</div><div id="lbl-estado-cajas" class="kpi-val">-</div></div>
    </div>
    <div class="ui-panel">
        <div class="kpi-box"><div class="kpi-title">Meta Cajas</div><div id="lbl-meta-cajas" class="kpi-val">0</div></div>
        <div class="kpi-box"><div class="kpi-title">Cajas Actuales</div><div id="lbl-cajas-actuales" class="kpi-val">0</div></div>
        <div class="kpi-box"><div class="kpi-title">CoG X (Largo)</div><div id="lbl-cog-x" class="kpi-val">0 m</div></div>
        <div class="kpi-box"><div class="kpi-title">CoG Y (Ancho)</div><div id="lbl-cog-y" class="kpi-val">0 m</div></div>
    </div>

    <script>
        // --- VARIABLES GLOBALES ---
        let scene, camera, renderer, controls;
        let cargoGroup, truckGroup; 
        let palletMeshes = [];

        // Datos de Flota (Dimensiones internas en metros)
        const FLOTA = {
            'camion_grande': { L: 13.5, W: 2.5, H: 2.7, min_cajas: 1500 },
            'camion_medio': { L: 8.0, W: 2.4, H: 2.5, min_cajas: 800 }
        };

        // --- CLASE SIMULADA DEL OPTIMIZADOR ---
        class OptimizadorCarga {
            constructor(tipoCamion) {
                this.camion = FLOTA[tipoCamion];
            }

            ejecutar() {
                const carga = [];
                let pesoTotal = 0;
                let cajasTotal = 0;
                let numPallets = 0;

                // Llenamos el camión al 80% como ejemplo
                const filas = Math.floor((this.camion.L * 0.8) / 1.3); 

                for (let i = 0; i < filas; i++) {
                    // Creador de fila "2x1.2m"
                    carga.push({
                        x: this.camion.W / 2,      // Centrado en el ancho
                        y: 0,                      // En el piso
                        z: 1.0 + (i * 1.3),        // Avanzando en profundidad
                        dimX: 2.0,                 // Ancho total (2 pallets)
                        dimY: 1.4,                 // Altura estándar
                        dimZ: 1.2,                 // Profundidad estándar
                        peso: 850                  // Peso de la fila
                    });
                    pesoTotal += 850;
                    cajasTotal += 60; // 30 cajas x 2
                    numPallets += 2;
                }

                const metricas = {
                    peso: pesoTotal,
                    cajas: cajasTotal,
                    palletsCount: numPallets,
                    cogX: (this.camion.L * 0.8) / 2, // Aproximado
                    cogY: this.camion.W / 2
                };

                return { carga, metricas };
            }
        }

        // --- INICIALIZACIÓN 3D ---
        function init3D() {
            const container = document.getElementById('canvas-container');
            
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f2f6);

            // Cámara ajustada para ver todo el camión
            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
            camera.position.set(15, 12, 15);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;

            // Iluminación
            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
            dirLight.position.set(5, 10, 7);
            scene.add(dirLight);

            // Grupos
            truckGroup = new THREE.Group();
            cargoGroup = new THREE.Group();
            scene.add(truckGroup);
            scene.add(cargoGroup);

            // Grid de suelo
            const grid = new THREE.GridHelper(30, 30, 0xcccccc, 0xe5e5e5);
            scene.add(grid);

            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        // --- DIBUJAR CAMIÓN (Esqueleto) ---
        function dibujarCamion(camion) {
            while(truckGroup.children.length > 0) truckGroup.remove(truckGroup.children[0]); 

            // Piso
            const floor = new THREE.Mesh(
                new THREE.PlaneGeometry(camion.L, camion.W),
                new THREE.MeshBasicMaterial({ color: 0xbbbbbb, side: THREE.DoubleSide })
            );
            floor.rotation.x = -Math.PI / 2;
            floor.position.set(camion.L / 2, 0, camion.W / 2);
            truckGroup.add(floor);

            // Marco de Alambre
            const boxGeo = new THREE.BoxGeometry(camion.L, camion.H, camion.W);
            const edges = new THREE.LineSegments(
                new THREE.EdgesGeometry(boxGeo),
                new THREE.LineBasicMaterial({ color: 0x333333 })
            );
            edges.position.set(camion.L / 2, camion.H / 2, camion.W / 2);
            truckGroup.add(edges);
        }

        // --- DIBUJAR CARGA (MODIFICADO: 2 PALLETS) ---
        function dibujarCarga(listaCarga, metricas, camion) {
            // Limpiar anterior
            while(cargoGroup.children.length > 0) cargoGroup.remove(cargoGroup.children[0]);
            palletMeshes = [];

            let momentoX = 0;
            let momentoY = 0;

            const matPallet = new THREE.MeshLambertMaterial({ color: 0xffcc00 }); // Amarillo Walmart
            const matBorde = new THREE.LineBasicMaterial({ color: 0x000000 });   // Borde Negro

            listaCarga.forEach(p => {
                // Lógica modificada: Si el ancho es >= 1.9 (es decir, aprox 2m), dibujamos 2 pallets
                
                if (p.dimX >= 1.9) { 
                    // === PALLET IZQUIERDO ===
                    const geoIzq = new THREE.BoxGeometry(1.0, p.dimY, p.dimZ);
                    const meshIzq = new THREE.Mesh(geoIzq, matPallet);
                    // Movemos 0.5m a la izquierda del centro original
                    meshIzq.position.set(p.x - 0.5, p.y + p.dimY/2, p.z);
                    
                    // Borde Negro
                    const bordeIzq = new THREE.LineSegments(new THREE.EdgesGeometry(geoIzq), matBorde);
                    meshIzq.add(bordeIzq);
                    
                    cargoGroup.add(meshIzq);
                    palletMeshes.push(meshIzq);

                    // === PALLET DERECHO ===
                    const geoDer = new THREE.BoxGeometry(1.0, p.dimY, p.dimZ);
                    const meshDer = new THREE.Mesh(geoDer, matPallet);
                    // Movemos 0.5m a la derecha del centro original
                    meshDer.position.set(p.x + 0.5, p.y + p.dimY/2, p.z);
                    
                    // Borde Negro
                    const bordeDer = new THREE.LineSegments(new THREE.EdgesGeometry(geoDer), matBorde);
                    meshDer.add(bordeDer);
                    
                    cargoGroup.add(meshDer);
                    palletMeshes.push(meshDer);

                } else {
                    // Si es un pallet solo (impar o especial), dibujamos normal
                    const geometry = new THREE.BoxGeometry(p.dimX, p.dimY, p.dimZ);
                    const mesh = new THREE.Mesh(geometry, matPallet);
                    mesh.position.set(p.x, p.y + p.dimY / 2, p.z);
                    
                    const borde = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), matBorde);
                    mesh.add(borde);

                    cargoGroup.add(mesh);
                    palletMeshes.push(mesh);
                }

                // Cálculo físico
                momentoX += (p.x + p.dimX/2) * p.peso; 
                momentoY += (p.y + p.dimY/2) * p.peso;
            });

            // Dibujar Centro de Gravedad (CoG)
            if (metricas.peso > 0) {
                // Esfera Verde
                const cogMesh = new THREE.Mesh(
                    new THREE.SphereGeometry(0.2, 16, 16),
                    new THREE.MeshBasicMaterial({ color: 0x00ff00 })
                );
                cogMesh.position.set(metricas.cogX, camion.H + 0.2, metricas.cogY);
                cargoGroup.add(cogMesh);

                // Línea guía hacia abajo
                const points = [
                    new THREE.Vector3(metricas.cogX, camion.H + 0.2, metricas.cogY), 
                    new THREE.Vector3(metricas.cogX, 0, metricas.cogY)
                ];
                const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ color: 0x00ff00 }));
                cargoGroup.add(line);
            }
            
            // Actualizar textos en pantalla
            actualizarUI(metricas, metricas.cogX, metricas.cogY, camion);
        }

        // --- ACTUALIZAR INTERFAZ (KPIs) ---
        function actualizarUI(metricas, cogX, cogY, camion) {
            document.getElementById('lbl-pallets').innerText = metricas.palletsCount;
            document.getElementById('lbl-peso').innerText = metricas.peso.toLocaleString('es-CL') + ' kg';
            
            // Volumen
            const volCarga = metricas.palletsCount * 1.2 * 1.0 * 1.4; 
            const volCamion = camion.L * camion.W * camion.H;
            document.getElementById('lbl-vol').innerText = ((volCarga/volCamion)*100).toFixed(1) + '%';
            
            document.getElementById('lbl-cog-x').innerText = cogX.toFixed(2) + ' m';
            document.getElementById('lbl-cog-y').innerText = cogY.toFixed(2) + ' m';

            // Estabilidad
            const diffY = Math.abs(cogY - (camion.W / 2));
            const lblEst = document.getElementById('lbl-estabilidad');
            
            if(metricas.peso > 0 && diffY < (camion.W * 0.15)) {
                lblEst.innerText = "ESTABLE"; lblEst.className = "kpi-val status-ok";
            } else if (metricas.peso === 0) {
                lblEst.innerText = "-"; lblEst.className = "kpi-val";
            } else {
                lblEst.innerText = "DESBALANCEADO"; lblEst.className = "kpi-val status-err";
            }

            // Metas
            document.getElementById('lbl-meta-cajas').innerText = camion.min_cajas;
            document.getElementById('lbl-cajas-actuales').innerText = metricas.cajas;
            const lblEstado = document.getElementById('lbl-estado-cajas');
            
            if(metricas.cajas >= camion.min_cajas) {
                lblEstado.innerText = "META CUMPLIDA"; lblEstado.className = "kpi-val status-ok";
            } else {
                lblEstado.innerText = "FALTA: " + (camion.min_cajas - metricas.cajas); 
                lblEstado.className = "kpi-val status-warn";
            }
        }

        // --- EJECUCIÓN PRINCIPAL ---
        function ejecutarSimulacion() {
            const sel = document.getElementById('sel-camion');
            const camionId = sel.value;
            const camion = FLOTA[camionId];

            dibujarCamion(camion);

            // Instanciar tu optimizador (o el simulado)
            const optimizador = new OptimizadorCarga(camionId);
            const resultado = optimizador.ejecutar();

            dibujarCarga(resultado.carga, resultado.metricas, camion);
        }

        // Arranque
        window.onload = function() {
            init3D();
            ejecutarSimulacion();
        }
    </script>
</body>
</html>
"""

# Renderizar el HTML en Streamlit
components.html(html_code, height=850, scrolling=True)
