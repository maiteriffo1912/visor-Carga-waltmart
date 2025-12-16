import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Gemelo Digital - Optimización de Estiba Walmart",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar elementos propios de Streamlit para dar más espacio al visor
st.markdown("""
    <style>
        .block-container { padding: 0 !important; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# Código HTML/JS/CSS completo del Gemelo Digital
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemelo Digital - Optimización de Estiba Walmart</title>
    <style>
        body { margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; color: white; }
        
        /* Panel Izquierdo */
        #info-panel {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 320px;
            max-height: 95vh;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.9);
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #007dc6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            pointer-events: auto;
            user-select: none;
            font-size: 13px;
            z-index: 10;
        }

        /* Panel Derecho (Controles) */
        #controls-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 250px;
            background: rgba(0, 0, 0, 0.9);
            padding: 15px;
            border-radius: 8px;
            border-right: 5px solid #ffc220;
            z-index: 10;
        }

        h1 { margin: 0 0 10px 0; font-size: 16px; color: #ffc220; text-transform: uppercase; letter-spacing: 1px; }
        h2 { margin: 15px 0 5px 0; font-size: 13px; border-bottom: 1px solid #444; padding-bottom: 2px; color: #ddd; }
        
        .kpi-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
        .kpi-val { font-family: monospace; font-weight: bold; }
        
        .status-ok { color: #4caf50; }
        .status-warn { color: #ff9800; }
        .status-err { color: #f44336; }

        label { display: block; margin-top: 10px; color: #aaa; font-size: 11px; }
        select, button, input[type="file"] { width: 100%; padding: 8px; margin-top: 5px; background: #333; color: white; border: 1px solid #555; border-radius: 4px; }
        input[type="file"] { font-size: 11px; cursor: pointer; }
        
        button { background: #007dc6; cursor: pointer; font-weight: bold; border: none; margin-top: 15px; }
        button:hover { background: #005c91; }
        button.secondary { background: #555; margin-top: 5px; }
        button.secondary:hover { background: #777; }
        
        button.excel-btn { background: #1D6F42; margin-top: 10px; }
        button.excel-btn:hover { background: #145231; }

        button.pdf-btn { background: #D32F2F; margin-top: 5px; }
        button.pdf-btn:hover { background: #B71C1C; }

        /* Leyenda */
        .legend-item { display: flex; align-items: center; margin-top: 4px; font-size: 11px; }
        .color-box { width: 12px; height: 12px; margin-right: 8px; border: 1px solid #fff; }

        /* Tooltip Flotante para Detalles del Pallet */
        #tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid #ffc220;
            padding: 10px;
            border-radius: 4px;
            color: #fff;
            font-size: 12px;
            pointer-events: none; /* El mouse lo atraviesa */
            display: none;
            z-index: 100;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            min-width: 160px;
        }
        #tooltip strong { color: #ffc220; display: block; margin-bottom: 5px; font-size: 13px; border-bottom: 1px solid #555; padding-bottom: 2px; }
        .tooltip-row { display: flex; justify-content: space-between; margin-bottom: 2px; }

        /* Modal Tabla Manifiesto */
        #modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        #modal-content {
            background: #222;
            width: 80%;
            max-width: 900px;
            max-height: 80vh;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            border: 1px solid #444;
        }
        .modal-header {
            padding: 15px 20px;
            background: #333;
            border-bottom: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px 8px 0 0;
        }
        .modal-header h3 { margin: 0; color: #ffc220; }
        .close-btn { background: none; border: none; color: #aaa; font-size: 20px; cursor: pointer; width: auto; padding: 0; margin: 0; }
        .close-btn:hover { color: white; }
        
        .modal-body {
            padding: 20px;
            overflow-y: auto;
        }
        
        /* Tabla de Datos */
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #333; }
        th { background-color: #2a2a2a; color: #007dc6; position: sticky; top: 0; }
        tr:hover { background-color: #2c2c2c; }
        .cell-id { font-weight: bold; color: #fff; }
        .cell-apilado { color: #ff9800; font-weight: bold; }
        .cell-piso { color: #4caf50; }
        .cell-lado-izq { color: #2196f3; font-weight: bold; }
        .cell-lado-der { color: #e91e63; font-weight: bold; }

        /* Toast de Alerta */
        #toast {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            padding: 10px 20px;
            border-radius: 20px;
            display: none;
            font-weight: bold;
            z-index: 100;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }

        /* Etiquetas 3D flotantes */
        .label-3d {
            position: absolute;
            color: #fff;
            background: rgba(0,0,0,0.6);
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 10px;
            pointer-events: none;
            border: 1px solid #ffc220;
        }
    </style>
    <!-- Librerías 3D -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <!-- Librería Excel (SheetJS) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <!-- Librerías PDF (jsPDF) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.29/jspdf.plugin.autotable.min.js"></script>
</head>
<body>

    <!-- Tooltip (Etiqueta Flotante) -->
    <div id="tooltip"></div>

    <!-- Etiquetas de Orientación (inyectadas por JS) -->
    <div id="labels-container"></div>

    <!-- Modal Manifiesto -->
    <div id="modal-overlay">
        <div id="modal-content">
            <div class="modal-header">
                <h3>Orden de Carga (Cabina a Puerta)</h3>
                <button class="close-btn" onclick="cerrarTabla()">×</button>
            </div>
            <div class="modal-body">
                <table id="tabla-manifiesto">
                    <thead>
                        <tr>
                            <th>Secuencia</th>
                            <th>Lado / Ubicación</th>
                            <th>ID Pallet</th>
                            <th>Tipo</th>
                            <th>Peso (kg)</th>
                            <th>Cajas</th>
                            <th>Distancia Cabina</th>
                            <th>Posición</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- JS llenará esto -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Panel de Datos -->
    <div id="info-panel">
        <h1>Optimización de Carga</h1>
        
        <div id="kpis-operativos">
            <h2>Holguras de Seguridad</h2>
            <div class="kpi-row"><span>Fondo (Cabina):</span> <span class="kpi-val status-ok">10 cm</span></div>
            <div class="kpi-row"><span>Lateral (x Lado):</span> <span class="kpi-val status-ok">5 cm</span></div>
            <div class="kpi-row"><span>Puerta (Trasera):</span> <span class="kpi-val status-ok">15 cm</span></div>
            <div class="kpi-row" style="margin-top:10px;"><span>Configuración:</span> <span class="kpi-val" style="color:#ffc220;">2 x 1.2m (Rotado)</span></div>
        </div>

        <div id="metrics-info">
            <h2>Métricas de Carga</h2>
            <div class="kpi-row"><span>Pallets Cargados:</span> <span id="lbl-pallets" class="kpi-val">0</span></div>
            <div class="kpi-row"><span>Peso Total:</span> <span id="lbl-peso" class="kpi-val">0 kg</span></div>
            <div class="kpi-row"><span>Ocupación Vol:</span> <span id="lbl-vol" class="kpi-val">0%</span></div>
            <div class="kpi-row"><span>Cajas Totales:</span> <span id="lbl-cajas-actuales" class="kpi-val">0</span></div>
            <div class="kpi-row"><span>Meta Cajas:</span> <span id="lbl-meta-cajas" class="kpi-val">-</span></div>
            <div class="kpi-row"><span>Estado Meta:</span> <span id="lbl-estado-cajas" class="kpi-val">-</span></div>
        </div>

        <div id="engineering-info">
            <h2>Ingeniería (CoG)</h2>
            <div class="kpi-row"><span>CoG X (Largo):</span> <span id="lbl-cog-x" class="kpi-val">0.00 m</span></div>
            <div class="kpi-row"><span>CoG Y (Ancho):</span> <span id="lbl-cog-y" class="kpi-val">0.00 m</span></div>
            <div class="kpi-row"><span>Estabilidad:</span> <span id="lbl-estabilidad" class="kpi-val">-</span></div>
        </div>
        
        <h2>Leyenda</h2>
        <div class="legend-item"><div class="color-box" style="background: #ff8f00;"></div>Alimento</div>
        <div class="legend-item"><div class="color-box" style="background: #7b1fa2;"></div>Contaminante (Químicos)</div>
        <div class="legend-item"><div class="color-box" style="background: rgba(255,0,0,0.5); border:1px solid red;"></div>Zonas Restringidas</div>
        <div class="legend-item" style="color:#00ff00; font-weight:bold;">⮕ Flujo de Carga (Cabina -> Puerta)</div>
    </div>

    <!-- Panel de Configuración -->
    <div id="controls-panel">
        <h1>Configuración</h1>
        
        <label>SUBIR MANIFIESTO (EXCEL)</label>
        <input type="file" id="input-excel" accept=".xlsx, .xls" />
        <div style="font-size:9px; color:#888; margin-bottom:10px;">Cols: ID, Fecha, Peso, Cajas, Tipo, Alto, PDQ, Apilable, Fragilidad</div>

        <label>TIPO DE CAMIÓN</label>
        <select id="sel-camion" onchange="ejecutarSimulacion()">
            <option value="CAM_01">Rampla 18 Pallets (9.5m)</option>
            <option value="CAM_02">Rampla 24 Pallets (12.3m)</option>
            <option value="CAM_03" selected>Rampla 26 Pallets (13.3m)</option>
            <option value="CAM_04">Rampla 28 Pallets (14.3m)</option>
        </select>

        <label>CONFERENTE ASIGNADO</label>
        <select id="sel-conferente">
            <!-- Se llena con JS -->
        </select>

        <label>ANDÉN DE CARGA</label>
        <select id="sel-anden">
            <!-- Se llena con JS -->
        </select>

        <button onclick="ejecutarSimulacion()">RECALCULAR ESTIBA</button>
        <button class="secondary" onclick="mostrarTabla()">VER TABLA DE CARGA</button>
        <button class="excel-btn" onclick="descargarExcel()">DESCARGAR MANIFIESTO (EXCEL)</button>
        <button class="pdf-btn" onclick="descargarPDF()">DESCARGAR LAYOUT (PDF)</button>
        
        <div style="margin-top: 15px; font-size: 10px; color: #888; border-top:1px solid #444; padding-top:10px;">
            <strong>Reglas Activas:</strong><br>
            • Llenado: Cabina ➡ Puerta<br>
            • Distribución: Pesado (80%) ➡ Liviano (20%)<br>
            • Prioridad: Llenar Piso Rampla<br>
            • Apilar: Solo si falta Meta Cajas<br>
        </div>
    </div>

    <div id="toast">Mensaje</div>

    <script>
        // ==============================================================================
        // 1. DATOS MAESTROS
        // ==============================================================================

        const FLOTA = {
            'CAM_01': { desc: 'Rampla 18 Pallets', L: 9.5, W: 2.5, H: 2.6, max_pallets: 18, min_cajas: 1450, peso_max: 22000 },
            'CAM_02': { desc: 'Rampla 24 Pallets', L: 12.3, W: 2.5, H: 2.6, max_pallets: 24, min_cajas: 1750, peso_max: 24000 },
            'CAM_03': { desc: 'Rampla 26 Pallets', L: 13.3, W: 2.5, H: 2.6, max_pallets: 26, min_cajas: 2200, peso_max: 26000 },
            'CAM_04': { desc: 'Rampla 28 Pallets', L: 14.3, W: 2.5, H: 2.6, max_pallets: 28, min_cajas: 2450, peso_max: 28000 }
        };

        const CSV_DATA_RAW = `
1112202501,2025-12-11,812,190,Contaminante,1.60,No,No,Baja
1312202502,2025-12-13,354,28,Contaminante,0.85,Sí,Sí,Media
1212202503,2025-12-12,894,191,Alimento,1.59,No,No,Alta
1112202504,2025-12-11,842,38,Alimento,1.33,No,No,Media
1312202505,2025-12-13,335,92,Alimento,0.78,Sí,Sí,Alta
1312202506,2025-12-13,974,170,Alimento,1.43,No,No,Alta
1112202507,2025-12-11,400,100,Alimento,0.80,Sí,Sí,Baja
1012202508,2025-12-10,450,120,Alimento,0.85,Sí,Sí,Baja
1012202509,2025-12-10,900,200,Alimento,1.60,No,No,Alta
1212202510,2025-12-12,380,50,Contaminante,0.90,Sí,Sí,Baja
1112202511,2025-12-11,410,60,Contaminante,0.85,Sí,Sí,Baja
1412202512,2025-12-14,950,180,Alimento,1.70,No,No,Media
1012202513,2025-12-10,320,40,Alimento,0.75,Sí,Sí,Baja
1012202514,2025-12-10,330,45,Alimento,0.75,Sí,Sí,Baja
1112202515,2025-12-11,800,150,Contaminante,1.50,No,No,Media
1212202516,2025-12-12,350,30,Contaminante,0.80,Sí,Sí,Media
1012202517,2025-12-10,920,190,Alimento,1.65,No,No,Alta
1112202518,2025-12-11,880,160,Alimento,1.55,No,No,Media
1312202519,2025-12-13,400,80,Alimento,0.90,Sí,Sí,Baja
1212202520,2025-12-12,420,85,Alimento,0.95,Sí,Sí,Baja
`.trim();

        function generarDatosDummy() {
            let pallets = [];
            const lineas = CSV_DATA_RAW.split('\\n');
            lineas.forEach(l => {
                const d = l.split(',');
                pallets.push({
                    id: d[0], fecha: new Date(d[1]), peso: parseFloat(d[2]), cajas: parseInt(d[3]),
                    tipo: d[4], alto: parseFloat(d[5]), pdq: d[6] === 'Sí', apilable: d[7] === 'Sí', fragilidad: d[8]
                });
            });
            for (let i = pallets.length; i < 70; i++) {
                const esPDQ = Math.random() > 0.6; 
                const tipo = Math.random() > 0.3 ? 'Alimento' : 'Contaminante';
                const fecha = new Date(2025, 11, 10 + Math.floor(Math.random() * 5));
                pallets.push({
                    id: `GEN_${i+1}`,
                    fecha: fecha,
                    peso: Math.floor(esPDQ ? 300 + Math.random()*200 : 700 + Math.random()*400),
                    cajas: Math.floor(20 + Math.random()*200),
                    tipo: tipo,
                    alto: parseFloat((esPDQ ? 0.7 + Math.random()*0.3 : 1.4 + Math.random()*0.4).toFixed(2)),
                    pdq: esPDQ,
                    apilable: esPDQ,
                    fragilidad: esPDQ ? 'Baja' : (Math.random() > 0.5 ? 'Alta' : 'Media')
                });
            }
            return pallets;
        }

        let STOCK_SHIPPING = generarDatosDummy();
        let ULTIMO_PLAN_CARGA = [];

        // ==============================================================================
        // 2. LÓGICA DE EXCEL REFORZADA
        // ==============================================================================
        
        document.getElementById('input-excel').addEventListener('change', handleFileSelect, false);

        function handleFileSelect(evt) {
            const file = evt.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, {type: 'array'});
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    const jsonData = XLSX.utils.sheet_to_json(worksheet);
                    if(jsonData.length === 0) { mostrarToast("Error: Archivo vacío", "#f44336"); return; }
                    procesarDatosExcel(jsonData);
                } catch (err) { console.error(err); mostrarToast("Error al leer Excel", "#f44336"); }
            };
            reader.readAsArrayBuffer(file);
        }

        function procesarDatosExcel(jsonData) {
            // Buscador flexible de columnas
            const findKey = (row, candidates) => {
                const keys = Object.keys(row);
                for (let c of candidates) {
                    // Match Exacto
                    let match = keys.find(k => k.trim().toLowerCase() === c.toLowerCase());
                    if (match) return match;
                    // Match Parcial (e.g. "Peso Bruto" contiene "peso")
                    match = keys.find(k => k.toLowerCase().includes(c.toLowerCase()));
                    if (match) return match;
                }
                return null;
            };

            const parseNumber = (val, defaultVal) => {
                if (val === undefined || val === null) return defaultVal;
                if (typeof val === 'number') return val;
                if (typeof val === 'string') {
                    // Limpiar: Quitar letras, dejar solo numeros, puntos, comas y signos.
                    // Ejemplo: "1.200,50 kg" -> "1200.50"
                    let clean = val.replace(/[^0-9.,-]/g, ''); 
                    // Si tiene coma y punto, asumimos formato miles/decimales estandar
                    if (clean.includes(',') && clean.includes('.')) {
                        clean = clean.replace(/\./g, '').replace(',', '.');
                    } else {
                        // Solo coma -> reemplazar por punto
                        clean = clean.replace(',', '.');
                    }
                    let num = parseFloat(clean);
                    return isNaN(num) ? defaultVal : num;
                }
                return defaultVal;
            };

            const nuevoStock = jsonData.map((row, index) => {
                
                // Columnas Clave
                let keyId = findKey(row, ['id', 'pallet', 'lpn', 'etiqueta']);
                let keyFecha = findKey(row, ['fecha', 'date', 'ingreso', 'vencimiento']);
                let keyPeso = findKey(row, ['peso', 'weight', 'kg', 'bruto']);
                let keyCajas = findKey(row, ['cajas', 'qty', 'cantidad', 'unidades']);
                let keyTipo = findKey(row, ['tipo', 'type', 'cat', 'familia']);
                let keyAlto = findKey(row, ['alto', 'height', 'altura']);
                let keyPDQ = findKey(row, ['pdq']);
                
                // Procesar Fecha
                let rawDate = keyFecha ? row[keyFecha] : null;
                let fechaObj = new Date();
                if (typeof rawDate === 'number') { fechaObj = new Date(Math.round((rawDate - 25569)*86400*1000)); }
                else if (rawDate) { fechaObj = new Date(rawDate); }
                if (isNaN(fechaObj.getTime())) fechaObj = new Date(); // Fallback hoy

                return {
                    id: keyId ? row[keyId] : `IMP_${index}`,
                    fecha: fechaObj,
                    peso: parseNumber(keyPeso ? row[keyPeso] : null, 500),
                    cajas: parseInt(parseNumber(keyCajas ? row[keyCajas] : null, 50)),
                    tipo: keyTipo ? row[keyTipo] : 'Alimento',
                    alto: parseNumber(keyAlto ? row[keyAlto] : null, 1.2),
                    pdq: keyPDQ ? (String(row[keyPDQ]).toLowerCase().includes('s') || row[keyPDQ]===true) : false,
                    // Si no viene info de apilable, asumimos true si es PDQ
                    apilable: true, 
                    fragilidad: 'Media'
                };
            });
            STOCK_SHIPPING = nuevoStock;
            mostrarToast(`Excel cargado: ${STOCK_SHIPPING.length} pallets. Pesos procesados.`, "#4caf50");
            ejecutarSimulacion(); 
        }

        // ==============================================================================
        // 3. LÓGICA DE OPTIMIZACIÓN
        // ==============================================================================

        class OptimizadorCarga {
            constructor(camionId) {
                this.camion = FLOTA[camionId];
                this.margenFondo = 0.10;  
                this.margenLateral = 0.05; 
                this.margenPuerta = 0.15; 
                this.pAnchoOcupado = 1.2; 
                this.pLargoOcupado = 1.0; 
            }

            ordenarPrioridad(pallets) {
                // Estrategia: Peso descendente para cargar lo más pesado adelante (80%) y liviano atrás (20%)
                return pallets.sort((a, b) => {
                     // Prioridad 1: Peso (Mayor a menor)
                    if (b.peso - a.peso !== 0) return b.peso - a.peso;
                    // Prioridad 2: Fecha (FIFO) - Solo en caso de empate de peso
                    if (a.fecha - b.fecha !== 0) return a.fecha - b.fecha; 
                    // Prioridad 3: PDQ
                    return (a.pdq === b.pdq) ? 0 : a.pdq ? -1 : 1; 
                });
            }

            esApilable(base, top) {
                if (!base.pdq) return false;
                if (base.fragilidad === 'Alta') return false;
                if (base.tipo !== top.tipo) return false; 
                if ((base.alto + top.alto) > (this.camion.H - 0.1)) return false; 
                if ((base.peso + top.peso) > 1800) return false;
                return true;
            }

            ejecutar() {
                let cola = [...STOCK_SHIPPING];
                cola = this.ordenarPrioridad(cola);

                let planCarga = [];
                let pesoTotal = 0;
                let cajasTotales = 0;
                
                let cursorX = this.margenFondo;
                let cursorY = this.margenLateral;
                let columna = 0; // 0=Izq, 1=Der
                let palletsCargadosIds = new Set();

                // FASE 1: LLENADO DE PISO COMPLETO (PRIORIDAD 1)
                let i = 0;
                while (i < cola.length) {
                    
                    let p = cola[i];
                    if (cursorX + this.pLargoOcupado + this.margenPuerta > this.camion.L) break;
                    if (pesoTotal + p.peso > this.camion.peso_max) break;

                    p.x = cursorX;
                    p.y = cursorY;
                    p.z = 0;
                    p.apiladoSobre = null;
                    p.dimX = this.pLargoOcupado;
                    p.dimY = this.pAnchoOcupado;
                    
                    // CORRECCIÓN LADO: INVERTIDO PARA COINCIDIR CON "CABINA ARRIBA"
                    p.lado = columna === 0 ? 'Derecha' : 'Izquierda';
                    
                    planCarga.push({...p});
                    palletsCargadosIds.add(i);
                    pesoTotal += p.peso;
                    cajasTotales += p.cajas;

                    // Avanzar intercalado: 
                    if (columna === 0) {
                        cursorY += this.pAnchoOcupado; 
                        columna = 1;
                    } else {
                        cursorY = this.margenLateral;
                        cursorX += this.pLargoOcupado;
                        columna = 0;
                    }
                    i++;
                }

                // FASE 2: APILAMIENTO JUST-IN-TIME (PRIORIDAD 2)
                if (cajasTotales < this.camion.min_cajas) {
                    let remanente = cola.filter((_, idx) => !palletsCargadosIds.has(idx));

                    for (let pisoPallet of planCarga) {
                        if (cajasTotales >= this.camion.min_cajas) break;
                        if (pisoPallet.z > 0) continue; 

                        let candidatoIdx = remanente.findIndex(cand => this.esApilable(pisoPallet, cand));
                        if (candidatoIdx !== -1) {
                            let topPallet = remanente[candidatoIdx];
                            if (pesoTotal + topPallet.peso > this.camion.peso_max) break;

                            topPallet.x = pisoPallet.x;
                            topPallet.y = pisoPallet.y;
                            topPallet.z = pisoPallet.alto; 
                            topPallet.apiladoSobre = pisoPallet.id;
                            topPallet.dimX = pisoPallet.dimX;
                            topPallet.dimY = pisoPallet.dimY;
                            topPallet.lado = pisoPallet.lado;

                            planCarga.push({...topPallet});
                            pesoTotal += topPallet.peso;
                            cajasTotales += topPallet.cajas;
                            remanente.splice(candidatoIdx, 1);
                        }
                    }
                }

                return {
                    carga: planCarga,
                    metricas: { peso: pesoTotal, cajas: cajasTotales, palletsCount: planCarga.length }
                };
            }
        }

        // ==============================================================================
        // 4. UI & VISUALIZACIÓN
        // ==============================================================================
        
        function generarTablaManifiesto(carga) {
            const tbody = document.querySelector('#tabla-manifiesto tbody');
            tbody.innerHTML = '';
            
            // Orden estricto para tabla: X (Fondo) -> Y (Lado) -> Z (Piso/Aire)
            const cargaOrdenada = [...carga].sort((a, b) => {
                if (Math.abs(a.x - b.x) > 0.1) return a.x - b.x; 
                // Ajuste visual orden tabla
                if (Math.abs(a.y - b.y) > 0.1) return a.y - b.y; 
                return a.z - b.z; 
            });
            
            cargaOrdenada.forEach((p, index) => {
                const tr = document.createElement('tr');
                let posTexto = p.apiladoSobre ? `<span class="cell-apilado">Apilado</span>` : '<span class="cell-piso">Piso</span>';
                let ladoClass = p.lado === 'Izquierda' ? 'cell-lado-izq' : 'cell-lado-der';
                let ladoIcono = p.lado === 'Izquierda' ? '⬅️' : '➡️';
                let distCabina = p.x.toFixed(2) + ' m';

                tr.innerHTML = `
                    <td style="color:#888;">${index + 1}</td>
                    <td class="${ladoClass}">${ladoIcono} ${p.lado}</td>
                    <td class="cell-id">${p.id}</td>
                    <td>${p.tipo}</td>
                    <td>${p.peso}</td>
                    <td>${p.cajas}</td>
                    <td style="font-family:monospace;">${distCabina}</td>
                    <td>${posTexto}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function mostrarTabla() { document.getElementById('modal-overlay').style.display = 'flex'; }
        function cerrarTabla() { document.getElementById('modal-overlay').style.display = 'none'; }
        function mostrarToast(msg, color) {
            const t = document.getElementById('toast');
            t.innerText = msg; t.style.display = 'block'; t.style.backgroundColor = color || '#333';
            setTimeout(() => t.style.display = 'none', 4000);
        }

        function poblarSelectores() {
            const selAnden = document.getElementById('sel-anden');
            for(let i=1; i<=118; i++) {
                let opt = document.createElement('option'); opt.value = i; opt.text = `Andén ${i}`; selAnden.add(opt);
            }
            const selConf = document.getElementById('sel-conferente');
            for(let i=1; i<=9; i++) {
                let opt = document.createElement('option'); opt.value = i; opt.text = `Conferente ${i}`; selConf.add(opt);
            }
        }

        // --- THREE.JS ---
        let scene, camera, renderer, controls;
        let truckGroup, cargoGroup;
        let raycaster, mouse;
        let palletMeshes = []; 

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x222222);

            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(-8, 15, 8); 

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(10, 20, 10);
            dirLight.castShadow = true;
            scene.add(dirLight);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            const gridHelper = new THREE.GridHelper(50, 50, 0x444444, 0x333333);
            scene.add(gridHelper);

            truckGroup = new THREE.Group();
            cargoGroup = new THREE.Group();
            scene.add(truckGroup);
            scene.add(cargoGroup);

            raycaster = new THREE.Raycaster();
            mouse = new THREE.Vector2();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
                updateLabels();
            });
            window.addEventListener('mousemove', onMouseMove, false);
            controls.addEventListener('change', updateLabels);
            animate();
        }

        function onMouseMove(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
            const tooltip = document.getElementById('tooltip');
            tooltip.style.left = event.clientX + 15 + 'px';
            tooltip.style.top = event.clientY + 15 + 'px';
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(palletMeshes);
            if (intersects.length > 0 && intersects[0].object.userData.id) {
                mostrarTooltip(intersects[0].object.userData);
                document.body.style.cursor = 'pointer';
            } else {
                ocultarTooltip();
                document.body.style.cursor = 'default';
            }
        }

        function mostrarTooltip(data) {
            const t = document.getElementById('tooltip');
            t.style.display = 'block';
            t.innerHTML = `
                <strong>ID: ${data.id}</strong>
                <div class="tooltip-row"><span>Tipo:</span> <span>${data.tipo}</span></div>
                <div class="tooltip-row"><span>Peso:</span> <span>${data.peso} kg</span></div>
                <div class="tooltip-row"><span>Cajas:</span> <span>${data.cajas}</span></div>
                <div class="tooltip-row"><span>PDQ:</span> <span>${data.pdq ? 'Sí' : 'No'}</span></div>
                <div class="tooltip-row" style="margin-top:2px; color:#ffc220;">${data.lado} | ${data.x.toFixed(2)}m</div>
            `;
        }
        function ocultarTooltip() { document.getElementById('tooltip').style.display = 'none'; }
        function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }

        function dibujarCamion(camion) {
            while(truckGroup.children.length > 0) truckGroup.remove(truckGroup.children[0]);

            // Piso
            const floor = new THREE.Mesh(new THREE.BoxGeometry(camion.L, 0.1, camion.W), new THREE.MeshLambertMaterial({ color: 0x333333 }));
            floor.position.set(camion.L/2, -0.05, camion.W/2);
            truckGroup.add(floor);

            // Holguras
            const matHolgura = new THREE.MeshBasicMaterial({ color: 0xff0000, opacity: 0.3, transparent: true, side: THREE.DoubleSide });
            
            // Cabina (Fondo)
            const hFondo = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.05, camion.W), matHolgura);
            hFondo.position.set(0.05, 0.03, camion.W/2);
            truckGroup.add(hFondo);
            
            // Puerta (Trasera)
            const hPuerta = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.05, camion.W), matHolgura);
            hPuerta.position.set(camion.L - 0.075, 0.03, camion.W/2);
            truckGroup.add(hPuerta);

            // Wireframe
            const wires = new THREE.LineSegments(
                new THREE.EdgesGeometry(new THREE.BoxGeometry(camion.L, camion.H, camion.W)),
                new THREE.LineBasicMaterial({ color: 0xffffff, opacity: 0.2, transparent: true })
            );
            wires.position.set(camion.L/2, camion.H/2, camion.W/2);
            truckGroup.add(wires);
            
            // Flecha de Dirección de Carga (Verde)
            // Origen: Cabina (0, 3, W/2) -> Dirección: X positivo
            const dir = new THREE.Vector3(1, 0, 0);
            const origin = new THREE.Vector3(0, camion.H + 0.5, camion.W/2);
            const length = camion.L;
            const hex = 0x00ff00;
            const arrowHelper = new THREE.ArrowHelper(dir, origin, length, hex, 0.5, 0.3);
            truckGroup.add(arrowHelper);

            controls.target.set(camion.L/2, 0, camion.W/2);
            crearEtiquetas(camion);
        }

        // Gestión de Etiquetas HTML sobre 3D
        let labels = [];
        function crearEtiquetas(camion) {
            const container = document.getElementById('labels-container');
            container.innerHTML = '';
            labels = [];

            function addLabel(text, x, y, z) {
                const div = document.createElement('div');
                div.className = 'label-3d';
                div.textContent = text;
                container.appendChild(div);
                labels.push({ elem: div, pos: new THREE.Vector3(x, y, z) });
            }

            addLabel("CABINA (FONDO)", 0, camion.H + 1, camion.W/2);
            addLabel("PUERTA (ATRÁS)", camion.L, camion.H + 1, camion.W/2);
            updateLabels();
        }

        function updateLabels() {
            labels.forEach(lbl => {
                const vector = lbl.pos.clone().project(camera);
                const x = (vector.x * .5 + .5) * window.innerWidth;
                const y = (-(vector.y * .5) + .5) * window.innerHeight;
                
                if(vector.z < 1) { // Si está delante de la cámara
                    lbl.elem.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
                    lbl.elem.style.display = 'block';
                } else {
                    lbl.elem.style.display = 'none';
                }
            });
        }

        function dibujarCarga(carga, metricas, camion) {
            while(cargoGroup.children.length > 0) cargoGroup.remove(cargoGroup.children[0]);
            palletMeshes = [];
            let momentoX = 0, momentoY = 0;

            carga.forEach(p => {
                let colorHex = p.tipo === 'Alimento' ? 0xff8f00 : 0x7b1fa2;
                const geo = new THREE.BoxGeometry(p.dimX * 0.98, p.alto, p.dimY * 0.98); 
                const mat = new THREE.MeshLambertMaterial({ color: colorHex });
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(p.x + p.dimX/2, p.z + p.alto/2, p.y + p.dimY/2);
                mesh.userData = { ...p };
                const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0x000000, opacity: 0.5, transparent: true }));
                mesh.add(edges);
                cargoGroup.add(mesh);
                palletMeshes.push(mesh);
                momentoX += (p.x + p.dimX/2) * p.peso;
                momentoY += (p.y + p.dimY/2) * p.peso;
            });

            if (metricas.peso > 0) {
                const cogX = momentoX / metricas.peso;
                const cogY = momentoY / metricas.peso;
                actualizarUI(metricas, cogX, cogY, camion);
                
                // Visualización de CoG (Punto Verde)
                const cogMesh = new THREE.Mesh(
                    new THREE.SphereGeometry(0.3, 16, 16),
                    new THREE.MeshBasicMaterial({ color: 0x00ff00 })
                );
                cogMesh.position.set(cogX, camion.H + 0.5, cogY);
                cargoGroup.add(cogMesh);
                const line = new THREE.Line(
                    new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(cogX, camion.H + 0.5, cogY), new THREE.Vector3(cogX, 0, cogY)]),
                    new THREE.LineBasicMaterial({ color: 0x00ff00 })
                );
                cargoGroup.add(line);

            } else {
                actualizarUI({peso:0, cajas:0, palletsCount:0}, 0, 0, camion);
            }
        }

        function actualizarUI(metricas, cogX, cogY, camion) {
            document.getElementById('lbl-pallets').innerText = metricas.palletsCount;
            document.getElementById('lbl-peso').innerText = metricas.peso.toLocaleString('es-CL') + ' kg';
            
            const volCarga = metricas.palletsCount * 1.2 * 1.0 * 1.4; 
            const volCamion = camion.L * camion.W * camion.H;
            document.getElementById('lbl-vol').innerText = ((volCarga/volCamion)*100).toFixed(1) + '%';
            document.getElementById('lbl-cog-x').innerText = cogX.toFixed(2) + ' m';
            document.getElementById('lbl-cog-y').innerText = cogY.toFixed(2) + ' m';

            const diffY = Math.abs(cogY - (camion.W / 2));
            const lblEst = document.getElementById('lbl-estabilidad');
            if(metricas.peso > 0 && diffY < (camion.W * 0.1)) {
                lblEst.innerText = "ESTABLE"; lblEst.className = "kpi-val status-ok";
            } else if (metricas.peso === 0) {
                lblEst.innerText = "-"; lblEst.className = "kpi-val";
            } else {
                lblEst.innerText = "DESBALANCEADO"; lblEst.className = "kpi-val status-err";
            }

            document.getElementById('lbl-meta-cajas').innerText = camion.min_cajas;
            document.getElementById('lbl-cajas-actuales').innerText = metricas.cajas;
            
            const lblEstadoCajas = document.getElementById('lbl-estado-cajas');
            if(metricas.cajas >= camion.min_cajas) {
                lblEstadoCajas.innerText = "META CUMPLIDA"; lblEstadoCajas.className = "kpi-val status-ok";
                mostrarToast("Meta de cajas alcanzada. Carga detenida.", "#4caf50");
            } else {
                const faltan = camion.min_cajas - metricas.cajas;
                lblEstadoCajas.innerText = `FALTAN ${faltan}`; lblEstadoCajas.className = "kpi-val status-warn";
            }
        }

        function ejecutarSimulacion() {
            const camionId = document.getElementById('sel-camion').value;
            const camion = FLOTA[camionId];
            const optimizador = new OptimizadorCarga(camionId);
            const resultado = optimizador.ejecutar();
            ULTIMO_PLAN_CARGA = resultado.carga;
            dibujarCamion(camion);
            dibujarCarga(resultado.carga, resultado.metricas, camion);
            generarTablaManifiesto(resultado.carga);
        }

        function descargarExcel() {
            if (!ULTIMO_PLAN_CARGA || ULTIMO_PLAN_CARGA.length === 0) {
                mostrarToast("No hay datos para exportar", "#f44336");
                return;
            }

            // Ordenar datos igual que la tabla visual (Fondo -> Lado -> Altura)
            const dataExport = [...ULTIMO_PLAN_CARGA].sort((a, b) => {
                if (Math.abs(a.x - b.x) > 0.1) return a.x - b.x;
                if (Math.abs(a.y - b.y) > 0.1) return a.y - b.y;
                return a.z - b.z;
            }).map((p, i) => ({
                "Secuencia": i + 1,
                "Lado": p.lado,
                "ID Pallet": p.id,
                "Tipo": p.tipo,
                "Peso (kg)": p.peso,
                "Cajas": p.cajas,
                "Distancia Cabina (m)": p.x.toFixed(2),
                "Ubicación": p.apiladoSobre ? `Apilado sobre ${p.apiladoSobre}` : "Piso",
                "Fecha": p.fecha ? new Date(p.fecha).toLocaleDateString() : "-"
            }));

            const ws = XLSX.utils.json_to_sheet(dataExport);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Manifiesto Carga");
            
            // Generar nombre de archivo con fecha
            const fechaStr = new Date().toISOString().slice(0,10);
            XLSX.writeFile(wb, `Manifiesto_Carga_Walmart_${fechaStr}.xlsx`);
            mostrarToast("Excel descargado correctamente", "#4caf50");
        }

        async function descargarPDF() {
            if (!ULTIMO_PLAN_CARGA || ULTIMO_PLAN_CARGA.length === 0) {
                mostrarToast("No hay datos para generar PDF", "#f44336");
                return;
            }

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
            
            // Configuración
            const pageWidth = doc.internal.pageSize.getWidth();
            const pageHeight = doc.internal.pageSize.getHeight();
            const margin = 10;
            
            const camionId = document.getElementById('sel-camion').value;
            const camionInfo = FLOTA[camionId];
            
            // Título
            doc.setFontSize(16);
            doc.setTextColor(0, 125, 198); // Azul Walmart
            doc.text("Reporte de Estiba - Layout de Carga", margin, margin + 5);
            
            doc.setFontSize(10);
            doc.setTextColor(50, 50, 50);
            doc.text(`Camión: ${camionInfo.desc} | Fecha: ${new Date().toLocaleDateString()}`, margin, margin + 12);

            // ==========================================
            // DIBUJO DEL CAMIÓN (TOP VIEW)
            // ==========================================
            
            // Espacio disponible para el dibujo
            const drawAreaWidth = pageWidth - (margin * 2);
            const drawAreaHeight = 70; // Altura fija para el gráfico
            const startY = margin + 20;

            // Escala: Ajustar el largo del camión al ancho disponible
            // Usamos un factor de seguridad (0.9) para que no toque los bordes
            const scale = (drawAreaWidth / camionInfo.L) * 0.95;
            
            // Coordenadas base del dibujo (centrado horizontalmente)
            const truckDrawWidth = camionInfo.L * scale;
            const truckDrawHeight = camionInfo.W * scale;
            const startX = margin + (drawAreaWidth - truckDrawWidth) / 2;
            const truckY = startY + (drawAreaHeight - truckDrawHeight) / 2;

            // 1. Dibujar Contorno Camión
            doc.setDrawColor(50, 50, 50);
            doc.setLineWidth(0.5);
            doc.rect(startX, truckY, truckDrawWidth, truckDrawHeight); // Chasis
            
            // Cabina (Indicador visual a la izquierda)
            doc.setFillColor(200, 200, 200);
            doc.rect(startX - 5, truckY, 5, truckDrawHeight, 'F');
            doc.setFontSize(8);
            doc.setTextColor(0, 0, 0);
            doc.text("CAB", startX - 4, truckY + truckDrawHeight/2 + 1, { angle: 90, align: 'center' });

            // 2. Dibujar Pallets
            // Filtramos solo los que están en el piso (z=0) para el layout 2D, 
            // pero indicamos si hay apilados.
            const palletsPiso = ULTIMO_PLAN_CARGA.filter(p => p.z < 0.1);

            palletsPiso.forEach((p, i) => {
                // Coordenadas PDF
                // X en 3D = Largo Camión = X en PDF
                // Y en 3D = Ancho Camión = Y en PDF
                const pdfX = startX + (p.x * scale);
                // Invertimos Y visualmente si es necesario, pero como el origen 3D suele ser (0,0) en esquina, 
                // y PDF es top-left, solo sumamos.
                const pdfY = truckY + (p.y * scale);
                
                const w = p.dimX * scale;
                const h = p.dimY * scale;

                // Color según tipo
                if (p.tipo === 'Alimento') {
                    doc.setFillColor(255, 143, 0); // Naranja
                } else {
                    doc.setFillColor(123, 31, 162); // Violeta
                }
                
                doc.setDrawColor(255, 255, 255);
                doc.rect(pdfX, pdfY, w, h, 'FD'); // Fill and Draw border

                // Verificar si tiene carga encima
                const tieneApilado = ULTIMO_PLAN_CARGA.some(top => top.apiladoSobre === p.id);
                
                // Texto ID
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(7);
                // Si es muy pequeño, solo poner numero de secuencia
                // Buscamos el índice original en el plan completo para el número
                const indexReal = ULTIMO_PLAN_CARGA.findIndex(x => x.id === p.id) + 1;
                doc.text(`${indexReal}`, pdfX + w/2, pdfY + h/2 + 1, { align: 'center' });

                // Indicador de Apilado
                if (tieneApilado) {
                    doc.setTextColor(0, 0, 0);
                    doc.setFontSize(6);
                    doc.text("x2", pdfX + w - 2, pdfY + 3);
                }
            });

            // Leyenda Gráfico
            const legendY = startY + drawAreaHeight + 5;
            doc.setFontSize(8);
            doc.setTextColor(0,0,0);
            
            // Naranja
            doc.setFillColor(255, 143, 0);
            doc.rect(margin, legendY, 4, 4, 'F');
            doc.text("Alimento", margin + 5, legendY + 3);
            
            // Violeta
            doc.setFillColor(123, 31, 162);
            doc.rect(margin + 25, legendY, 4, 4, 'F');
            doc.text("Contaminante", margin + 30, legendY + 3);

            doc.text("* Números indican secuencia de carga. 'x2' indica pallet apilado.", margin + 60, legendY + 3);

            // ==========================================
            // TABLA DE DATOS
            // ==========================================
            
            // Preparar datos para autotable
            const tableData = ULTIMO_PLAN_CARGA.sort((a, b) => {
                 if (Math.abs(a.x - b.x) > 0.1) return a.x - b.x;
                 return a.z - b.z;
            }).map((p, i) => [
                i + 1,
                p.id,
                p.tipo,
                `${p.peso} kg`,
                p.cajas,
                p.lado,
                p.apiladoSobre ? 'Apilado' : 'Piso'
            ]);

            doc.autoTable({
                startY: legendY + 10,
                head: [['Sec', 'ID Pallet', 'Tipo', 'Peso', 'Cajas', 'Lado', 'Posición']],
                body: tableData,
                theme: 'grid',
                styles: { fontSize: 8, cellPadding: 2 },
                headStyles: { fillColor: [0, 125, 198] }
            });

            // Guardar
            const fechaStr = new Date().toISOString().slice(0,10);
            doc.save(`Layout_Carga_Walmart_${fechaStr}.pdf`);
            mostrarToast("PDF generado correctamente", "#4caf50");
        }

        window.onload = function() {
            poblarSelectores();
            init3D();
            ejecutarSimulacion();
        };

    </script>
</body>
</html>
"""

# Renderizar el HTML
components.html(html_code, height=900, scrolling=True)
